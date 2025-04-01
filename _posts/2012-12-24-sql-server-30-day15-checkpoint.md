---
layout: post
title: "SQL Server误区30日谈-Day15-CheckPoint只会将已提交的事务写入磁盘"
date: 2012-12-24
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

**误区 \#15:CheckPoint只会将已提交的事务写入磁盘**

错误

这个误区是由于太多人对日志和恢复系统缺少全面的了解而存在已久。CheckPoint会将自上次CheckPoint以来所有在内存中改变的页写回磁盘\(译者注：也就是脏页\),或是在上一个CheckPoint读入内存的脏页写入磁盘。无论事务是否已经提交，其所影响的页都会在Checkpoint时写回磁盘。但对于TempDB来说例外，因为TempDB的Checkpoint的事件周期中并不包含将脏页写回磁盘的步骤。

如果你想了解更多，请阅读下面文章:

  * Technet 杂志文章:[Understanding Logging and Recovery in SQL Server](http://technet.microsoft.com/en-us/magazine/2009.02.logging.aspx)

  * 博文: [How do checkpoints work and what gets logged](http://www.sqlskills.com/BLOGS/PAUL/post/How-do-checkpoints-work.aspx)

  * 博文: [What does checkpoint do for tempdb?](http://www.sqlskills.com/BLOGS/PAUL/post/What-does-checkpoint-do-for-tempdb.aspx)




你可以使用如下两个跟踪标记查看CheckPoint是如何工作的。

  * 3502: 当CheckPoint开始和结束时，将相关信息写入错误日志

  * 3504: 将CheckPoint时写回磁盘的页的信息写入错误日志




为了使用这个跟踪标记,你必须针对所有线程开启,否则你将会在错误日志中什么都看不到。使用DBCC TRACEON \(3502, 3504, -1\) 针对所有线程开启这两个追踪标记。

下面的代码可以证明Checkpoint会将未提交的脏页写回磁盘，跟随下面的步骤。
    
    
    CREATE DATABASE CheckpointTest;   
    GO   
    USE CheckpointTest;   
    GO 
      
    CREATE TABLE t1 (c1 INT IDENTITY, c2 CHAR (8000) DEFAULT 'a');   
    CREATE 
    CLUSTERED INDEX t1c1 on t1 (c1);   
    GO
    
    
    
    
    SET NOCOUNT ON;   
    GO
    
    
    
    
    CHECKPOINT;   
    GO
    
    
    
    
    DBCC TRACEON (3502, 3504, -1);   
    GO

  


下面那个事务会产生10MB的脏页，紧接着进行CheckPoint
    
    
    BEGIN TRAN;   
    GO   
    INSERT INTO t1 DEFAULT VALUES;   
    GO 1280
    
    
    
    
    CHECKPOINT;   
    GO

  


日志如你所见:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-12-24-sql-server-30-day15-checkpoint/sql-server-30-day15-checkpoint-201212241628166318.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201212/201212241628164399.png)

我们可以清楚的看出，在事务没有提交的情况下，脏页依然会被写入磁盘。
