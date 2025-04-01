---
layout: post
title: "SQL Server误区30日谈-Day27-使用BACKUP ... WITH CHECKSUM可以替代DBCC CheckDB"
date: 2013-01-25
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

**误区 \#27:使用BACKUP ... WITH CHECKSUM可以替代DBCC CheckDB**

错误

乍一看，由于BACKUP WITH CHECKSUM会检测所有分配出去的页的校验和的值，这个误区貌似是这么回事，但实际上并不是这么回事，原因如下:

由SQL Server 2000或是更早版本升上来的数据库page checksums必须开启，在开启后，并不是数据库中所有的页都会被叫上页校验和，当页损坏发生时，IO系统可不会区分损坏的页是有页校验和还是没有校验和的。所以使用BACKUP ... WITH CHECKSUM就有可能导致一些损坏页不被发现，造成的后果……

除此之外，还有一个问题是完整备份的时间间隔相对比较长，假如说一个月，而相对于DBCC CheckDB的最佳实践是一个礼拜，这导致WITH CHECKSUM不能替代CHECKDB。即使你每周都进行差异备份，但差异备份只会检测差异部分的页校验和。

最后一点，也是危害最大的一点,就是使用BACKUP WITH CHECKSUM选项不能发现内存中的页损坏。这是因为由于内存芯片或是WINDOWS进程导致内存中的页损坏，并且在这之后写回磁盘。这导致损坏页却有正常的校验和，只有使用DBCC CheckDB才能发现这类错误。

因此，说到底，你必须经常使用DBCC CHECKDB，如果对此你仍然心存疑问，请看我之前的一篇文章:[CHECKDB From Every Angle: Consistency Checking Options for a VLDB](http://www.sqlskills.com/BLOGS/PAUL/post/CHECKDB-From-Every-Angle-Consistency-Checking-Options-for-a-VLDB.aspx)。

扩展阅读:[Search Engine Q&A \#26: Myths around causing corruption](http://www.sqlskills.com/BLOGS/PAUL/post/Search-Engine-QA-26-Myths-around-causing-corruption.aspx)
