---
layout: post
title: "【译】SQL Server误区30日谈-Day4-DDL触发器就是INSTEAD OF触发器"
date: 2012-10-22
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)和博客园上。希望对大家有所帮助。

**误区 \#4: DDL触发器\(SQL Server 2005之后被引入\)就是INSTEAD OF触发器**

这是错误的

****

**** DDL触发器的实现原理其实就是一个AFTER触发器。这个意思是先发生DDL操作，然后触发器再捕捉操作（当然如果你在触发器内写了Rollback,则也可能回滚）。

存在Rollback也意味着这个触发器并不像你想象的那么轻量，来看下面的例子:

ALTER TABLE MyBigTable ADD MyNewNonNullColumn VARCHAR \(20\) DEFAULT 'Paul'

如果存在一个defined for ALTER\_TABLE事件的DDL触发器,或是一个更宽泛的事件比如DDL\_TABLE\_EVENTS。上面那个DDL代码将会对表中每一行数据加进新列，之后触发触发器操作。如果你的触发器中存在回滚来阻止DDL操作发生，那么这个代价可不小\(不信的话你自己看看这么做后产生的日志\)。

当然更好的办法是对ALTER设置GRANT或是DENY权限，或是仅仅允许通过你创建的存储过程进行DDL操作。

但不管怎么样，虽然DDL触发器可以达到禁止DDL的操作的目的，但代价昂贵。而DDL触发器的好处是允许记录某些人做了某些修改表之类的操作，所以我并不是说不允许DDL触发器，而是要小心使用。

Kimberly有一篇非常好的关于DDL触发器的博文：["EXECUTE AS" and an important update your DDL Triggers \(for auditing or prevention\)](http://www.sqlskills.com/blogs/kimberly/post/EXECUTE-AS-and-an-important-update-your-DDL-Triggers-\(for-auditing-or-prevention\).aspx)”。
