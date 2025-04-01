---
layout: post
title: "【译】SQL Server误区30日谈-Day12-TempDB的文件数和需要和CPU数目保持一致"
date: 2012-10-29
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

**误区 \#12:TempDB的文件数和需要和CPU数目保持一致**

错误

哎，由于上述误区是微软“官方”的建议，并且还有大量博文坚持这个观点，这个误区已经是老生常谈。

但让人困惑的是SQL CAT团队给出的建议就是1：1，但这个建议是源自扩展方面的原理来说,而不是一个通用法则。因为他们所面对的大型客户数据量服务器和IO子系统都是大部分人没有机会遇到的。

每个实例仅仅允许有一个TempDb,但需要用到TempDB的地方却有很多，所以TempDB很容易成为性能瓶颈，我想大家数人都了解这一点，而大多数人所不了解的应该是在什么情况下才需要额外的TempDB文件。

当你看到PAGELATCH类型的阻塞时，说明遇到内存中分配位图的争用问题了。而看到PAGEIOLATCH，说明遇到I/O子系统层面的争用问题了。对于闩锁（Latch）你可以将其看作和普通锁是一种东西，但更轻量,更短，并且只会被存储引擎内部使用。

MVP Glenn Berry 有一篇[博文](http://glennberrysqlperformance.spaces.live.com/blog/cns!45041418ECCAA960!2991.entry)里有查看sys.dm\_os\_wait\_stats的DMV。这篇博文中可以查到你的服务器造成阻塞最多的原因是什么。如果你发现是PAGELATCH型等待，你可以使用这段[脚本](http://www.sqlservercentral.com/blogs/robert_davis/archive/2010/03/05/Breaking-Down-TempDB-Contention.aspx)来查看是由于FPS,GAM还是SGAM争用造成的问题。

如果你遇到闩锁争用，可以通过跟踪标记1118或是多建一个TempDB文件来缓和这个状况\(原理可以在知识库[KB 328551](http://support.microsoft.com/kb/328551)查到\),我已经写了一篇关于为什么追踪标记1118依然被需要的长博文，链接：[Misconceptions around TF 1118](http://www.sqlskills.com/BLOGS/PAUL/post/Misconceptions-around-TF-1118.aspx)。

在SQL SERVER 2000时代，TempDB的文件数需要和CPU核数保持1：1的关系，在SQL SERVER 2005和2008版本这条建议也适用，但由于SQL SERVER 2005+后的优化措施\(详细请看我的[博文](http://www.sqlskills.com/BLOGS/PAUL/post/Misconceptions-around-TF-1118.aspx)\),你不再需要严格按照1：1的比例关系设置CPU核数和TempDB文件数，而是文件数和CPU核数的比例保持在1:2或是1:4就行了。

\[题外话：在SQL PASS 2011我的好朋友Bob Ward,也是SQL CSS最牛的人。给出了一个新的公式:如果CPU核数小于等于8，使其比例保持在1:1,而如果CPU核数大于8，使用8个文件，当你发现闩锁争用现象时，每次额外加4个文件\]

不过这也不能一概而论。上周我遇到一个问题，一个客户的TempDB负载大到需要32个CPU配上64个TempDB文件才能减轻闩锁争用。这是否意味着这是一个最佳实践呢？当然不是。

那你或许有疑问，为什么1:1的比例不好呢，那是因为太多的TempDB有可能引起另一个性能问题。如果你的一条查询中某些操作（比如排序）需要使用大量的内存，但内存不够时，就需要将这些内容分配到TempDB中。当存在多个TempDB文件时,由于TempDB的循环分配机制,这有可能导致性能被拖累，对于比较大的临时表也是如此。

那为什么循环分配机制对于TempDB存在大量文件时产生性能问题呢？有如下几种可能:

  * 循环分配算法是针对文件组而言，而对于TempDB只能存在一个文件组。当这个文件组包含16或32个文件时，由于循环分配算法的线程有限，但对于大量文件的TempDB依然需要做一些额外的同步工作，因此这部分工作会造成性能损失 
  * TempDB的文件大小不一致，则有可能导致某个单独文件的自动增长，从而造成热点IO。 
  * 当缓冲区需要通过LazyWriter释放一些空间时\(TempDB的Checkpoint不会做写回操作\)，多个TempDB文件有可能导致IO子系统的随机读写问题，这会导致IO方面的性能问题。 



所以这个选择让你进亦忧，退亦忧。到底多少TempDB文件才是合适的呢？我也不能给你具体答案，但是基于我多年咨询经验以及出席各种大会的经验，我可以给你一个指导方针---当为了解决闩锁争用时为TempDB创建多个文件要小心，仅仅在必须情况下才额外增加TempDB文件。也就是你需要在可扩展性和性能之间取得一个平衡。

希望上面的指导方针对你有帮助。

PS:回应一些评论：TempDB的文件没有必要分布在多个存储器之间。如果你看到PAGELATCH类型的等待，即使你进行了分布也不会改善性能，而如果PAGEIOLATCH型的等待，或许你需要多个存储器，但这也不是必然-有可能你需要讲整个TempDB迁移到另一个存储系统，而不是仅仅为TempDB增加一个文件。这需要你仔细分析后再做定夺。
