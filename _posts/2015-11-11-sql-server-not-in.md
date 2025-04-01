---
layout: post
title: "在SQL Server中为什么不建议使用Not In子查询"
date: 2015-11-11
categories: blog
tags: [博客园迁移]
---

在SQL Server中，子查询可以分为相关子查询和无关子查询，对于无关子查询来说，Not In子句比较常见，但Not In潜在会带来下面两种问题：

  * 结果不准确 
  * 查询性能低下 



下面我们来看一下为什么尽量不使用Not In子句。

### 结果不准确问题

在SQL Server中，Null值并不是一个值，而是表示特定含义，其所表示的含义是“Unknow”，可以理解为未定义或者未知，因此任何与Null值进行比对的二元操作符结果一定为Null，包括Null值本身。而在SQL Server中，Null值的含义转换为Bool类型的结果为False。让我们来看一个简单的例子，如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-11-11-sql-server-not-in/sql-server-not-in-35368-20151111063611619-1065964099.png)](http://images2015.cnblogs.com/blog/35368/201511/35368-20151111063611306-1805598654.png)

图1.Null值与任何值进行对比结果都为Null

SQL Server提供了“IS”操作符与Null值做对比，用于衡量某个值是否为Null。

那么Not In 的问题在哪呢，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-11-11-sql-server-not-in/sql-server-not-in-35368-20151111063612119-1218892393.png)](http://images2015.cnblogs.com/blog/35368/201511/35368-20151111063611884-851309083.png)

图2.Not In产生不准确的值

在图2中，条件3不属于Not In后面列表的任意一个，该查询却不返回任何值，与预期的结果不同，那么具体原因就是Not In子句对于Null值的处理，在SQL Server中，图2中所示的Not In子句其实可以等价转换为如图3所示的查询。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-11-11-sql-server-not-in/sql-server-not-in-35368-20151111063612837-9931551.png)](http://images2015.cnblogs.com/blog/35368/201511/35368-20151111063612400-1965282221.png)

图3.对于Not In子句来说，可以进行等价转换

在图3中可以看到Not In可以转换为条件对于每个值进行不等比对，并用逻辑与连接起来，而前面提到过Null值与任意其他值做比较时，结果永远为Null，在Where条件中也就是False，因此3<>null就会导致不返回任何行，导致Not In子句产生的结果在意料之外。

因此，Not In子句如果来自于某个表或者列表很长，其中大量值中即使存在一个Null值，也会导致最终结果不会返回任何数据。

#### 解决办法？

解决办法就是不使用Not In，而使用Not Exists作为替代。Exists的操作符不会返回Null，只会根据子查询中的每一行决定返回True或者False，当遇到Null值时，只会返回False，而不会由某个Null值导致整个子查询表达式为Null。对于图2中所示的查询，我们可以改写为子查询，如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-11-11-sql-server-not-in/sql-server-not-in-35368-20151111063613322-1679652101.png)](http://images2015.cnblogs.com/blog/35368/201511/35368-20151111063613072-1580418429.png)

图4.Not Exists可以正确返回结果

### Not In导致的查询性能低下

前面我们可以看出，Not In的主要问题是由于对Null值的处理问题所导致，那么对Null值的处理究竟为什么会导致性能问题？让我们来看图5的示例。图5中，我们使用了Adventurework示例数据库，并为了演示目的将SalesOrderDetail表的ProductId的定义由Not Null改为Null，此时我们进行一个简单的Not In查询。如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-11-11-sql-server-not-in/sql-server-not-in-35368-20151111063614697-833307101.png)](http://images2015.cnblogs.com/blog/35368/201511/35368-20151111063613681-25472666.png)

图5.Not In的执行计划

在图5中，我们看到一个Row Count Spool操作符，该操作符用于确认ProductId列中是否有Null值（过程是对比总行数和非Null行数，不想等则为有Null值，虽然我们知道该列中没有Null值，但由于列定义是允许Null的，因此SQL Server必须进行额外的确认），而该操作符占用了接近一半的查询成本。因此我们对比Not Exists，如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-11-11-sql-server-not-in/sql-server-not-in-35368-20151111063616040-706843799.png)](http://images2015.cnblogs.com/blog/35368/201511/35368-20151111063615556-477008434.png)

图6.Not In Vs Not Exists

由图6可以看出，Not In的执行成本几乎是Not Exists的3倍，仅仅是由于SQL Server需要确认允许Null列中是否存在Null。根据图3中Not In的等价形式，我们完全可以将Not In转换为等价的Not Exist形式，如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-11-11-sql-server-not-in/sql-server-not-in-35368-20151111063616478-1085919728.png)](http://images2015.cnblogs.com/blog/35368/201511/35368-20151111063616275-1992021121.png)

图7.Not In转换为Not Exists

我们来对比图7和其等价Not In查询的成本，如图8所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-11-11-sql-server-not-in/sql-server-not-in-35368-20151111063617244-1804436162.png)](http://images2015.cnblogs.com/blog/35368/201511/35368-20151111063616822-878832694.png)

图8.成本上完全等价

因此我们可以看到Not In需要额外的步骤处理Null值，上述情况是仅仅在SalesOrderDetail表中的ProductId列定义为允许Null，如果我们将SalesOrderHeader的SalesOrderID列也定义为允许Null时，会发现SQL Server还需要额外的成本确认该列上是否有Null值。如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-11-11-sql-server-not-in/sql-server-not-in-35368-20151111063618915-1837109002.png)](http://images2015.cnblogs.com/blog/35368/201511/35368-20151111063618103-1710679103.png)

图9.SQL Server通过加入Left Anti Semi Join操作符解决列允许Null的问题

此时Not In对应的等价Not Exist形式变为如代码清单1所示。
    
    
    SELECT  *
    
    
    FROM    Sales.SalesOrderHeader a
    
    
    WHERE   NOT EXISTS ( SELECT *
    
    
                         FROM   Sales.SalesOrderDetail b
    
    
                         WHERE  a.SalesOrderID = b.ProductID )
    
    
            AND NOT EXISTS ( ( SELECT   *
    
    
                               FROM     Sales.SalesOrderDetail b
    
    
                               WHERE    b.ProductID IS NULL
    
    
                             ) )
    
    
            AND NOT EXISTS ( SELECT 1
    
    
                             FROM   ( SELECT    *
    
    
                                      FROM      Sales.SalesOrderHeader
    
    
                                    ) AS c
    
    
                             WHERE  c.SalesOrderID IS NULL )

代码清单1.当连接列两列定义都允许Null时，Not In等价的Not Exists形式

此时我们简单对比Not In和Not Exists的IO情况，如图10所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-11-11-sql-server-not-in/sql-server-not-in-35368-20151111063619962-1554907732.png)](http://images2015.cnblogs.com/blog/35368/201511/35368-20151111063619244-1543757489.png)

图10.Not In吃掉很高的IO

### 小结

本文阐述了Not In 的实现原理以及所带来的数据不一致和性能问题，在写查询时，尽量避免使用Not In，而转换为本文提供的Not Exists等价形式，将会减少很多麻烦。
