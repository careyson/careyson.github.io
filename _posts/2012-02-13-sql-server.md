---
layout: post
title: "浅谈SQL Server中的事务日志(一)----事务日志的物理和逻辑构架"
date: 2012-02-13
categories: blog
tags: [博客园迁移]
---

### 简介

SQL Server中的事务日志无疑是SQL Server中最重要的部分之一。因为SQL SERVER利用事务日志来确保持久性\(Durability\)和事务回滚\(Rollback\)。从而还部分确保了事务的[ACID](http://www.cnblogs.com/CareySon/archive/2012/01/29/2331088.html)属性.在SQL Server崩溃时，DBA还可以通过事务日志将数据恢复到指定的时间点。当SQL Server运转良好时，多了解一些事务日志的原理和概念显得并不是那么重要。但是，一旦SQL SERVER发生崩溃时，了解事务日志的原理和概念对于快速做出正确的决策来恢复数据显得尤为重要.本系列文章将会从事务日志的概念，原理，SQL Server如何使用日志来确保持久性属性等方面来谈SQL Server的事务日志.

### 事务日志的物理组织构架

事务日志仅仅是记录与其对应数据库上的事务行为和对数据库修改的日志文件.在你新建数据库时，伴随着数据库文件，会有一个默认以ldf为扩展名的事务日志文件. 当然，一个数据库也可以配有多个日志文件，但是在逻辑上，他们可以看成一个.

在SQL Server对于日志文件的管理，是将逻辑上一个ldf文件划分成多个逻辑上的虚拟日志文件\(virtual log files,简称VLFs\).以便于管理。用个类比方法来看，日志文件\(ldf\)好比一趟火车，每一节车厢都是一个虚拟日志文件\(VLFs\):

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-13-sql-server/sql-server-20120213172032510.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202131720319506.png)

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-13-sql-server/sql-server-201202131720334230.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202131720336116.png)

那为什么SQL Server要把日志文件划分出多个VLFS呢？因为SQL Server通过这种方式使得存储引擎管理事务日志更加有效.并且对于日志空间的重复利用也会更加高效。使用VLF作为收缩数据库的最小单位比使用ldf文件作为最小单位无疑是更加高效的.

VLFS的个数和大小无法通过配置进行设定,而是由SQL Server进行管理.当Create或Alter数据库时,SQL Server通过ldf文件的大小来决定VLFS的大小和数量。在日志文件增长时，SQL Server也会重新规划VLFS的数量.

注意：根据这个原理不难看书，如果设置日志文件的增量过小，则会产生过多的VLFS,也就是日志文件碎片，过多的日志文件碎片会拖累SQL Server性能.

SQL Server创建数据库时，根据日志文件\(ldf\)的大小，生成VLF的数量公式如下:

ldf文件的大小 |  VLF的数量  
---|---  
1M到64M |  4  
64M到1GB |  8  
大于1GB |  16  
  
下面我们来看一个例子:

创建数据库，指定日志大小为65M

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-13-sql-server/sql-server-201202131720363938.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202131720349869.png)

通过DBCC，我们可以看到，对应的有8个VLFs:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-13-sql-server/sql-server-201202131720413354.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202131720407399.png)

再次创建数据库，指定日志初始大小为28M:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-13-sql-server/sql-server-201202131720456324.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202131720415612.png)

可以看到，对应的，VLF的数量变为4:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-13-sql-server/sql-server-201202131720599762.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202131720558494.png)

而对于日志文件的增长，SQL Server使用了和创建数据库时相同的公式，也就是每次增长比如为2M，则按照公式每次增长4个VLFs.

我们创建一个TestGrow数据库，指定日志文件为2M，此时有4个VLFS:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-13-sql-server/sql-server-201202131721113558.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202131721004562.png)

当我们增长2M时，这个2M则是按照公式，再次分配4个VLFs:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-13-sql-server/sql-server-201202131721148490.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202131721121149.png)

此时，这时能看到的VLFs数量应该为4+4=8个:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-13-sql-server/sql-server-201202131721155939.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202131721155001.png)

由此可以看出，指定合适的日志文件初始大小和增长，是减少日志碎片最关键的部分.

### 事务日志的逻辑组织构架

当针对数据库对象所做的任何修改保存到数据库之前，相应的日志首先会被记录到日志文件。这个记录会被按照先后顺序记录到日志文件的逻辑末尾，并分配一个全局唯一的日志序列号\(log sequence number,简称LSN）,这个序列号完全是按照顺序来的，如果日志中两个序列号LSN2>LSN1,则说明LSN2所在LSN1之后发生的.

由此可以看出，将日志文件分为多个文件除了磁盘空间的考虑之外。完全不会像数据那样可以并行访问，所以将日志文件分为多个完全不会有性能上的提升.

LSN号可以看作是将日志文件和其记录数据之间的纽带.每一条日志不仅有LSN号，还有其对应事务的事务日志:

一个简单的图片示例如下:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-13-sql-server/sql-server-201202131721177184.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202131721164610.png)

许多类型的操作都记录在事务日志中。这些操作包括： 

  * 每个事务的开始和结束。

  * 每次数据修改（插入、更新或删除）。这包括系统存储过程或数据定义语言 \(DDL\) 语句对包括系统表在内的任何表所做的更改。

  * 每次分配或释放区和页。

  * 创建或删除表或索引。




对于LSN如何在ROLLBACK或者是ROLL FORWARD中以及在备份恢复过程中起作用，会在后续文章中提到

### 总结

本篇文章从事务日志的逻辑和物理构架简单介绍了事务日志的构成.这是理解SQL Server如何利用日志保证持久性和数据备份恢复的基础。下一篇文章将会介绍SQL Server在操作中会如何使用到日志文件。
