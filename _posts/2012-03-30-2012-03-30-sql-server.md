---
layout: post
title: "浅谈SQL Server中的快照"
date: 2012-03-30
categories: blog
tags: [博客园迁移]
---

### 简介

数据库快照，正如其名称所示那样，是数据库在某一时间点的视图。是SQL Server在2005之后的版本引入的特性。快照的应用场景比较多，但快照设计最开始的目的是为了报表服务。比如我需要出2011的资产负债表，这需要数据保持在2011年12月31日零点时的状态，则利用快照可以实现这一点。快照还可以和镜像结合来达到读写分离的目的。下面我们来看什么是快照。

### 什么是快照

数据库快照是 SQL Server 数据库（源数据库）的只读静态视图。换句话说，快照可以理解为一个只读的数据库。利用快照，可以提供如下好处:

  * 提供了一个静态的视图来为报表提供服务 
  * 可以利用数据库快照来恢复数据库，相比备份恢复来说，这个速度会大大提高\(在下面我会解释为什么\) 
  * 和数据库镜像结合使用，提供读写分离 
  * 作为测试环境或数据变更前的备份，比如我要大批导入或删除数据前，或是将数据提供给测试人员进行测试前，做一个快照，如果出现问题，则可以利用快照恢复到快照建立时的状态 



### 快照的原理

与备份数据库复制整个数据库不同，快照并不复制整个数据库的页，而是仅仅复制在快照建立时间点之后改变的页。因此，当利用快照进行数据库恢复时，也仅仅将那些做出改变的页恢复到源数据库，这个速度无疑会大大高于备份和恢复方式。这个原理如图1所示（图摘自SQL Server 2008揭秘）。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-30-sql-server/sql-server-20120330105405562.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203301054034697.png)

图1.镜像的原理

由图1可以看出，快照并不是复制整个整个数据库，而仅仅利用快照存储原始页。因此可以看出,源数据库上建立快照会给IO增加额外负担.当对快照数据库进行查询时，快照时间点之后更改的数据会查询数据文件，。这个概念如图2所示（图摘自SQL Server 2008揭秘）。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-30-sql-server/sql-server-201203301054136148.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203301054074758.png)

图2.查询快照数据库时查询的分布

### 写入时复制\(Copy On Writing\)和稀疏文件\(Sparse Flie\)

由上图中可以看出，快照数据库的文件是基于稀疏文件\(Sparse File\),稀疏文件是NTFS文件系统的一项特性。所谓的稀疏文件，是指文件中出现大量0的数据，这些数据对我们用处并不大，却一样占用着磁盘空间。因此NTFS对此进行了优化，利用算法将这个文件进行压缩。因此当稀疏文件被创建时，稀疏文件刚开始大小会很小\(甚至是空文件\)，比如图3所示的文件就是一个稀疏文件。虽然逻辑上占了21M，但文件实际上占了128KB磁盘空间。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-30-sql-server/sql-server-201203301054166375.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203301054142636.png)

图3.一个稀疏文件

对于快照来说，除了通过快照数据库文件的属性来看快照的大小之外，也可以通过DMV来查看，如图4所示.

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-30-sql-server/sql-server-201203301054197473.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/20120330105417113.png)

图4.通过DMV查看快照数据库大小

而当快照创建后，随着对源数据库的改变逐渐增多，稀疏文件也会慢慢增长,概念如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-30-sql-server/sql-server-201203301054229335.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203301054203404.gif)

图5.随着源数据库的更改越来越多，稀疏文件不断增长

所以，通常来说，当稀疏文件增长到源数据库文件大小的30%时，就应该考虑重建快照了。

而稀疏文件的写入是利用了微软的写入时复制技术（Copy-On-Writing）,意思是在复制一个对象时并不是真正把对象复制到另一个位置，而是在新的对象中映射一个指针，指向原对象的位置。这样当对新对象执行读操作时，直接指向原对象。而在对新的对象执行写操作时,将改变部分对象的指针指向到新的地址中。并修改映射表到新的位置中。

### 使用快照的限制

使用快照存在诸多限制，由于列表太长（详细请参考MSDN：<http://msdn.microsoft.com/zh-cn/library/ms175158.aspx#LimitationsRequirements>）,我只概括的说一下主要限制。

  * 当使用快照恢复数据库时，首先要删除其他快照 
  * 快照在创建时的时间点上没有commit的数据不会被记入快照 
  * 快照是快照整个数据库，而不是数据库的某一部分 
  * 快照是只读的，意思是不能在快照上加任何更改，即使是你想加一个让报表跑得更快的索引 
  * 在利用快照恢复数据库时，快照和源数据库都不可用 
  * 快照和源数据必须在同一个实例上 
  * 快照数据库的文件必须在NTFS格式的盘上 
  * 当磁盘不能满足快照的增长时，快照数据库会被置为suspect状态 
  * 快照上不能存在全文索引 



其实，虽然限制看上去很多，但只要明白快照的原理，自然能推测出快照应该有的限制。

### 快照的创建和使用

无论是使用SSMS或是命令行，快照只能通过T-SQL语句创建。在创建数据库之前，首先要知道数据库分布在几个文件上，因为快照需要对每一个文件进行copy-on-writing。如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-30-sql-server/sql-server-201203301054283069.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203301054244644.png)

图6.首先查出数据库的文件分布

根据图6的数据库分布，我们通过T-SQL创建快照,如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-30-sql-server/sql-server-201203301054408749.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203301054304889.png)

图7，根据图6的数据库信息创建一个数据库快照

当快照数据库创建成功后，就可以像使用普通数据库一样使用快照数据库了,如图8所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-30-sql-server/sql-server-20120330105444371.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203301054426109.png)

图8.快照数据库和普通数据库一样使用

通过如下语句可以看到，快照数据库文件和源数据库的文件貌似并无区别，仅仅是快照数据库文件是稀疏文件，如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-30-sql-server/sql-server-201203301054518740.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/20120330105445206.png)

图9.源数据库和快照数据库

而删除快照数据库和删除普通数据库并无二至，也仅仅是使用DROP语句，如图10所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-30-sql-server/sql-server-201203301054542313.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203301054521116.png)

图10.删除快照数据库

我们也可以利用快照恢复数据库，这个恢复速度要比普通的备份-恢复来的快得多,这也可以将数据库呈现给测试人员，当测试结束后，恢复数据库到测试之前的状态。如图11所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-30-sql-server/sql-server-201203301113401351.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/20120330105455753.png)

图11.利用快照恢复数据库

### 使用快照其他一些需要考虑的因素

1.快照数据库的安全设置继承源数据库的安全设置。也就是说能访问源数据库的用户或角色也能访问快照数据库，当然，因为快照数据库是只读的，所以无论任何角色或人都无法修改快照数据库。

2.我们由文章前面图5看出，随着快照存在的时间越来越长，快照会不断增长。所以推荐在快照达到源数据库大小30%之前，重新创建快照。

3.由于快照会拖累数据库性能，所以数据库不宜存在过多快照。

### 总结

本文简单讲述了数据库快照的概念，原理以及使用。数据库快照可以在很多场景下使用，无论是用于报表，还是和镜像配合提供负载，以及利用快照恢复数据库，使用得当的话，快照将会是一把利器。

**[本文示例代码猛击这里](https://files.cnblogs.com/CareySon/snapshot.rar)**
