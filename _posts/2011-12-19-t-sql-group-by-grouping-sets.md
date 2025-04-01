---
layout: post
title: "T-SQL中的GROUP BY GROUPING SETS"
date: 2011-12-19
categories: blog
tags: [博客园迁移]
---

最近遇到一个情况,需要在内网系统中出一个统计报表。需要根据不同条件使用多个[group by](http://www.cnblogs.com/CareySon/archive/2011/05/18/2049727.html)语句.需要将所有聚合的数据进行[UNION](http://www.cnblogs.com/CareySon/archive/2011/10/13/2210156.html)操作来完成不同维度的统计查看.

直到发现在SQL SERVER 2008之后引入了GROUPING SETS这个对于GROUP BY的增强后，上面的需求实现起来就简单多了,下面我用AdventureWork中的表作为DEMO来解释一下GROUPING SETS.

假设我现在需要两个维度查询我的销售订单，查询T-SQL如下:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-19-t-sql-group-by-grouping-sets/t-sql-group-by-grouping-sets-201112191304494093.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112191304484244.png)

而使用SQL SERVER 2008之后新增的GROUPING SETS语句，仅仅需要这样写:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-19-t-sql-group-by-grouping-sets/t-sql-group-by-grouping-sets-201112191304534772.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112191304517116.png)

值得注意的是，虽然上面使用GROUPING SETS语句和多个GROUP BY语句产生的结果是完全一样的，但顺序却完全不同。

### **GROUPING SETS,仅仅是语法糖?**

* * *

从上面结果来看，使用GROUPING SETS仅仅是一个可以少写些代码的语法糖.但实际情况是，GROUPING SETS在遇到多个条件时，聚合是一次性从数据库中取出所有需要操作的数据，在内存中对数据库进行聚合操作并生成结果。而UNION ALL是多次扫描表，将返回的结果进行UNION操作，这也就是为什么GROUPING SETS和UNION操作所返回的数据顺序是不同的.

下面通过查看上面两个语句的IO和CPU来进行对比:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-19-t-sql-group-by-grouping-sets/t-sql-group-by-grouping-sets-201112191305001039.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/20111219130455543.png)

通过上面的图来看GROUPING SETS不仅仅只是语法糖.而是从执行原理上做出了改变.

对于GROUPING SETS来说，还经常和GROUPING函数联合使用，这个函数是反映目标列是否聚合，如何聚合则返回1,否则返回0，如下：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-19-t-sql-group-by-grouping-sets/t-sql-group-by-grouping-sets-201112191305127932.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112191305029874.png)
