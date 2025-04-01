---
layout: post
title: "【译】SQL Server误区30日谈-Day2-DBCC CHECKDB会导致阻塞"
date: 2012-10-22
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.AgileSharp.com)上。希望对大家有所帮助。

**误区 \#2: DBCC CHECKDB会引起阻塞，因为这个命令默认会加锁**

这是错误的！

在SQL Server 7.0以及之前的版本中，DBCC CHECKDB命令的本质是C语言实现的一个不断嵌套循环的代码并对表加表锁\(循环嵌套算法时间复杂度是嵌套次数的N次方,作为程序员的你懂得\),这种方式并不和谐,并且…..

在SQL Server 2000时代，一个叫Steve Lindell的哥们（现在仍然在SQL Server Team）使用分析事务日志的方法来检查数据库的一致性的方式重写了DBCC CHECKDB命令。DBCC CHECKDB会阻止截断日志。当将日志从头读到尾时，在事务日志内部进行了某种Recovery操作，这实际上是另一种全新的实现Recovery的代码，但是仅限于CHECKDB命令内部。但这种方式依然存在问题，比如这个命令存在检查失败的可能性，如果检查失败，你还需要重新执行它看是否还会出现同样的错误。并且有时候，这个命令还会使用SCH\_S锁，索然这个锁仅仅阻塞表扫描和表构架的改变，但通过日志来检查一致性的代码也并不是尽善尽美，并且…..

在SQL Server 2005时代，一个叫Paul Randal的家伙（译者：也就是本文作者）再次重写了DBCC CHECKDB命令。这次使用数据库快照来检查一致性（因为数据库快照会提供在数据库某一特定时间点的一致性视图）,因此不再有事务日志的分析代码，不再有任何的锁--因为访问数据库快照不需要对原数据库加任何的锁，缓冲池会自动处理可能出现的资源争用。

如果想了解更多内幕消息，你可以阅读下面的文章:

  * [CHECKDB From Every Angle: Complete description of all CHECKDB stages](http://www.sqlskills.com/BLOGS/PAUL/post/CHECKDB-From-Every-Angle-Complete-description-of-all-CHECKDB-stages.aspx)

  * [CHECKDB From Every Angle: Why would CHECKDB run out of space?](http://www.sqlskills.com/BLOGS/PAUL/post/CHECKDB-From-Every-Angle-Why-would-CHECKDB-run-out-of-space.aspx)

  * [Database snapshots - when things go wrong](http://www.sqlskills.com/BLOGS/PAUL/post/Database-snapshots-when-things-go-wrong.aspx)

  * [Issues around DBCC CHECKDB and the use of hidden database snapshots](http://www.sqlskills.com/BLOGS/PAUL/post/Issues-around-DBCC-CHECKDB-and-the-use-of-hidden-database-snapshots.aspx)

  * [Do transactions rollback when DBCC CHECKDB runs?](http://www.sqlskills.com/BLOGS/PAUL/post/Do-transactions-rollback-when-DBCC-CHECKDB-runs.aspx)

  * [Diskeeper 10 Intelliwrite corruption bug](http://www.sqlskills.com/BLOGS/PAUL/post/Diskeeper-10-Intelliwrite-corruption-bug.aspx)




现在，在任何SQL Server版本中,如果你依然使用WITH TABLOCK提示，那将会产生表锁来保证事务的一致性。但我不推荐这种方式。因为这种方式不仅需要更长的时间，还将会尝试对数据库加排他锁，但已经活动在数据库的连接有可能导致这种方式失败。

在SQL Server 2000中，这个命令阻止事务日志截断将会导致日志不正常增长的相关问题，但对于SQL Server 2005来说，这个命令就会导致快照相关的问题（具体请看上面的链接）。

但是在默认情况下,自从SQL SERVER 2000之后，DBCC CHECKDB不会再产生阻塞。
