---
layout: post
title: "DBA应该知道的一些SQL Server跟踪标记"
date: 2013-04-23
categories: blog
tags: [博客园迁移]
---

### 跟踪标记是什么？

对于DBA来说，掌握Trace Flag是一个成为SQL Server高手的必要条件之一，在大多数情况下，Trace Flag只是一个剑走偏锋的奇招，不必要，但在很多情况下，会使用这些标记可以让你更好的控制SQL Server的行为。

下面是官方对于Trace Flag的标记:

**跟踪标记是一个标记，用于启用或禁用SQL Server的某些行为。**

由上面的定义不难看出，Trace Flag是一种用来控制SQL Server的行为的方式。很多DBA对Trace Flag都存在一些误区，认为只有在测试和开发环境中才有可能用到Trace Flag，这种想法只能说部分正确，因此对于Trace Flag可以分为两类，适合在生产环境中使用的和不适合在生产环境中使用的。

Important:Trace Flag属于剑走偏锋的招数，在使用Trace Flag做优化之前，先Apply基本的Best Practice。

### 如何控制跟踪标记

控制跟踪标记的方式有以下三种：

**1.通过DBCC命令**

可以通过DBCC命令来启用或关闭跟踪标记，这种方式的好处是简单易用，分别使用下面三个命令来启用，禁用已经查看跟踪标记的状态：

  * DBCC TRACEON\(2203,-1\) 
  * DBCC TRACEOFF\(2203,1\) 
  * DBCC TRACESTATUS 



其中，TRACEON和TRACEOFF第二个参数代表启用标志的范围，1是Session Scope,-1是Global Scope,如果不指定该值，则保持默认值Session Scope。

另外，值得说的是，如果你希望在每次SQL Server服务启动时通过DBCC命令控制某些Flag，则使用
    
    
    EXEC sp_procoption @ProcName = '<procedure name>' 
        , @OptionName = ] 'startup' 
        , @OptionValue = 'on'; 

这个存储过程来指定，sp\_procoption存储过程会在SQL Server服务器启动时自动执行。

还有一点值得注意的是，不是所有的跟踪标记都可以用DBCC命令启动，比如Flag 835就只能通过启动参数指定。

**2.通过在SQL Server配置管理器中指定**

这种方式是通过在数据库引擎启动项里加启动参数设置，只有Global Scope。格式为-T\#跟踪标记1;T跟踪标记2;T跟踪标记3。

**3.通过注册表启动**

这种方式和方法2大同小异，就不多说了。

### 一些在生产环境中可能需要的跟踪标记
    
    
    **Trace Flag 610**

减少日志产生量。如果你对于日志用了很多基础的best practice，比如说只有一个日志文件、VLF数量适当、单独存储，如果还是不能缓解日志过大的话，考虑使用该跟踪标记。 

参考资料：
    
    
    <http://msdn.microsoft.com/en-us/library/dd425070.aspx>

<http://blogs.msdn.com/b/sqlserverstorageengine/archive/2008/10/24/new-update-on-minimal-logging-for-sql-server-2008.aspx>
    
    
    **Trace Flag  834**

使用 Microsoft Windows 大页面缓冲池分配。如果服务器是SQL Server专用服务器的话，值得开启该跟踪标记。 
    
    
    **Trace Flag  835**

允许SQL Server 2005和2008标准版使用＂锁定内存页＂，和在组策略中设置的结果大同小异，但是允许在标准版中使用． 
    
    
    **Trace Flag  1118**
    
    
    tempdb分配整个区，而不是混合区，减少SGAM页争抢。
    
    
    当apply tempdb的best practice之后，还遇到争抢问题，考虑使用该跟踪标记。
    
    
    参考资料：

<http://blogs.msdn.com/b/psssql/archive/2008/12/17/sql-server-2005-and-2008-trace-flag-1118-t1118-usage.aspx>
    
    
    **Trace Flag  1204和1222**
    
    
    这两个跟踪标记都是将死锁写到错误日志中，不过1204是以文本格式进行，而1222是以XML格式保存。可以通过
    
    
    **sp_readerrorlog** 查看日志**。**
    
    
    ****
    
    
    ****
    
    
    ****
    
    
    ****
    
    
    **Trace Flag  1211和1224**

两种方式都是禁用锁升级。但行为有所差别1211是无论何时都不会锁升级，而1224在内存压力大的时候会启用锁升级，从而避免了out-of-locks错误。当两个跟踪标记都启用是，1211的优先级更高。 
    
    
    **Trace Flag  2528**

禁用并行执行DBCC CHECKDB, DBCC CHECKFILEGROUP,DBCC CHECKTABLE。这意味着这几个命令只能单线程执行，这可能会需要更多的时间，但是在某些特定情况下还是有些用处。 
    
    
    **Trace Flag  3226   **

防止日志记录成功的备份。如果日志备份过于频繁的话，会产生大量错误日志，启用该跟踪标记可以使得日志备份不再被记录到错误日志。 
    
    
    **Trace Flag  4199**
    
    
    **所有ＫＢ补丁对于查询分析器行为的修改都生效，这个命令比较危险，可能扫称性能的下降，具体请参看：**
    
    
    <http://support.microsoft.com/kb/974006>
    
    
     
    
    
     

### 不应该在生产环境中启用的跟踪标记
    
    
     
    
    
    **Trace Flag  806 **
    
    
    ****
    
    
    在读取过程中对页检查逻辑一致性，在错误日志中就可以看到类似下面的信息：
    
    
    ****
    
    
    2004-06-25 11:29:04.11 spid51 错误： 823，严重性： 24 日状态： 2  
    2004-06-25 11:29:04.11 spid51 I/O 错误 （审核失败） 在读取过程中检测到的偏移量主题 SQL Server\MSSQL\data\pubs.mdf e:\Program 文件中的 0x000000000b0000.
    
    
     
    
    
    参考资料：<http://support.microsoft.com/kb/841776>
    
    
     
    
    
    该跟踪标记会极大的降低性能！！！
    
    
      
    
    
    
    **Trace Flag 818**
    
    
     
    
    
    检查写一致性
    
    
    踪标志 818 启用了一个内存中的环形缓冲区，用于跟踪由运行 SQL Server 的计算机执行的最后 2,048 个成功写操作（不包括排序和工作文件 I/O）。发生 605、823 或 3448 之类的错误时，将传入缓冲区的日志序列号 (LSN) 值与最新写入列表进行比较。如果在读操作期间检索到的 LSN 比在写操作期间指定的更旧，就会在 SQL Server 错误日志中记录一条新的错误信息。大部分 SQL Server 写操作以检查点或惰性写入形式出现。惰性写入是一项使用异步 I/O 操作的后台任务。环形缓冲区的实现是轻量的，因此对系统性能的影响可以忽略。
    
    
      
    
    
    
    参考资料：<http://support.microsoft.com/kb/826433>
    
    
      
    
    
    
    **Trace Flag 1200 **
    
    
     
    
    
    返回加锁信息的整个过程，是学习加锁过程很牛逼的标志，示例代码如下：
    
    
    ****
    
    
    DBCC TRACEON(1200,-1)
    DBCC TRACEON(3604)
    DBCC TRACESTATUS
    
    SELECT * FROM AdventureWorks.person.Address
    
    
     
    
    
    参考资料：
    
    
    <http://stackoverflow.com/questions/7449061/nolock-on-a-temp-table-in-sql-server-2008>
    
    
      
    
    
    
    **Trace Flag 1806**
    
    
    ****
    
    
    禁用即时文件初始化，所有的磁盘空间请求全部使用填０初始化，可能造成在空间增长时产生阻塞。
    
    
    ****
    
    
    **Trace Flag 3502**
    
    
    在日志中显示有关checkpoint的相关信息。如图１所示。

****
    
    
    **[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-04-23-dba-sql-server/dba-sql-server-23233744-e7ff1d4dce064aa18cc30d4675754349.png)](//images0.cnblogs.com/blog/35368/201304/23233741-bd4a4a74a29d4519be036f11f5abc7a7.png)**
    
    
    图１.在错误日志中显示Checkpoint
    
    
      
    **Trace Flag 3505**
    
    
    不允许自动进行checkpoint,checkpoint只能手动进行，是非常危险的一个命令。
    
    
     
    
    
     

### 小结

跟踪标志是控制SQL Server行为的一种方式，对于某些跟踪标志来说，可以在生产环境中提高性能，而对于另一些来说，用在生产环境中是一件非常危险的事情，只有在测试环境中才能被使用。要记住，跟踪标记对于调优是一种剑走偏锋的手段，只有在使用了所有基本的调优手段之后，才考虑使用跟踪标记。
