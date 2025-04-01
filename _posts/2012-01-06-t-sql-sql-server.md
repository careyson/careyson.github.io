---
layout: post
title: "T-SQL查询高级—SQL Server索引中的碎片和填充因子"
date: 2012-01-06
categories: blog
tags: [博客园迁移]
---

**** 写在前面:本篇文章需要你对[索引](http://www.cnblogs.com/CareySon/archive/2011/12/22/2297568.html)和SQL中数据的[存储方式](http://www.cnblogs.com/CareySon/archive/2011/12/26/2301597.html)有一定了解.标题中高级两个字仅仅是因为本篇文章需要我的T-SQL进阶系列文章的一些内容作为基础.

### **简介**

* * *

在SQL Server中，存储数据的最小单位是页，每一页所能容纳的数据为8060字节.而页的组织方式是通过B树结构（表上没有聚集索引则为堆结构，不在本文讨论之列\)如下图:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-201201060845428567.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845425012.png)

在聚集索引B树中，只有叶子节点实际存储数据，而其他根节点和中间节点仅仅用于存放查找叶子节点的数据.

每一个叶子节点为一页，每页是不可分割的. 而SQL Server向每个页内存储数据的最小单位是表的行\(Row\).当叶子节点中新插入的行或更新的行使得叶子节点无法容纳当前更新或者插入的行时，分页就产生了.在分页的过程中，就会产生碎片.

### **理解外部碎片**

* * *

首先，理解外部碎片的这个“外”是相对页面来说的。外部碎片指的是由于分页而产生的碎片.比如，我想在现有的聚集索引中插入一行，这行正好导致现有的页空间无法满足容纳新的行。从而导致了分页:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-201201060845435993.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/20120106084542486.png)

因为在SQL SERVER中，新的页是随着数据的增长不断产生的，而聚集索引要求行之间连续，所以很多情况下分页后和原来的页在磁盘上并不连续.

这就是所谓的外部碎片.

由于分页会导致数据在页之间的移动，所以如果插入更新等操作经常需要导致分页，则会大大提升IO消耗，造成性能下降.

而对于查找来说，在有特定搜索条件，比如where子句有很细的限制或者返回无序结果集时，外部碎片并不会对性能产生影响。但如果要返回扫描聚集索引而查找连续页面时,外部碎片就会产生性能上的影响.

在SQL Server中，比页更大的单位是区\(Extent\).一个区可以容纳8个页.区作为磁盘分配的物理单元.所以当页分割如果跨区后，需要多次切区。需要更多的扫描.因为读取连续数据时会不能预读，从而造成额外的[物理读](http://www.cnblogs.com/CareySon/archive/2011/12/23/2299127.html)，增加磁盘IO.

### **理解内部碎片**

* * *

和外部碎片一样，内部碎片的”内”也是相对页来说的.下面我们来看一个例子:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-201201060845446973.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845437006.png)

我们创建一个表，这个表每个行由int\(4字节\),char\(999字节\)和varchar\(0字节组成），所以每行为1003个字节,则8行占用空间1003\*8=8024字节加上一些内部开销，可以容纳在一个页面中:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-20120106084545778.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845443319.png)

当我们随意更新某行中的col3字段后，造成页内无法容纳下新的数据，从而造成分页:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-201201060845463710.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845453220.png)

分页后的示意图:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-201201060845465596.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845463677.png)

而当分页时如果新的页和当前页物理上不连续，则还会造成外部碎片

### **内部碎片和外部碎片对于查询性能的影响**

* * *

外部碎片对于性能的影响上面说过，主要是在于需要进行更多的跨区扫描，从而造成更多的IO操作.

而内部碎片会造成数据行分布在更多的页中，从而加重了扫描的页树，也会降低查询性能.

下面通过一个例子看一下,我们人为的为刚才那个表插入一些数据造成内部碎片:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-201201060845476610.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845479151.png)

通过查看碎片，我们发现这时碎片已经达到了一个比较高的程度:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-201201060845487416.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845479401.png)

通过查看对碎片整理之前和之后的IO，我们可以看出，IO大大下降了:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-20120106084548382.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845482923.png)

### **对于碎片的解决办法**

* * *

基本上所有解决办法都是基于对索引的重建和整理，只是方式不同

1.删除索引并重建

这种方式并不好.在删除索引期间，索引不可用.会导致阻塞发生。而对于删除聚集索引，则会导致对应的非聚集索引重建两次\(删除时重建，建立时再重建\).虽然这种方法并不好，但是对于索引的整理最为有效

2.使用DROP\_EXISTING语句重建索引

为了避免重建两次索引，使用DROP\_EXISTING语句重建索引，因为这个语句是原子性的，不会导致非聚集索引重建两次，但同样的，这种方式也会造成阻塞

3.如前面文章所示，使用ALTER INDEX REBUILD语句重建索引

使用这个语句同样也是重建索引，但是通过动态重建索引而不需要卸载并重建索引.是优于前两种方法的，但依旧会造成阻塞。可以通过ONLINE关键字减少锁，但会造成重建时间加长.

4.使用ALTER INDEX REORGANIZE

这种方式不会重建索引，也不会生成新的页，仅仅是整理，当遇到加锁的页时跳过，所以不会造成阻塞。但同时，整理效果会差于前三种.

### **理解填充因子**

* * *

重建索引固然可以解决碎片的问题.但是重建索引的代价不仅仅是麻烦，还会造成阻塞。影响使用.而对于数据比较少的情况下，重建索引代价并不大。而当索引本身超过百兆的时候。重建索引的时间将会很让人蛋疼.

填充因子的作用正是如此。对于默认值来说，填充因子为0（0和100表示的是一个概念）,则表示页面可以100%使用。所以会遇到前面update或insert时，空间不足导致分页.通过设置填充因子，可以设置页面的使用程度:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-201201060845492267.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845492300.png)

下面来看一个例子:

还是上面那个表.我插入31条数据，则占4页:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-20120106084550217.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845502758.png)

通过设置填充因子，页被设置到了5页上:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-201201060845513706.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/20120106084550707.png)

这时我再插入一页，不会造成分页:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-201201060845526430.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845518656.png)

上面的概念可以如下图来解释:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-06-t-sql-sql-server/t-sql-sql-server-201201060845531032.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201060845523573.png)

可以看出，使用填充因子会减少更新或者插入时的分页次数，但由于需要更多的页，则会对应的损失查找性能.

### **如何设置填充因子的值**

* * *

如何设置填充因子的值并没有一个公式或者理念可以准确的设置。使用填充因子虽然可以减少更新或者插入时的分页，但同时因为需要更多的页，所以降低了查询的性能和占用更多的磁盘空间.如何设置这个值进行trade-off需要根据具体的情况来看.

具体情况要根据对于表的读写比例来看,我这里给出我认为比较合适的值:

1.当读写比例大于100：1时，不要设置填充因子，100%填充

2.当写的次数大于读的次数时，设置50%-70%填充

3.当读写比例位于两者之间时80%-90%填充

上面的数据仅仅是我的看法，具体设置的数据还要根据具体情况进行测试才能找到最优.

### **总结**

* * *

本文讲述了SQL SERVER中碎片产生的原理，内部碎片和外部碎片的概念。以及解决碎片的办法和填充因子.在数据库中，往往每一个对于某一方面性能增加的功能也会伴随着另一方面性能的减弱。系统的学习数据库知识，从而根据具体情况进行权衡，是dba和开发人员的必修课.
