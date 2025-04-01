---
layout: post
title: "【译】SQL Server误区30日谈-Day9-数据库文件收缩不会影响性能"
date: 2012-10-26
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

**误区 \#9: 数据库文件收缩不会影响性能**

****

Hahahahahahahahahahahahahahahaha

\(擦掉眼角的泪水和掉在键盘上的鼻涕，我才能勉强把注意力集中在屏幕上\)

错误\!

收缩数据库文件唯一不影响性能的情况是文件末尾有剩余空间的情况下，收缩文件指定了TruncateOnly选项。

收缩文件的过程非常影响性能，这个过程需要移动大量数据从而造成大量IO，这个过程会被记录到日志从而造成日志暴涨，相应的，还会占去大量的CPU资源。

不仅在收缩的过程中影响性能，并且在文件收缩之后同样影响应能，收缩产生的大量日志会被事务日志传送，镜像，复制能操作重复执行。而空间不够时，文件还需要填0初始化从而影响性能（除非你开启的不用填零初始化的选项）。

这还不算最糟，最糟的结果是文件收缩造成了大量的索引碎片，对于scan操作来说这个碎片影响性能。

不幸的是，收缩数据库的代码不是我写的（如果要是我写的话，我一开始就不会允许这种机制的）所以我们唯一能做的就是接受这种操作。

如果你想找到替代数据库文件收缩的方式，请看这篇博文：[Why you should not shrink your data files](http://www.sqlskills.com/BLOGS/PAUL/post/Why-you-should-not-shrink-your-data-files.aspx),或者是一开始你就对文件做好规划:[Importance of data file size management](http://www.sqlskills.com/BLOGS/PAUL/post/Importance-of-data-file-size-management.aspx)。还有这篇:[TGIF Time Warp](http://www.sqlskills.com/BLOGS/PAUL/post/TGIF-Time-Warp.aspx).

孩子，记住这一点:

  * 数据文件收缩是邪恶的 
  * 收缩数据库更加邪恶 
  * 自动收缩那简直就是十恶不赦了 



简单的对收缩说NO就可以让我们永远远离其造成的烦恼。
