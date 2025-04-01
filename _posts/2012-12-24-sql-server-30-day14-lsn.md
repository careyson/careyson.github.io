---
layout: post
title: "SQL Server误区30日谈-Day14-清除日志后会将相关的LSN填零初始化"
date: 2012-12-24
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

**误区 \#14.清除日志后会将相关的LSN填零初始化**

错误

****

**** 当日志文件在手动增长，自动增长和创建时都会进行填零初始化操作。但是请不要把这个过程和定期清除日志的过程搞混。日志截断仅仅意味着将一个或多个VLF标记为不活动以便被重复使用。在日志清除的过程中，并没有任何日志被清除或是填0。“清除日志”和”截断日志”意思是一样的，但都属于用词不当，因为在这个过程中日志的大小不会有任何改变。

你可以在我的博客中看到有关日志文件填零初始化的博文：[Search Engine Q&A \#24: Why can't the transaction log use instant initialization?](http://www.sqlskills.com/BLOGS/PAUL/post/Search-Engine-QA-24-Why-cant-the-transaction-log-use-instant-initialization.aspx)。以及我发布在TechNet杂志的文章:[Understanding Logging and Recovery in SQL Server](http://technet.microsoft.com/en-us/magazine/2009.02.logging.aspx)。

你可以通过跟踪标记3004来查看SQL Server对日志文件进行填零初始化的过程。将这个追踪标记打开当日志文件增长时，你就可以在SQL Server日志中看到相关信息，下面是测试代码:
    
    
    [DBCC](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DBCC&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) TRACEON (3004, 3605); [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    -- Create database and put in SIMPLE recovery model so the log will clear on 
    [checkpoint](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=checkpoint&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [DATABASE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DATABASE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) LogClearTest [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [PRIMARY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=PRIMARY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ( NAME = 
    'LogClearTest_data', FILENAME = N'D:\SQLskills\LogClearTest_data.mdf') 
    LOG [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ( NAME = 'LogClearTest_log', FILENAME = 
    N'D:\SQLskills\LogClearTest_log.ldf', [SIZE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SIZE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) = 20MB); [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    -- Error log mark 1 ALTER DATABASE LogClearTest SET RECOVERY SIMPLE; 
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    [USE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=USE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) LogClearTest; [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    -- Create table and fill with 10MB - so 10MB in the log CREATE TABLE t1 
    (c1 [INT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=INT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [IDENTITY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=IDENTITY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99), c2 [CHAR](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CHAR&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) (8000) [DEFAULT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DEFAULT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 'a'); [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [INSERT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=INSERT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [INTO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=INTO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) t1 [DEFAULT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DEFAULT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 
    [VALUES](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=VALUES&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99); [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 1280
    -- Clear the log CHECKPOINT; GO
    -- Error log mark 2 ALTER DATABASE LogClearTest SET RECOVERY SIMPLE; 
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)

  


  


相应的，在日志中你可以看到:
    
    
    [DBCC](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DBCC&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) TRACEON (3004, 3605); [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    -- Create database and put in SIMPLE recovery model so the log will clear on 
    [checkpoint](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=checkpoint&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [DATABASE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DATABASE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) LogClearTest [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [PRIMARY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=PRIMARY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ( NAME = 
    'LogClearTest_data', FILENAME = N'D:\SQLskills\LogClearTest_data.mdf') 
    LOG [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ( NAME = 'LogClearTest_log', FILENAME = 
    N'D:\SQLskills\LogClearTest_log.ldf', [SIZE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SIZE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) = 20MB); [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    -- Error log mark 1 ALTER DATABASE LogClearTest SET RECOVERY SIMPLE; 
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    [USE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=USE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) LogClearTest; [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    -- Create table and fill with 10MB - so 10MB in the log CREATE TABLE t1 
    (c1 [INT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=INT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [IDENTITY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=IDENTITY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99), c2 [CHAR](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CHAR&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) (8000) [DEFAULT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DEFAULT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 'a'); [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [INSERT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=INSERT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [INTO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=INTO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) t1 [DEFAULT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DEFAULT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 
    [VALUES](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=VALUES&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99); [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 1280
    -- Clear the log CHECKPOINT; GO
    -- Error log mark 2 ALTER DATABASE LogClearTest SET RECOVERY SIMPLE; 
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)

  


上面测试代码中ALTER DATABASE是作为日志中这部分的开始和结束标记。在两个Alter Database命令中的CheckPoint并不会引起填0操作。如果你需要进一步验证这点，在Checkpoint之前和之后分别使用DBCC SQLPERF \(LOGSPACE\)来查看日志文件的大小，你会发现虽然日志文件大小没有变，但是日志的使用空间百分比会大大减少。

\(下图是译者测试的结果\):

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-12-24-sql-server-30-day14-lsn/sql-server-30-day14-lsn-201212241627157217.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201212/201212241627146444.png)
