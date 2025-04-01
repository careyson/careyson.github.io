---
layout: post
title: "SQL Server复制入门(一)----复制简介"
date: 2012-06-20
categories: blog
tags: [博客园迁移]
---

### 简介

SQL Server中的复制\(Replication\)是SQL Server高可用性的核心功能之一,在我看来，复制指的并不仅仅是一项技术，而是一些列技术的集合,包括从存储转发数据到同步数据到维护数据一致性。使用复制功能不仅仅需要你对业务的熟悉，还需要对复制功能的整体有一个全面的了解，本系列文章旨在对SQL Server中的复制进行一个简单全面的探讨。\(PS:在我的上篇文章中我发现某些文章的图片使用mspaint手绘更有感觉，但被很多人吐槽，因此在不考虑个人羞耻感的前提下，本系列文章中的一些图片继续使用mspaint![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201124379450.png)\)。

### 复制是什么

复制，英文是Replication,这个词源自于拉丁文replicare，原意是重复。SQL Server中的复制也是这个意思，复制的核心功能是存储转发，意味着在一个在一个位置增删改了数据以后，重复这个动作到其他的数据源，概念如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321386779.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321374728.png)

图1.复制的基本概念

当然，上面的这个模型是复制最简单的模型，实际中的模型可能会复杂很多，但是大多数使用复制的原因可以分为如下几类：

1.负载均衡----通过将数据复制到其它数据库服务器来减少当前服务器的负载，比如说最典型的应用就是分发数据来分离OLTP和OLAP环境。

2.分区----将经常使用的数据和历史数据隔离，将历史数据复制到其它数据库中

3.授权----将一部分数据提供给需要使用数据的人，以供其使用

4.数据合并-每个区域都有其各自的数据，将其数据进行合并。比如一个大公司，每个地区都有其各自的销售数据，总部需要汇总这些数据。

5.故障转移----复制所有数据，以便故障时进行转移。

虽然需要使用复制的原因多种多样，但是在使用之前你首先要了解复制技术所需的组成元素。

### 复制的组成部分

复制的概念很像发行杂志的模型，从发行商那里出版后，需要通过报刊亭等地方分发到订阅杂志的人手里。对于SQL Server复制来说，这个概念也是如此。对于SQL Server复制来说，发行商，报刊亭，订阅者分别对应的是发布服务器，分发服务器，订阅服务器。概念如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321395516.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/20120620132138433.png)

图2.发布分发订阅的基本概念

**发布服务器**

图2中的发布服务器包含了需要被发布的数据库。也就是需要向其它数据源分发内容的源数据库。当然，被发布的数据首先需要被允许发布。关于这里的详细设置会在文章后面提到。

**分发服务器**

图2中的分发服务器包含了分发数据库，分发数据库的作用是存储转发发布服务器发过来的数据。一个分发服务器支持多个发布服务器，就像一个报刊亭可以出售多个出版社所出的杂志一样。同理，分发服务器也可以和发布服务器是同一个实例，这就像出版商不通过报刊亭，自己直接贩卖杂志一样。

**订阅服务器**

图2中的订阅服务器包含了发布服务器所发布的数据的副本。这个副本可以是一个数据库，或者一个表，甚至是一个表的子集。根据不同的设置，有些发布服务器发布的更新到订阅服务器就是只读的（比如说用于出报表的OLAP环境），或者是订阅服务器也可以进行更新来将这些改变提交到发布服务器。

**发布和文章**

发布指的是可以发布的文章的集合，这些文章包括表，存储过程，视图和用户自定义函数，如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321409519.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321391961.png)

图3.可以发布的内容

当我们发布表时,还可以根据限定条件只发布表的子集。

**订阅**

订阅是相对发布的一个概念，订阅定义了订阅服务器从哪个分发服务器接收发布。有两类订阅方式，推送订阅（Push\)和请求订阅（Pull\),根据名字就可以望文生义的知道,在推送订阅的情况下，当发布服务器产生更新时，分发服务器直接更新订阅的内容，而请求订阅需要订阅服务器定期查看分发服务器是否有可用更新，如果存在可用更新，则订阅服务器更新数据。

### 复制类型

SQL Server将复制方式分为三大类，每一个发布只能有一种复制类型，分别为:快照复制，事务复制和合并复制。

**快照复制**

快照复制将发布的所有表做成一个镜像，然后一次性复制到订阅服务器。中间的更新不会像其它复制类型那样自动传送到订阅服务器。由这个概念不难看出，快照复制的特点会是:

1.占用网络宽带，因为一次性传输整个镜像，所以快照复制的内容不应该太大。

2.适合那些更新不频繁，但每次更新都比较大的数据。比如企业员工信息表，每半年更新一次这类的业务场景。

3.适合订阅服务器是OLAP只读的环境。

来自MSDN的配图能很好的阐述快照复制，如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-20120620112602317.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201126006564.gif)

图4.快照复制

**事务复制**

事务复制就像其名字一样，复制事务。在第一次设置好事务复制后，发布的表、存储过程等将会被镜像，之后每次对于发布服务器所做的改动都会以日志的方式传送到订阅服务器。使得发布服务器和订阅服务器几乎可以保持同步。因此，可以看出事务复制的特点是:

1.发布服务器和订阅服务器内容基本可以同步

2.发布服务器，分发服务器，订阅服务器之间的网络连接要保持畅通。

3.订阅服务器也可以设置成请求订阅,使得订阅服务器也可以不用一直和分发服务器保持连接。

4.适用于要求实时性的环境。

来自MSDN的配图能很好的阐述事务复制，如图5所示

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201126068828.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201126031072.gif)

图5.事务复制

**合并复制**

合并复制即允许发布服务器更新数据库，也允许订阅服务器更新数据。定期将这些更新进行合并，使得发布的数据在所有的节点上保持一致。因此，有可能发布服务器和订阅服务器更新了同样的数据，当冲突产生时，并不是完全按照发布服务器优先来处理冲突，而是根据设置进行处理，这些会在后续文章中讲到。

来自MSDN的配图能很好的阐述合并复制，如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-20120620112613426.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201126118243.gif)

图6.合并复制

### 建立一个简单的事务复制

下面我进行一个简单的事务复制。首先，在本地安装两个SQL Server实例，我本机安装的两个实例分别为SQL Server 2008R2和SQL Server 2012,其中，SQL Server 2008R2作为发布和分发服务器，SQL Server 2012作为订阅服务器，如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321416237.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321405648.png)

图7.复制的两个实例

首先在SQL Server 2008R2上配置发布服务器和分发服务器，选择配置分发，如图8所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321426369.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321418255.png)

图8.配置分发

将发布服务器和分发服务器选择为同1台，如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321441584.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321431485.png)

图9.设置发布服务器和分发服务器为同一台服务器

设置快照文件夹，由上面MSDN的图可知，快照代理是需要在分发服务器上暂存快照的，设置这个目录，如图10所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321468717.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321456667.png)

图10.设置快照文件夹

这里值得注意的是，需要给这个目录对于Everyone设置读取权限，如图11所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-20120620132147801.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321467147.png)

图11.设置读取权限

下一步配置分发向导就按照默认值来，如图12所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-20120620132149443.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321485884.png)

图12.配置分发向导

剩下的步骤都保持默认值，最后成功在SQL Server 2008R2实例上配置发布服务器和分发服务器，如图13所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321501721.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321491622.png)

图13.成功配置发布和分发服务器

下面就要建立一个发布了，选择新建发布，如图14所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321529901.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321513739.png)

图14.新建发布

一路next,在选择发布类型时选择事务发布，如图15所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321544036.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321538921.png)

图15.选择事务发布

发布用于测试的一个表，只有两个列，一个为自增的int型主键id,另一个为随便设置的列，如图16所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321565663.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321555564.png)

图16.设置发布的表\(文章\)

下一个页面不过滤文章，直接保持默认值下一步。在下一个窗口中选择立即创建快照并初始化..如图17所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321583909.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201321575762.png)

图17.立即创造快照并初始化

安全设置保持和SQL Server Agent一样的账户，如图18所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201321598534.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/20120620132158628.png)

图18.快照代理和日志读取代理设置和SQL Server Agent同一个账户

剩下的步骤一路下一步，设置好发布名称后，成功创建发布,如图19所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201322019845.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201322008318.png)

图19.成功创建发布

下面我们来在SQL Server 2012的实例上创建订阅，选择新建订阅，如图20所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201322035517.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201322024895.png)

图20.新建订阅

在欢迎界面选择下一步后，选择刚刚创建的发布,如图21所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201322045682.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201322034503.png)

图21.选择发布服务器

下一步选择推送订阅，以便发布服务器所做的改动能自动更改到订阅服务器，如图22所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201322066437.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/20120620132205241.png)

图23.选择推送订阅

选择保持连接，下一步保持默认值，然后在分发代理安全性下选择模拟进程账户。如图24所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201322084442.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201322074028.png)

图24.选择模拟进程账户

保持默认值，一路下一步直到订阅创建完成，如图25所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201322101816.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201322099209.png)

图25.创建订阅成功

现在我们进行测试，向表中插入100条数据，监视状态，发现100个事务已经成功传到了订阅服务器，如图26所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201322116442.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201322106899.png)

图26.插入的100条数据已经成功传送到订阅服务器

现在我们再来看订阅服务器\(SQL Server 2012\),在发布服务器插入的100条数据已经成功存在于订阅服务器，如图27所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-06-20-sql-server/sql-server-201206201322122081.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201206/201206201322125395.png)

图27.100条数据已经成功发布到了订阅服务器

### 总结

本文对SQL Server的复制进行了大致的讲解，并实现了一个简单的复制。复制的概念需要对SQL Server的各个方面都要有所涉猎，本系列文章的下一篇将会将复制应用的一些模式。
