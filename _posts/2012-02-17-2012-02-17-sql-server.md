---
layout: post
title: "浅谈SQL Server中的事务日志(三)----在简单恢复模式下日志的角色"
date: 2012-02-17
categories: blog
tags: [博客园迁移]
---

本篇文章是系列文章中的第三篇，前两篇的地址如下：

[浅谈SQL Server中的事务日志\(一\)----事务日志的物理和逻辑构架](http://www.cnblogs.com/CareySon/archive/2012/02/13/2349751.html)

[浅谈SQL Server中的事务日志\(二\)----事务日志在修改数据时的角色](http://www.cnblogs.com/CareySon/archive/2012/02/14/2351149.html)

### 简介

在简单恢复模式下，日志文件的作用仅仅是保证了SQL Server事务的ACID属性。并不承担具体的恢复数据的角色。正如”简单”这个词的字面意思一样，数据的备份和恢复仅仅是依赖于手动备份和恢复.在开始文章之前，首先要了解SQL Server提供的几种不同备份类型。

### SQL Server提供的几种备份类型

SQL Server所提供的几种备份类型基本可以分为以下三种（文件和文件组备份以及部分备份不在本文讨论之列\):

1.完整\(Full\)备份:直接将所备份的数据的所有区\(Extent\)进行复制。这里值得注意的有2点:

  * 完整备份并不像其名字“完整”那样备份所有部分，而是仅备份数据库本身，而不备份日志\(虽然仅仅备份少量日志用于同步） 
  * 完整备份在备份期间，数据库是可用的。完整备份会记录开始备份时的MinLSN号，结束备份时的LSN号，将这个区间的日志进行备份，在恢复时应用到被恢复的数据库\(这里经过修改，感谢魔君六道指出\) 



2.差异\(Differential\)备份:只备份上次完整备份后，做修改的部分。备份单位是区\(Extent\)。意味着某个区内即使只有一页做了变动，则在差异备份里会被体现.差异备份依靠一个BitMap进行维护，一个Bit对应一个区，自上次完整备份后，被修改的区会被置为1，而BitMap中被置为1对应的区会被差异备份所备份。而到下一次完整备份后，BitMap中所有的Bit都会被重置为0。

3.日志\(Log\)备份:仅仅备份自上次完整备份或日志备份之后的记录。在简单模式下，日志备份毫无意义\(SQL Server不允许在简单恢复模式下备份日志\)，下文会说明在简单恢复模式下，为什么日志备份没有意义。

### 简单恢复模式\(Simple Recovery Mode\)

在简单恢复模式下，日志仅仅是为了保证SQL Server事务的ACID。并没有恢复数据的功能.

比如，我们有一个备份计划，如下:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-17-sql-server/sql-server-201202170757153501.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202170757148135.png)

我们在每周一0点做一次完整备份，在周三0点和周五0点分别做差异备份。在简单恢复模式下，如果周六数据库崩溃。我们的恢复计划只有根据周一0点的做的完整备份恢复后，再利用周五0点的差异备份进行恢复.而周五0点之后到服务器崩溃期间所有的数据将会丢失。

正如”简单”这个词所涵盖的意思，在简单恢复模式下，日志可以完全不用管理。而备份和恢复完全依赖于我们自己的完整和差异备份.

恢复模式是一个数据库级别的参数，可以通过在SSMS里或通过SQL语句进行配置:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-17-sql-server/sql-server-201202170757238504.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202170757151582.png)

### 简单恢复模式下日志的空间使用

在本系列文章的第一篇文章提到过，日志文件会划分成多个VLF进行管理，在逻辑上记录是线性的，给每个记录一个顺序的，唯一的LSN。

而在简单恢复模式下,为了保证事务的持久性，那些有可能回滚的数据会被写入日志。这些日志需要被暂时保存在日志以确保在特定条件下事务可以顺利回滚。这就涉及到了一个概念—最小恢复LSN（Minimum Recovery LSN（MinLSN） ）

MinLsn是在还未结束的事务记录在日志中最小的LSN号,MinLSN是下列三者之一的最小值:

  * CheckPoint的开始LSN

  * 还未结束的事务在日志的最小LSN

  * 尚未传递给分发数据库的最早的复制事务起点的 LSN. 




下图是一个日志的片段：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-17-sql-server/sql-server-201202170757248013.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/20120217075723488.gif)

\(图片摘自MSDN）

可以看到，最新的LSN是148，147是CheckPoint,在这个CheckPoint之前事务1已经完成，而事务2还未完成，所以对应的MinLSN应该是事务2的开始，也就是142.

而从MinLSN到日志的逻辑结尾处，则称为活动日志\(Active Log\)。

而活动日志分布在物理VLF上的关系可以用下图表示:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-17-sql-server/sql-server-201202170757243063.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202170757247490.png)

因此，VLF的状态是源自其上所含有的LSN的状态，可以分为两大类:活动VLF和不活动VLF

而更加细分可以将VLF的状态分为以下四类:

  1. **活动\(Active\)** –在VLF 上存储的任意一条LSN是活动的时，则VLF则为活动状态，即使一个200M的VLF只包含了一条LSN，如上图的VLF3 
  2. **可恢复\(Recoverable\)** – VLF是不活动的，VLF上不包含活动LSN,但还未被截断\(truncated\) 
  3. **可重用\(Reusable\)** – VLF是不活动的，VLF上不包含活动LSN,已经被截断\(truncated\)，可以重用 
  4. **未使用\(Unused\)** – VLF是不活动的,并且还未被使用过 



概念如下图:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-17-sql-server/sql-server-201202170757252572.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202170757246999.png)

而所谓的截断\(truncated\)只是将可恢复状态的VLF转换到可重用状态。在简单恢复模式下，每一次CheckPoint，都会去检查是否有日志可以截断.如果有inactive的VLF时，CheckPoint都会将可截断部分进行截断，并将MinLSN向后推.

在日志达到日志文件\(ldf文件）末尾时，也就是上图的VLF8时，会重新循环到VLF1开始，以便让空间进行重复利用.所以日志虽然可以从物理顺序上是从VLF1到VLF8，但逻辑顺序可以是从VLF6开始到VLF2结束:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-17-sql-server/sql-server-20120217075725130.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202170757254557.png)

因此可以看出，简单恢复模式下日志是不保存的（当事务结束后，相关的会被截断）。仅仅是用于保证事务回滚和崩溃恢复的用途.所以备份日志也就无从谈起，更不能利用日志来恢复数据库。

### 总结

本文介绍了简单恢复模式下日志的原理，并简单的引出了一些备份或者恢复数据的基础。而实际上，除了在开发或测试环境下。使用简单恢复模式的场景并不多，因为在现实生活中，在生产环境允许几个小时的数据丢失的场景几乎没有.下篇文章将会讲述在完整恢复模式下，日志的作用。
