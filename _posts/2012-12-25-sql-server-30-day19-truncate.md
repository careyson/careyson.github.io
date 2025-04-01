---
layout: post
title: "SQL Server误区30日谈-Day19-Truncate表的操作不会被记录到日志"
date: 2012-12-25
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

这个误区也同样流传已久，我想是时候通过一些Demo进行揭穿了。

**误区 \#19:Truncate表的操作不会被记录到日志**

错误

在用户表中的操作都会被记录到日志。在SQL Server中唯一不会被记录到日志的操作是TempDB中的行版本控制。

Truncate Table语句会将整个表中的所有数据删除。但删除的方式并不是一行一行的删除，而是将组成表的数据页释放，将组成表的相关页释放的操作交给一个后台的线程进行队列处理的过程被称为deferred-drop。使用后台线程处理deferred-drop的好处是这个操作不会使得其所在的事务需要执行很长时间，因此也就不需要大量的锁。在SQL Server 2000SP3之前的版本（这个版本引入了deferred-drop）在Truncate Table的时候出现过多的锁耗尽内存的事是家常便饭。

下面是测试代码:

CREATE DATABASE TruncateTest;   
GO   
USE TruncateTest;   
GO   
ALTER DATABASE TruncateTest SET RECOVERY SIMPLE;   
GO   
CREATE TABLE t1 \(c1 INT IDENTITY, c2 CHAR \(8000\) DEFAULT 'a'\);   
CREATE CLUSTERED INDEX t1c1 on t1 \(c1\);   
GO

SET NOCOUNT ON;   
GO

INSERT INTO t1 DEFAULT VALUES;   
GO 1280

CHECKPOINT;   
GO

上面的测试数据库恢复模式是简单，所以每个Checkpoint都会截断日志\(仅仅是为了简单，哈哈\)。

一分钟后让我们来看看日志中有多少条记录。

SELECT COUNT \(\*\) FROM fn\_dblog \(NULL, NULL\);   
GO

可以看到，现在的日志条目数字为2。

如果你得到的数字不是2，那么再做一次Checkpoint直到数据是2为止。

现在已有的日志已经知道了，那么日志的增长就是由于后面的操作所导致。下面我们执行如下代码:

TRUNCATE TABLE t1;   
GO

SELECT COUNT \(\*\) FROM fn\_dblog \(NULL, NULL\);   
GO

可以看到现在已经有了541条日志记录。很明显Truncate操作是需要记录到日志中的。但也可以看出Truncate并不会逐行删除,因为这541条日志记录删除的是1280条数据。

执行下面语句来查看日志:

SELECT   
\[Current LSN\], \[Operation\], \[Context\],   
\[Transaction ID\], \[AllocUnitName\], \[Transaction Name\]   
FROM fn\_dblog \(NULL, NULL\);

下面是结果:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-12-25-sql-server-30-day19-truncate/sql-server-30-day19-truncate-25095830-9f0cae9d7249441a8a28b2412c9af2e5.png)](//images0.cnblogs.com/blog/35368/201212/25095826-caca1957d0ba42b8abc823a4159ecdc1.png)

图1.查看Truncate后的日志\(部分\)

通过日志可以看出第一条显式开始Truncate Table事务，最后一条开始DeferredAlloc。正如你所见，Truncate操作仅仅是释放了构成表的页和区。

下面这个代码可以查看日志具体所做操作的描述:

SELECT   
\[Current LSN\], \[Operation\], \[Lock Information\], \[Description\]   
FROM fn\_dblog \(NULL, NULL\);   
GO

结果如图2：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-12-25-sql-server-30-day19-truncate/sql-server-30-day19-truncate-25095837-1c3048c14ca540a2b40dbbec4547c7d9.png)](//images0.cnblogs.com/blog/35368/201212/25095831-a420beea6b224094886547cb32318d48.png)

图2.日志操作描述（节选）

你可以看出为了快速恢复的目的而加的相关锁（你可以在我的博文:[Lock logging and fast recovery](http://www.sqlskills.com/BLOGS/PAUL/post/Lock-logging-and-fast-recovery.aspx)中了解更多）。

由上面日志看出，这个操作会对8个页加相关的锁，然后整个区一次性释放。释放过后会对相关的区加IX锁,也就是不能再被使用,当事务提交后才会进行deferred-drop,因此也就保证了Truncate table操作可以回滚。

另外，如果表上存在非聚集索引.那么操作方式也是类似，都是交给一个后台线程然后释放表和索引的页。释放的最小单位就是每个分配单元。按照上面步骤你自己尝试一下就应该能明白我的意思了。

PS：还有一个关于Truncate Table操作不能回滚的误区,我在:[Search Engine Q&A \#10: When are pages from a truncated table reused?](http://www.sqlskills.com/BLOGS/PAUL/post/Search-Engine-QA-10-When-are-pages-from-a-truncated-table-reused.aspx)这篇文章中进行了详细的解释。
