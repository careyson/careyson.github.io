---
layout: post
title: "强制SQL Server执行计划使用并行提升在复杂查询语句下的性能"
date: 2014-07-17
categories: blog
tags: [博客园迁移]
---

最近在给一个客户做调优的时候发现一个很有意思的现象，对于一个复杂查询（涉及12个表）建立必要的索引后，语句使用的IO急剧下降，但执行时间不降反升，由原来的8秒升到20秒。

通过观察执行计划，发现之前的执行计划在很多大表连接的部分使用了Hash Join，由于涉及的表中数据众多，因此查询优化器选择使用并行执行，速度较快。而我们优化完的执行计划由于索引的存在，且表内数据非常大，过滤条件的值在一个很宽的统计信息步长范围内，导致估计行数出现较大偏差（过滤条件实际为15000行，步长内估计的平均行数为800行左右），因此查询优化器选择了Loop Join，且没有选择并行执行，因此执行时间不降反升。

由于语句是在存储过程中实现，因此我们直接对该语句使用一个undocument查询提示，使得该查询的并行开销阈值强制降为0，使得该语句强制走并行，语句执行时间由20秒降为5秒\(注:使用Hash Join提示是7秒\)。

下面通过一个简单的例子展示使用该提示的效果，示例T-SQL如代码清单1所示：
    
    
    SELECT *  
    FROM [AdventureWorks].[Sales].[SalesOrderDetail] a   
    INNER JOIN [Sales].SalesOrderHeader b  
    ON a.SalesOrderID=b.SalesOrderID

  


代码清单1.

该语句默认不会走并行，执行计划如图1所示：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-07-17-sql-server/sql-server-171507100992011.png)](//images0.cnblogs.com/blog/35368/201407/171507083033827.png)

图1.

下面我们对该语句加上提示，如代码清单2所示。
    
    
    SELECT *  
      FROM [AdventureWorks].[Sales].[SalesOrderDetail] a   
      INNER JOIN [Sales].SalesOrderHeader b  
      ON a.SalesOrderID=b.SalesOrderID  
      OPTION(querytraceon 8649)

  


代码清单2.

此时执行计划会按照提示走并行，如图2所示：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-07-17-sql-server/sql-server-171507136159637.png)](//images0.cnblogs.com/blog/35368/201407/171507120068695.png)

图2.

在面对一些复杂的DSS或OLAP查询时遇到类似的情况，可以考虑使用该Undocument提示要求SQL Server尽可能的使用并行，从而降低执行时间。
