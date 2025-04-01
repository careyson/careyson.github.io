---
layout: post
title: "SQL Server误区30日谈-Day18-有关FileStream的存储，垃圾回收以及其它"
date: 2012-12-25
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

**误区 \#18:如下多个有关FileStream的误区**

全部错误

**18 a\)FileStream数据可以在远程存储**

不能，由于FileStream数据容器\(指的是存放FileStream文件的NTFS文件夹，杜撰出来的术语\)必须像数据文件或日志文件那样符合本地存储策略-也就是说，这个数据容器必须放在对于运行SQL Server的Windows Server是本地存储（译者注：也就是在‘计算机’里能看到的存储，DAC当然是了，其实SAN这类不直接连接服务器的也算是）访问FileStream数据只要客户端连接到了SQL Server服务器并获取响应的事务上下文后，就可以通过UNC路径进行访问了。

**18 b\)FileStream的数据容器可以嵌套**

不能，对于同一个数据库的两个不同的FileStream容器可能在同一个目录下，但是却不能嵌套。而对于不同数据库的FileStream容器无法在同一个目录下。我的一篇博文有一段代码能说明这一点:[Misconceptions around FILESTREAM storage](http://www.sqlskills.com/BLOGS/PAUL/post/Misconceptions-around-FILESTREAM-storage.aspx)。

**18 c\)对于FileStream的更新可以部分更新**

对于任何FileStream的更新都会导致创建一个全新的FileStream文件,这个操作会被日志原原本本的记录下来。这也就是为什么FileStream不能被用于数据库镜像。这么多数据如果用于镜像的话那后果简直不可想象，只能希望未来的SQL Server版本可以修改这种机制以允许部分更新。

**18 d\)FileStream会在不需要的时候立刻被垃圾回收**

错误。FileStream数据会在不再需要并且到了下一个Checkpoint的时候进行垃圾回收。这点并不是那么直接以至于很多人对FileStream的回收机制存在误区。

**18 f\)FileStream存放的目录以及文件名是随机取得**

其实不然，FileStream的文件名其实代表的是创建其操作对应LSN号。表和列的GUID目录名是可以在系统表中获取到。

我下面两篇博文对此有了更详细的解释:

  * [FILESTREAM directory structure](http://www.sqlskills.com/BLOGS/PAUL/post/FILESTREAM-directory-structure.aspx) 解释了如何从一个FileStream所在行来得知其名称

  * [FILESTREAM directory structure - where do the GUIDs come from?](http://www.sqlskills.com/BLOGS/PAUL/post/FILESTREAM-directory-structure-where-do-the-GUIDs-come-from.aspx) 可以望文生义的知道这篇文章所讲述的内容:-\)



