---
layout: post
title: "【译】SQL Server误区30日谈-Day5-AWE在64位SQL SERVER中必须开启"
date: 2012-10-23
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

**误区 \#5: AWE在64位SQL SERVER中必须开启**

错误！

**** 在坊间流传的有关AWE的设置的各种版本让人非常困惑。比如说如何设置起作用，如何设置不起作用，在32位和64位上是否需要AWE等。

好吧，我来概括一下:

  * 在64位系统\(SQL SERVER 2005+版本\) 
    * AWE是不需要的\(即使是ON状态，也毫无影响\) 
    * 开启“锁定内存页”使得缓冲池中的内存页不会被置换到虚拟内存中\(实际上所有的Single Page Allocator分配和Stolen的内存都不会被置换\) 
    * 当开启“锁定内存页时”,SQL Server使用Windows AWE API来分配内存，这种方式略快 
    * “锁定内存页”仅仅在标准版和企业版中存在（译者注：在非生产环境的开发版也是存在的） 
  * 在32位系统\(SQL SERVER 2005+版本\) 
    * 为了使用大于4G的内存，必须开启AWE来使用额外的虚拟地址空间 
    * 为了使用AWE，“锁定内存页”权限必须开启 
    * “锁定内存页”仅仅在标准版和企业版中存在（译者注：在非生产环境的开发版也是存在的） 



看上去有点复杂，这也是为什么会引起困惑吧。

我的一个来自CSS的好朋友Bob Ward有一篇关于这块非常好的博文:[Fun with Locked Pages, AWE, Task Manager, and the Working Set…](http://blogs.msdn.com/psssql/archive/2009/09/11/fun-with-locked-pages-awe-task-manager-and-the-working-set.aspx)

PS:译者有一篇关于内存管理的一篇文章:[浅谈SQL Server 对于内存的管理](http://www.cnblogs.com/CareySon/archive/2012/08/16/HowSQLServerManageMemory.html)
