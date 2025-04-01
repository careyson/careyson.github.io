---
layout: post
title: "【译】SQL Server误区30日谈-Day3-即时文件初始化特性可以在SQL Server中开启和关闭"
date: 2012-10-22
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)和博客园上。希望对大家有所帮助。

**误区 \#3: 即时文件初始化特性可以在SQL Server中 a\)开启 和 b\)关闭**

a\)是不允许的 b\)是允许的

即时文件初始化是一个在SQL Server 2005以及之上的版本鲜为人知的特性。这个特性允许数据文件\(仅仅是数据文件，不包括日志文件\)初始化的过程跳过填0初始化过程。这种方式是在发生灾难时大大减少Downtime的好办法---在恢复数据库时由于免去了填0初始化的过程而直接开始恢复过程。

我之前已经写过关于即时文件初始化误区的文章了（见[Misconceptions around instant initialization](http://www.sqlskills.com/BLOGS/PAUL/post/Misconceptions-around-instant-file-initialization.aspx)）,但这并没有谈到这方面误区。

你并不能在SQL Server中开启这个特性。在SQL Server启动时会检查启动SQL Server的账户是否拥有适当的Windows权限\(也就是“执行卷维护任务”这个权限\),当启动SQL Server实例的账户拥有这个权限后，这个特性就会针对这个实例开启，见图1.Kimberly有一篇关于讲述如何开启这个特性细节的文章[Instant Initialization - What, Why, and How](http://sqlskills.com/BLOGS/KIMBERLY/post/Instant-Initialization-What-Why-and-How.aspx)。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-10-22-sql-server-30-day3-sql-server/sql-server-30-day3-sql-server-201210221025465891.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201210/20121022102546940.png)

图1.开启执行卷维护任务\(Perform Volume Maintenance Tasks \)

你可以在SQL Server中查看即时文件初始化特性是否开始，通过追踪标志3004\(3605可以强制输出错误信息\)创建一个数据库，在日志中查看是否有填0操作,如果即时文件初始化有填0初始化操作，则这个特性在SQL Server中并没有开启。

你可以在SQL Server中通过追踪标志1806设置为ON来暂时停止即时文件初始化特性。如果你想永久的禁止这个特性，请把启动SQL Server账户中”执行卷维护任务”这个权限删除。

这两个追踪标志是在[SQL Server Premier Field Engineer Blog](http://blogs.msdn.com/sql_pfe_blog/default.aspx)和[How and Why to Enable Instant File Initialization](http://blogs.msdn.com/sql_pfe_blog/archive/2009/12/23/how-and-why-to-enable-instant-file-initialization.aspx)这两篇博文中首次被提到的。

如果可以的话，尽量打开这个特性。
