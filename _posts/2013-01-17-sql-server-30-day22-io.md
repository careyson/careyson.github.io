---
layout: post
title: "SQL Server误区30日谈-Day22-资源调控器可以调控IO"
date: 2013-01-17
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.AgileSharp.com)上。希望对大家有所帮助。

**误区 \#22: 资源调控器可以调控IO**

错误

资源调控器无法调控IO，希望下一个版本的SQL Server支持调控IO，调控IO对于对于减少对于大表的scan操作带来的性能影响很有帮助。

下面列表中的功能资源调控器同样也无法完成:

  * 调控Buffer Pool的内存，内存调控器仅仅可以调控执行计划所占的内存，但对于Buffer Pool中缓存的数据页是无法调控的 
  * 可以对多个实例进行当作一个逻辑实体进行资源调控。这是不能的，对于多实例的资源调控只能通过Windows Server资源调控器实现，在这基础之上，在每台实例上对资源调控器进行设置 
  * 允许资源调控器对资源的使用进行监测，当超过阈值时进行报警 



别会错意，我可不是说资源调控器不好，而是说加上了上面的功能会更好。

我的一个朋友，同时也是SQL MVP Aaron Bertrand 和SQL Team的项目经理写了关于这一点的白皮书:[Using the Resource Governor](http://download.microsoft.com/download/D/B/D/DBDE7972-1EB9-470A-BA18-58849DB3EB3B/ResourceGov.docx)。
