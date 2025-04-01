---
layout: post
title: "SQL Server中使用Check约束提升性能"
date: 2015-02-16
categories: blog
tags: [博客园迁移]
---

在SQL Server中，SQL语句的执行是依赖查询优化器生成的执行计划，而执行计划的好坏直接关乎执行性能。

在查询优化器生成执行计划过程中，需要参考元数据来尽可能生成高效的执行计划，因此元数据越多，则执行计划更可能会高效。所谓需要参考的元数据主要包括：索引、表结构、统计信息等，但还有一些不是很被注意的元数据，其中包括本文阐述的Check约束。

查询优化器在生成执行计划之前有一个阶段叫做代数树优化，比如说下面这个简单查询：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-02-16-sql-server-check/sql-server-check-161617179083261.png)](//images0.cnblogs.com/blog/35368/201502/161617169558717.png)

图1.简单查询

查询优化器意识到1=2这个条件是永远不相等的，因此不需要返回任何数据，因此也就没有必要扫描表，从图1执行计划可以看出仅仅扫描常量后确定了1=2永远为false后，就可完成查询。

**那么Check约束呢**

Check约束可以确保一列或多列的值符合表达式的约束。在某些时候，Check约束也可以为优化器提供信息，从而优化性能，比如看图二的例子。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-02-16-sql-server-check/sql-server-check-161617190498344.png)](//images0.cnblogs.com/blog/35368/201502/161617184396931.png)

图2.有Check约束的列提升查询性能

图2是一个简单的例子，有时候在分区视图中应用Check约束也会提升性能，测试代码如下：
    
    
     
    
    
    CREATE TABLE [dbo].[Test2007](
    
    
        [ProductReviewID] [int] IDENTITY(1,1) NOT NULL,
    
    
        [ReviewDate] [datetime] NOT NULL
    
    
    ) ON [PRIMARY]
    
    
     
    
    
    GO
    
    
     
    
    
    ALTER TABLE [dbo].[Test2007]  WITH CHECK ADD  CONSTRAINT [CK_Test2007] CHECK  (([ReviewDate]>='2007-01-01' AND [ReviewDate]<='2007-12-31'))
    
    
    GO
    
    
     
    
    
    ALTER TABLE [dbo].[Test2007] CHECK CONSTRAINT [CK_Test2007]
    
    
    GO
    
    
     
    
    
     
    
    
    CREATE TABLE [dbo].[Test2008](
    
    
        [ProductReviewID] [int] IDENTITY(1,1) NOT NULL,
    
    
        [ReviewDate] [datetime] NOT NULL
    
    
    ) ON [PRIMARY]
    
    
     
    
    
    GO
    
    
     
    
    
    ALTER TABLE [dbo].[Test2008]  WITH CHECK ADD  CONSTRAINT [CK_Test2008] CHECK  (([ReviewDate]>='2008-01-01' AND [ProductReviewID]<='2008-12-31'))
    
    
    GO
    
    
     
    
    
    ALTER TABLE [dbo].[Test2008] CHECK CONSTRAINT [CK_Test2008]
    
    
    GO
    
    
     
    
    
    INSERT INTO [Test2008] values('2008-05-06')
    
    
    INSERT INTO [Test2007] VALUES('2007-05-06')
    
    
     
    
    
    CREATE VIEW testPartitionView
    
    
    AS
    
    
    SELECT * FROM Test2007
    
    
    UNION
    
    
    SELECT * FROM Test2008
    
    
     
    
    
    SELECT * FROM testPartitionView
    
    
    WHERE [ReviewDate]='2007-01-01'
    
    
     
    
    
     
    
    
    SELECT * FROM testPartitionView
    
    
    WHERE [ReviewDate]='2008-01-01'
    
    
     
    
    
     
    
    
    SELECT * FROM testPartitionView
    
    
    WHERE [ReviewDate]='2010-01-01'

代码清单1.

我们针对Test2007和Test2008两张表结构一模一样的表做了一个分区视图。并对日期列做了Check约束，限制每张表包含的数据都是特定一年内的数据。当我们对视图进行查询并给定不同的筛选条件时，可以看到结果如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-02-16-sql-server-check/sql-server-check-161617207367030.png)](//images0.cnblogs.com/blog/35368/201502/161617199081917.png)

图3.不同的条件产生不同的执行计划

由图3可以看出，当筛选条件为2007年时，自动只扫描2007年的表，2008年的表也是同样。而当查询范围超出了2007和2008年的Check约束后，查询优化器自动判定结果为空，因此不做任何IO操作，从而提升了性能。

**结论**

在Check约束条件为简单的情况下（指的是约束限制在单列且表达式中不包含函数），不仅可以约束数据完整性，在很多时候还能够提供给查询优化器信息从而提升性能。
