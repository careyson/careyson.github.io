---
layout: post
title: "【译】SQL Server误区30日谈-Day7-一个实例多个镜像和日志传送延迟"
date: 2012-10-24
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

**误区 \#7:一个数据库可以存在多个镜像**

**错误**

****

**** 这个误区就有点老生常谈了。每一个主体服务器只允许一个镜像服务器。如果你希望存在多个主体服务器的副本，那么请使用事务日志传送，事务日志传送允许针对每一个主体存在多个辅助实例。

使用事务日志传送的一个优点是允许其中一个或多个辅助服务器存在延迟还原备份。这也是就是说对主体服务器进行日志备份\(无论你喜欢与否，这几种高可用性技术各自有各自的术语\):

  * 数据库镜像:主体服务器-镜像服务器 
  * 事务日志传送:主要服务器-辅助服务器 
  * 复制:发布服务器-订阅服务器 



当使用镜像时，你在主体服务器Drop掉一个表时，在镜像服务器上同时也会Drop掉这个表\(即使存在延时，你也无法取消掉这个操作\)。但是如果是8小时延时的事务日志传送方式的话，在主要服务器上Drop掉这个表，则辅助服务器上依然可以访问这个表，直到8小时后日志生效。

顺便说一下，SQLCAT Team写了一篇文章，对于一个实例来说，你最多只能镜像10个数据库，文章如下:[Mirroring a Large Number of Databases in a Single SQL Server Instance](http://sqlcat.com/technicalnotes/archive/2010/02/10/mirroring-a-large-number-of-databases-in-a-single-sql-server-instance.aspx)以及我写的另一篇同样关于这个话题的文章:[KB 2001270 Things to consider when setting up database mirroring in SQL Server](http://support.microsoft.com/kb/2001270).
