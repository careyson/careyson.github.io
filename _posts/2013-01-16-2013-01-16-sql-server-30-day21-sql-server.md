---
layout: post
title: "SQL Server误区30日谈-Day21-数据损坏可以通过重启SQL Server来修复"
date: 2013-01-16
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)和博客园上。希望对大家有所帮助。

**误区 \#21:数据库损坏可以通过重启SQL Server或是Windows,或是附加和分离数据库解决**

错误

SQL Server中没有任何一项操作可以修复数据损坏。损坏的页当然需要通过某种机制进行修复或是恢复-但绝不是通过重启动SQL Server,Windows亦或是分离附加数据库。

而实际上，如果你的数据库的损坏程度无法进行Crash Recovery的话\(质疑状态\)，那么分离附加数据库将会是你做的最糟糕的决定。这个原理是由于附加数据库中包含Crash Recovery步骤，如果Crash Recovery失败的话，那么附加也会失败。所以下面的技巧才是你所需要的:[TechEd Demo: Creating, detaching, re-attaching, and fixing a suspect database](http://www.sqlskills.com/BLOGS/PAUL/post/TechEd-Demo-Creating-detaching-re-attaching-and-fixing-a-suspect-database.aspx)。记住，永远不要分离损坏的数据库。

下面这类错误才是有可能通过重启解决:

  * 如果在内存中的页损坏，但在磁盘上的页完好时，重启能够解决损坏问题 
  * 如果损坏发生了,但是重启过程中的某个步骤导致这个页不再被分配，则貌似损坏通过重启解决了，这个问题我之前已经有一篇博文进行阐述了:[Misconceptions around corruptions: can they disappear?](http://www.sqlskills.com/BLOGS/PAUL/post/Misconceptions-around-corruptions-can-they-disappear.aspx)
  * 如果IO子系统也重启,之前SQL Server对IO的需求被IO子系统“卡”住，则重启貌似能解决问题，但实际上这并不是修复损坏，而只是让出问题的IO子系统恢复。我只碰见过三四次这类情况。 



不管怎么说，你起码要做到有对应的备份策略或是容易系统进行恢复和故障转移。重启可不是一个解决方案，这只会浪费时间。
