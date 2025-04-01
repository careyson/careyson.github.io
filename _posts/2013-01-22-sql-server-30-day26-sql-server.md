---
layout: post
title: "SQL Server误区30日谈-Day26-SQL Server中存在真正的“事务嵌套”"
date: 2013-01-22
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

**误区 \#26: SQL Server中存在真正的“事务嵌套”**

错误

嵌套事务可不会像其语法表现的那样看起来允许事务嵌套。我真不知道为什么有人会这样写代码，我唯一能够想到的就是某个哥们对SQL Server社区嗤之以鼻然后写了这样的代码说：“玩玩你们”。

让我更详细的解释一下，SQL Server允许你在一个事务中开启嵌套另一个事务,SQL Server允许你提交这个嵌套事务，也允许你回滚这个事务。

但是，嵌套事务并不是真正的“嵌套”，对于嵌套事务来说SQL Server仅仅能够识别外层的事务。嵌套事务是日志不正常增长的罪魁祸首之一因为开发人员以为回滚了内层事务，仅仅是回滚内层事务。

但实际上当回滚内层事务时，会回滚整个内层事务，而不是仅仅是内层。这也是为什么我说嵌套事务并不存在。

所以作为开发人员来讲，永远不要对事务进行嵌套。事务嵌套是邪恶的。

如果你不相信我说的，那么通过下面的例子就就会相信。创建完数据库和表之后，每一条记录都会导致日志增加8K。

CREATE DATABASE NestedXactsAreNotReal;   
GO   
USE NestedXactsAreNotReal;   
GO   
ALTER DATABASE NestedXactsAreNotReal SET RECOVERY SIMPLE;   
GO   
CREATE TABLE t1 \(c1 INT IDENTITY, c2 CHAR \(8000\) DEFAULT 'a'\);   
CREATE CLUSTERED INDEX t1c1 ON t1 \(c1\);   
GO   
SET NOCOUNT ON;   
GO

**测试 \#1：回滚内部事务时仅仅回滚内部事务?**

BEGIN TRAN OuterTran;   
GO 

INSERT INTO t1 DEFAULT Values;   
GO 1000 

BEGIN TRAN InnerTran;   
GO 

INSERT INTO t1 DEFAULT Values;   
GO 1000 

SELECT @@TRANCOUNT, COUNT \(\*\) FROM t1;   
GO 

你可以看到得出的结果是2和2000，下面我来回滚内部的事务，按照我们的猜想应该只回滚1000条吧，但事实上你会得到如下结果:

ROLLBACK TRAN InnerTran;   
GO   


消息 6401，级别 16，状态 1，第 2 行   
无法回滚 InnerTran。找不到该名称的事务或保存点。

好吧，由[Books Online](http://msdn.microsoft.com/en-us/library/ms181299.aspx)来看,我只能使用外部事务的名称或是将事务名称留空来进行回滚，代码如下:

ROLLBACK TRAN;   
GO 

SELECT @@TRANCOUNT, COUNT \(\*\) FROM t1;   
GO 

现在我得到结果是0和0。正如[Books Online](http://msdn.microsoft.com/en-us/library/ms181299.aspx)所言,这个回滚操作将外部事务进行了回滚并将全局变量@@TRANCOUNT设置为0。事务中所有的修改都被回滚，如果想部分回滚的话只能使用SAVE TRAN 和ROLLBACK TRAN。

**测试 \#2：嵌套事务中内部事务提交后会保存内部事务的修改吗？**

BEGIN TRAN OuterTran;   
GO 

BEGIN TRAN InnerTran;   
GO 

INSERT INTO t1 DEFAULT Values;   
GO 1000 

COMMIT TRAN InnerTran;   
GO 

SELECT COUNT \(\*\) FROM t1;   
GO

正如我所期待，得到的结果是1000。这说明内部事务提交是会修改到磁盘的。但是如果这时外部事务回滚的话，那么不应该回滚内部事务…

ROLLBACK TRAN OuterTran;   
GO 

SELECT COUNT \(\*\) FROM t1;   
GO

但运行上面查询后结果是0，这说明外部事务的回滚会影响内部事务。

**测试 \#3：提交嵌套的事务的内部事务至少可以让我清除日志吧。**

在开始这个测试之前我首先清除了日志，然后运行如下代码：

BEGIN TRAN OuterTran;   
GO

BEGIN TRAN InnerTran;   
GO

INSERT INTO t1 DEFAULT Values;   
GO 1000

DBCC SQLPERF \('LOGSPACE'\);   
GO

得到结果:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-01-22-sql-server-30-day26-sql-server/sql-server-30-day26-sql-server-22130341-494d6f0784e247fabf4f3deb5d5140f5.png)](//images0.cnblogs.com/blog/35368/201301/22130341-6987c886169745e6a8744938ef045862.png)

  


下面我将事务提交后运行CheckPoint\(对于简单恢复模式的数据库将会截断日志\),得到的结果:

COMMIT TRAN InnerTran;   
GO

CHECKPOINT;   
GO

DBCC SQLPERF \('LOGSPACE'\);   
GO

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-01-22-sql-server-30-day26-sql-server/sql-server-30-day26-sql-server-22130342-f5435701aeb64fac88c9cb83b63bfe5a.png)](//images0.cnblogs.com/blog/35368/201301/22130341-c9d5c80b488049b2ae011cad8652f819.png)

我们发现日志的使用不减反赠，这是由于日志写入了CheckPoint记录（详情请看:[How do checkpoints work and what gets logged](http://www.sqlskills.com/BLOGS/PAUL/post/How-do-checkpoints-work.aspx)）。提交内部事务不会导致日志被清除，这是由于外部事务回滚时也会连同内部事务一起回滚（译者注：所以这部分VLF在外部事务提交之前永远不会被标记位reusable）。所以这部分日志在外部事务提交之前永远不会被截断。为了证明这一点，我提交外部事务，然后再来看日志：

COMMIT TRAN OuterTran;   
GO

CHECKPOINT;   
GO

DBCC SQLPERF \('LOGSPACE'\);   
GO

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-01-22-sql-server-30-day26-sql-server/sql-server-30-day26-sql-server-22130343-b5fcb5e42ad141beae1ee8edcf1f53dc.png)](//images0.cnblogs.com/blog/35368/201301/22130342-ee6867f662704a649b9ed4aba264db2e.png)

怎么样，日志使用百分比大幅下降了吧。

**对于嵌套事务来说---Just Say no** 。\(这句话你可以当作来自SQLSkill.com的一个热心的家伙给的福利![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-01-22-sql-server-30-day26-sql-server/sql-server-30-day26-sql-server-22130343-2c817823ccb54feba4851710c4f5421e.png)\)
