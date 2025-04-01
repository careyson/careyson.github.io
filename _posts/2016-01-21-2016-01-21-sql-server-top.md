---
layout: post
title: "SQL Server中TOP子句可能导致的问题以及解决办法"
date: 2016-01-21
categories: blog
tags: [博客园迁移]
---

## 简介

在SQL Server中，针对复杂查询使用TOP子句可能会出现对性能的影响，这种影响可能是好的影响，也可能是坏的影响，针对不同的情况有不同的可能性。

关系数据库中SQL语句只是一个抽象的概念，不包含任何实现。很多元数据都会影响执行计划的生成，SQL语句本身并不作为生成执行计划所参考的元数据（提示除外），但TOP关键字却是直接影响执行计划的一个关键字，因此在某些情况下使用TOP会导致性能受到影响，下面我们来看集中不同的情况。

### 单表情况

对于单表查询（这里的所说的单表指的是不包含视图、表值函数的物理单表）来说，存在TOP基本不会对性能产生影响，如果在SQL Server中加入了TOP，那么TOP本身可以看作是一个查询提示，意味着告诉优化器“返回结果只有N行”。我们看一个简单的例子，如图1所示：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-01-21-sql-server-top/sql-server-top-35368-20160121170932422-1418223319.png)](http://images2015.cnblogs.com/blog/35368/201601/35368-20160121170931656-1044696218.png)

图1.指定TOP关键字的单表执行计划

由图1执行计划对比可以看出，对于有索引支撑的单表查询来说，使用TOP子句往往可以提升性能，此时TOP N的行数的N则提示查询优化器该查询返回N行，而不是使用统计信息中的数据分布，此时TOP N对于查询优化器来说是合理的。

但有些时候Grant Memory（每次执行计划生成时会预估所需的内存，如果预估内存小于执行内存，则会spill to tempdb，对性能产生非常大的影响，由于每一个版本预估内存的公式变化极大，因此不在此详细解释了）不准会产生非常高的性能影响。在开始谈这点，之前，我们先谈两个操作符：

#### Sort

Sort操作符是非常通用的排序操作符，在执行计划中可能会出现在多个地方，比如Merge Join之前，由于Order By导致的等。该算法非常通用，可以对非常大的结果集进行排序，该操作符是阻塞式（意味着排序结束之前数据无法流动到下一个操作符），并且需要大量内存和CPU资源。该操作符还有一个问题是当Grant Memory不足时，需要TempDB辅助完成排序，因此有极大的性能开销。

#### Top N Sort

TOP N Sort是适应小场景，专门针对少量查询的排序算法。对于只选择几条数据来说，对于整个结果集进行排序成本过于高昂，因此TOP N的算法是首先取第一条数据，与其他数据进行对比，看是否最大（或最小），再取第二条数据对比，依次类推，直到找到前N条数据。该算法如果行数较小，则相比SORT操作符性能提升明显，但如果N值过大，则由于下述原因该算法不合适：

1.该算法不支持spill to tempdb，导致无法承载太大的结果集。

2.该算法需要遍历N次，如果N过大，则成本过高。

对于SQL Server来说，这个N是否过大的阈值是100。下面我们来看一个例子，测试数据和代码如代码清单1所示。
    
    
    CREATE TABLE TestTop
    
    
    (id INT,sortkey INT,SOMEvalue CHAR(1000))
    
    
     
    
    
      DECLARE @i INT =1
    
    
      WHILE @i<300000
    
    
      BEGIN
    
    
      INSERT INTO TestTop VALUES(@i,@i,'a')
    
    
      SET @i=@i+1
    
    
      END
    
    
      
    
    
      CREATE CLUSTERED INDEX PK_id ON TestTop(id)
    
    
      --test 1
    
    
      SELECT TOP(100) * FROM TestTop
    
    
      ORDER BY sortkey
    
    
      --test 2
    
    
      SELECT TOP(101) * FROM TestTop
    
    
      ORDER BY sortkey

代码清单1.测试数据与测试代码

第一个测试为TOP 100，正好使用TOP N Sort的算法，第二个测试为TOP 101，只能使用普通Sort的算法，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-01-21-sql-server-top/sql-server-top-35368-20160121170933578-1821077673.png)](http://images2015.cnblogs.com/blog/35368/201601/35368-20160121170933015-670903037.png)

图2.TOP 101的SORT需要更多内存，从而导致内存授予不足spill to tempdb

我们再来看执行时间，由于spill to tempdb的存在，那么执行时间如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-01-21-sql-server-top/sql-server-top-35368-20160121170934422-438710374.png)](http://images2015.cnblogs.com/blog/35368/201601/35368-20160121170934093-1983663541.png)

图3.相差非常大的执行时间

从图3可以看出，执行时间相差非常大。

**因此对于TOP的使用来说，尽量使用TOP 100以内的数值。**

### 多表情况

由于TOP语句带有对优化器基数估计的提示功能，因此多表查询时在极端情况下可能导致行数低估从而影响性能。

比如下面如图4的示例查询

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-01-21-sql-server-top/sql-server-top-35368-20160121170937297-62736609.png)](http://images2015.cnblogs.com/blog/35368/201601/35368-20160121170935484-304542014.png)

图4.使用TOP 1的表接连查询

在这种情况下，由于TOP1的存在使得查询优化器使用1作为估计行数，与实际的行数差异巨大，因此对于这种情况，使用TOP反而可能导致成本更高（虽然我们看到图4中估计的是0%对比100%，但实际差异巨大），更高的原因不仅仅是优化器估计为1，因为Loop Join只要发现1条就可以立刻结束，但上面例子中由于过滤条件选择性过低，导致找到第一条数据的随机查找过多（loop join内表循环是随机IO），成本如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-01-21-sql-server-top/sql-server-top-35368-20160121170938390-330666600.png)](http://images2015.cnblogs.com/blog/35368/201601/35368-20160121170937984-1429225524.png)

图5.使用TOP反而导致性能下降

根本原因是由于估计行数只有1行，大部分情况下这一行

对于上面这种情况来说，我们通常可以有下面集中解决办法：

1.使用提示，由于我们知道这是由于实际行数远大于估计行数导致，因此我们可以尝试使用hash join,forcescan等提示。

2.增加where条件，使得返回行数具有更高的选择性。

3.不使用TOP1，而使用TOP 10以上的数字，让估计行数变大，比如图5中的查询我们由TOP1 变为TOP10，那么执行计划则变为如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-01-21-sql-server-top/sql-server-top-35368-20160121170939875-1057340729.png)](http://images2015.cnblogs.com/blog/35368/201601/35368-20160121170938797-25864305.png)

图6.TOP 10的执行计划

这是由于当行数少时，LOOP JOIN可以更快返回有限的行数，相当于对表加了FAST N提示，但行数增多时，优化器更倾向使用MERGE或者HASH完成操作，在上面返回行极多（选择性低）的极端情况下，会拥有更好的性能，结果如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-01-21-sql-server-top/sql-server-top-35368-20160121170940750-802179184.png)](http://images2015.cnblogs.com/blog/35368/201601/35368-20160121170940359-1963305624.png)

图7.特殊情况下TOP10相比TOP1有更好性能。

**因此结合单表的例子，推荐使用TOP关键字时，数字在10到100之间。**

## 小结

本文介绍了TOP关键字在单表和多表条件下可能对执行计划产生的影响，进而影响了查询计划。TOP影响执行计划主要是下面两个方面：

  * 内存授予 
  * 估计行数 



因此在特殊情况下调优TOP语句时，可以根据实际情况考虑本文的建议。
