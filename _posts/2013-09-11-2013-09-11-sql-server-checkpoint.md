---
layout: post
title: "SQL Server CheckPoint的几个误区"
date: 2013-09-11
categories: blog
tags: [博客园迁移]
---

有关CheckPoint的概念对大多数SQL Server开发或DBA人员都不陌生。但是包括我自己在内，大家对于CheckPoint都或多或少存在某些误区，最近和高文佳同学（感谢高同学的探讨）关于该处进行过一些探讨，整理出来几个误区。

**1.CheckPoint实例级别，而不是数据库级别**

CheckPoint的时间虽然可以在实例级别进行设置，但CheckPoint的过程是以数据库为粒度。从CheckPoint在Redo和Undo的作用来看，CheckPoint是为了优化IO和减少Recovery时间，而Recovery是需要日志支持，因此日志是数据库级别的概念，因此可以知道CheckPoint是以数据库为单位进行的。

我们来做一个简单的实验，分别设置两个连接A和B，A和B使用不同的数据库并修改数据产生脏数据，在A上进行了CheckPoint后，A连接的数据库脏页全部写入磁盘，而B连接产生的脏页依然驻留在Buffer中，因此可以确定CheckPoint是数据库级别而不是服务器级别。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-11-sql-server-checkpoint/sql-server-checkpoint-11173404-be1ab25d110f466c93004db8d560db97.jpg)](//images0.cnblogs.com/blog/35368/201309/11173402-affb9600e70640aa96a28a6e56731981.jpg)

图1.CheckPoint是数据库级别的

**2.由于日志增长导致的自动CheckPoint会将所有数据库的脏页写入磁盘**

事实证明，这也是错误的，自动CheckPoint仅仅会将某些脏页或日志过多的数据库脏页写入磁盘。可以同样通过图1的例子进行。

**3.CheckPoint仅仅将已经提交的脏数据写入磁盘**

这同样是错误的，无论事务是否提交，所产生的脏数据都会被CheckPoint写入磁盘。例证可以参看我的博文:[再谈SQL Server中日志的的作用](http://www.cnblogs.com/CareySon/p/3308926.html)中有关CheckPoint的实验。

**4.如果一个实例上有多个数据库，则CheckPoint是并行的**

错误，通过3502跟踪标记来看，CheckPoint是串行的，也就是一个数据库CheckPoint完了才会继续下一个。如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-11-sql-server-checkpoint/sql-server-checkpoint-11173405-9333f7c4d52945d48fe2fe0c7355a70d.jpg)](//images0.cnblogs.com/blog/35368/201309/11173404-f41e92b245074196bc5f7058d23cbfb9.jpg)

图2.串行CheckPoint

我们可以注意到，CheckPoint使用的是同一个Spid。

**5.将恢复间隔设置为1分钟，意味着每1分钟会对所有的数据库做一次CheckPoint**

错误。将恢复间隔设置为1分钟不能想成建立一个Agent，每分钟写一个CheckPoint命令，这是两码事。这只是意味着每分钟去检查一次是否需要做CheckPoint，如果期间积累的日志量足够，才会对积累足够日志量的数据库去做CheckPoint。即使中间积累了巨量的日志，不到1分钟也不会做CheckPoint。

**6.SQL Server一些Internal CheckPoint时，比如说关闭数据库，会对所有数据库做CheckPoint\(高同学补充\)**

这条是正确的![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-11-sql-server-checkpoint/sql-server-checkpoint-11173405-bd018a6569ca485caec20b25f5ee351d.png)，因为SQL Server此时需要保证所有的数据写入磁盘，从而保证了数据库一致性，如果没有活动的事务，那么这种关闭方式叫做Clean ShutDown，这意味着该数据本身一致，因此即使没有日志，MDF也可以附加。

**7.CheckPoint是一个时间点\(高同学补充\)**

错误，这是打游戏存档的想法，从哪存进度，从哪取进度，是某个时间点。在SQL Server中，CheckPoint是一个完整的过程，这个过程的耗时取决于脏数据的大小，更多资料，请参阅MSDN：<http://technet.microsoft.com/zh-cn/library/ms188748.aspx>

**8.引发自动CheckPoint的条件是内存中脏页的多少\(高同学补充\)**

错误，CheckPoint的触发条件，是在CheckPoint期间生成日志的大小。因此，大家见过内存中有很多脏页，却不引发CheckPoint的情况。

**9.当数据所在磁盘压力大时，通过checkpoint pages/ sec 计数器来观察写入磁盘的脏页\(高同学补充\)**

部分正确。实际上，脏页被写入磁盘一共有3中方式，CheckPoint仅仅是其中一种，我们还需要将Lazy writes/sec考虑在内。

**10.TempDB上永远不会写入脏页**

错误。TempdB是一个特殊的数据库，永远只能简单恢复模式，如果您在TempDB上造成大量脏页，自动CheckPoint时会发现的确不会有任何脏页写入操作，但手动CheckPoint时，脏页依然会被写入磁盘。

最后，再次感谢高文佳同学和我探讨。
