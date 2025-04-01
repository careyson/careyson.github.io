---
layout: post
title: "SQL Server中的执行引擎入门"
date: 2012-05-23
categories: blog
tags: [博客园迁移]
---

### 简介

当查询优化器\(Query Optimizer\)将T-SQL语句解析后并从执行计划中选择最低消耗的执行计划后，具体的执行就会交由执行引擎\(Execution Engine\)来进行执行。本文旨在分类讲述执行计划中每一种操作的相关信息。

### 数据访问操作

首先最基本的操作就是访问数据。这既可以通过直接访问表，也可以通过访问索引来进行。表内数据的组织方式分为堆\(Heap\)和B树，其中表中没有建立聚集索引时数据是通过堆进行组织的，这个是无序的，表中建立聚集索引后和非聚集索引的数据都是以B树方式进行组织，这种方式数据是有序存储的。通常来说，非聚集索引仅仅包含整个表的部分列，对于过滤索引，还仅仅包含部分行。

除去数据的组织方式不同外，访问数据也分为两种方式，扫描\(Scan\)和查找\(Seek\),扫描是扫描整个结构的所有数据，而查找只是查找整个结构中的部分数据。因此可以看出，由于堆是无序的，所以不可能在堆上面进行查找\(Seek\)操作,而相对于B树的有序，使得在B树中进行查找成为可能。当针对一个以堆组织的表进行数据访问时，就会进行堆扫描,如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232246581307.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232246579487.png)

图1.表扫描

可以看出，表扫描的图标很清晰的表明表扫描的性质，在一个无序组织表中从头到尾扫描一遍。

而对于B树结构的聚集索引和非聚集索引，同样可以进行扫描，通常来讲，为了获取索引表中的所有数据或是获得索引行树占了数据大多数使得扫描的成本小于查找时，会进行聚集索引扫描。如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247006093.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232246599256.png)

图2.聚集索引扫描

聚集索引扫描的图标也同样能够清晰的表明聚集索引扫描的性质，找到最左边的叶子节点后，依次扫描所有叶子节点,达到扫描整个结构的作用。当然对于非聚集索引也是同样的概念，如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247028370.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247011533.png)

图3.非聚集索引的扫描

而对于仅仅选择B树结构中的部分数据，索引查找\(Seek\)使得B树变得有意义。根据所查找的关键值，可以使得从仅仅从B树根部向下走单一路径，因此免去了扫描不必要页的消耗，图4是查询计划中的一个索引查找。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247051170.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247034334.png)

图4.聚集索引查找

索引查找的图标也是很传神的，可以看到图标那根线从根节点一路向下到叶子节点。也就是找到所求数据所在的页，不难看出，如果我们需要查找多条数据且分散在不同的页中，这个查找操作需要重复执行很多回，当这个次数大到一定程度时，SQL Server会选择消耗比较低的索引扫描而不是再去重复索引查找。对于非聚集索引查找，概念是一样的，就不再上图片了。

**书签查找\(Bookmark Lookup\)**

**** 你也许会想，假如非聚集索引可以快速的找到所求的数据，但遗憾的是，非聚集索引却不包含所有所求列时该怎么办？这时SQL Server会面临两个选择，直接访问基本表去获取数据或是在非聚集索引中找到数据后，再去基本表获得非聚集索引没有覆盖到的所求列。这个选择取决于所估计的行数等统计信息。查询分析器会选择消耗比较少的那个。

一个简单的书签查找如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247071462.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247067134.png)

图5.一个简单的书签查找

从图5可以看出，首先通过非聚集索引找到所求的行，但这个索引并不包含所有的列，因此还要额外去基本表中找到这些列，因此要进行键查找，如果基本表是以堆进行组织的，那么这个键查找\(Key Lookup\)就会变成RID查找\(RID Lookup\),键查找和RID查找统称为书签查找。

不过有时候索引查找所返回的行数过多导致书签查找的性能远不如直接进行扫描操作，因此SQL Server这时会选择扫描而不是书签查找。如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-2012052322471052.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247094329.png)

图6.StateProvinceID列有非聚集索引，但由于返回行数过多，分析器会选择扫描而不是书签查找 

这个估计是根据统计信息进行的，关于统计信息，可以看我之前的一篇博文：[浅谈SQL Server中统计对于查询的影响](http://www.cnblogs.com/CareySon/archive/2012/05/14/HowStatisticImpactQuery.html)

### 聚合操作\(Aggregation\)

聚合函数会导致聚合操作。聚合函数是将一个集合的数据按照某种规则汇总成1个数据，或基于分组按照规则汇总成多个数据的过程。一些聚合函数比如:avg,sum,min，另外还有distinct关键字都有可能导致两类聚合操作:流聚合\(Stream Aggregation\)和哈希聚合\(Hash Aggregation\)。

**流聚合\(Stream Aggregation\)**

流聚合需要再执行聚合函数之前，被聚合的数据集合是有序的，这个有序数据既可以通过执行计划中的Sort进行，也可以直接从聚集或是非聚集索引中直接获得有序数据，另外，没有Group by的聚合操作被成为标量聚合，这类操作一定是会执行流聚合。

比如，我们直接进行标量聚合，如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247137803.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247112952.png)

图7.流聚合

但对于加了Group by的子句，因为需要数据按照group by 后面的列有序，就需要Sort来保证排序。注意,Sort操作是占用内存的操作，当内存不足时还会去占用tempdb。SQL Server总是会在Sort操作和散列匹配中选择成本最低的。一个需要Sort的操作如图8所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247164126.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247149274.png)

图8.需要排序的流聚合

图8中排序操作按照ProductLine进行排序后，然后就根据各自的分组做聚合操作了。

**散列聚合\(Hash aggregation\)**

上面的流聚合适合比较少的数据，但是对于相对大一点的表。使用散列集合成本会比排序要低。散列集合通过在内存中建立散列表来实现聚合，因此无需对数据集合进行排序。内存中所建立的散列表以Group by后面的列作为键值，如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247209029.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247171453.png)   
图9.散列聚合

在内存中建立好散列表后，会按照group by后面的值作为键，然后依次处理集合中的每条数据，当键在散列表中不存在时，向散列表添加条目，当键已经在散列表中存在时，按照规则（规则是聚合函数，比如Sum,avg什么的）计算散列表中的值（Value）。

### 连接\(Join\)

当多表连接时\(书签查找，索引之间的连接都算\)，SQL Server会采用三类不同的连接方式:循环嵌套连接\(Nested Loops Join\),合并连接\(Merge Join\),散列连接\(Hash Join\)。这几种连接并不是哪种会比另一种更好，而是每种连接方式都会适应特定场景。

**循环嵌套连接\(Nested Loops Join\)**

由图10可以看到一个简单的循环嵌套连接。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-20120523224723858.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247218515.png)

图10.一个循环嵌套连接的实例

循环嵌套连接的图标同样十分传神，处在上面的外部输入\(Outer input\)，这里也就是聚集索引扫描。和处在下面的内部输入\(Inner Input\),这里也就是聚集索引查找。外部输入仅仅执行一次，根据外部输入满足Join条件的每一行，对内部输入进行查找。这里由于是290行，对于内部输入执行290次。

可以通过属性窗口看到.如图11所示：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247264432.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247246058.png)

图11.内部输入的执行次数

根据嵌套循环的原理不难看出，由于外部输入是扫描，内部输入是查找，当两个Join的表外部输入结果集比较小，而内部输入所查找的表非常大时，查询优化器更倾向于选择循环嵌套方式。

**合并连接\(Merge Join\)**

不同于循环嵌套的是，合并连接是从每个表仅仅执行一次访问。从这个原理来看，合并连接要比循环嵌套要快了不少。下面来看一个典型的合并连接，如图12所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247296610.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247282871.png)

图12.合并连接

从合并连接的原理不难想象，首先合并连接需要双方有序.并且要求Join的条件为等于号。因为两个输入条件已经有序，所以从每一个输入集合中取一行进行比较，相等的返回，不相等的舍弃，从这里也不难看出Merge join为什么只允许Join后面是等于号。从图11的图标中我们可以看出这个原理。

如果输入数据的双方无序，则查询分析器不会选择合并连接，我们也可以通过索引提示强制使用合并连接，为了达到这一目的，执行计划必须加上一个排序步骤来实现有序，如图13所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247324884.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/2012052322473133.png)

图13.通过排序来实现Merge Join

**散列连接\(Hash Join\)**

散列连接同样仅仅只需要只访问1次双方的数据。散列连接通过在内存中建立散列表实现。这比较消耗内存，如果内存不足还会占用tempdb。但并不像合并连接那样需要双方有序。一个典型的散列连接如图14所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247383144.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247344163.png)

图14.散列连接

这里我删除了Costomer的聚集索引，否则两个有序输入SQL Server会选择代价更低的合并连接。SQL Server利用两个上面的输入生成哈希表，下面的输入来探测，可以在属性窗口看到这些信息，如图15所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247471314.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247427698.png)

图15.散列键生成和散列键探测

通常来说，在两个输入数据比较大，且所求数据在其中一方或双方没有排序的条件达成时，会选用散列匹配。

**并行**

**** 当多个表连接时，SQL Server还允许在多CPU或多核的情况下允许查询并行，这样无疑提高了效率，一个并行的例子如图16所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-05-23-sql-server/sql-server-201205232247507429.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201205/201205232247498118.png)

图16.并行提高效率

### 总结

本文简单介绍了SQL Server执行计划中常见的操作极其原理，了解这些步骤和原理是优化查询的基本功。
