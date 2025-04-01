---
layout: post
title: "SQL Server中提前找到隐式转换提升性能的办法"
date: 2015-01-28
categories: blog
tags: [博客园迁移]
---

<http://www.cnblogs.com/shanksgao/p/4254942.html> 高兄这篇文章很好的谈论了由于数据隐式转换造成执行计划不准确，从而造成了死锁。那如果在事情出现之前发现了这类潜在的风险岂不是更好？

那么我们来看一个简单的例子，如代码清单1所示。
    
    
       1: SELECT    *
    
    
       2: FROM      HumanResources.Employee
    
    
       3: WHERE     NationalIDNumber = 243322160
    
    
       4:  
    
    
       5: SELECT    *
    
    
       6: FROM      HumanResources.Employee
    
    
       7: WHERE     NationalIDNumber = '243322160'

代码清单1. 

NationalIDNumber列定义是Nvarchar，而参数第一个为INT类型，第二个为Varchar类型。那么就存在隐式转换，由高继伟提到的数据类型转换优先级（<https://msdn.microsoft.com/zh-cn/library/ms190309.aspx>）可以看到，第一列Nvarchar和INT属性类型，INT数据类型优先级高，需要把列NationalIDNumber转换为INT类型，因此涉及到需要把所有该列值转换为INT，因此只能通过扫描操作，从而影响性能。

而代码清单1中第二个查询，NationalIDNumber列为Nvarchar类型，而参数为varchar类型，根据数据类型优先级，需要将Varchar转换为Navrchar，因此仅仅需要对参数进行隐式转换，因此不影响性能。

### 如何在出现问题之前找到出问题的查询？

在SQL Server中，执行计划会被缓存起来，以便后续进行复用。SQL Server提供了一系列DMV可以查看这些执行计划。由于执行计划的本质是XML，因此通过XQUERY查询特定的执行计划变为可能。

在执行计划中，存在隐式转换的节点会存在类似如代码清单2所示的字段： 
    
    
       1: <Convert DataType="int" Style="0" Implicit="true">
    
    
       2:                                   <ScalarOperator>
    
    
       3:                                     <Identifier>
    
    
       4:                                       <ColumnReference Database="[AdventureWorks2012]" Schema="[HumanResources]" Table="[Employee]" Column="NationalIDNumber" />
    
    
       5:                                     </Identifier>
    
    
       6:                                   </ScalarOperator>
    
    
       7:                                 </Convert>

代码清单2.对列进行转换的执行计划片段

前面提到，只有对列而不是参数进行隐式转换时，才会影响性能。而在代码清单2中对列进行隐式转换的执行计划会引用具体的数据库名称、架构名称、表名称、列名称。而对参数进行隐式转换的仅仅是引用参数，如代码清单3所示。
    
    
       1: <Convert DataType="nvarchar" Length="8000" Style="0" Implicit="true">
    
    
       2:                                     <ScalarOperator>
    
    
       3:                                       <Identifier>
    
    
       4:                                         <ColumnReference Column="@1" />
    
    
       5:                                       </Identifier>
    
    
       6:                                     </ScalarOperator>
    
    
       7:                                   </Convert>

代码清单3.对参数进行转换的执行计划片段 

既然我们已经知道产生问题的执行计划特征，那么我们就可以利用DMV和Xquery找出这些执行计划，代码如代码清单4所示：
    
    
       1: SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED
    
    
       2:  DECLARE @dbname SYSNAME
    
    
       3:  SET @dbname = QUOTENAME(DB_NAME());
    
    
       4:  WITH XMLNAMESPACES
    
    
       5:  (DEFAULT 'http://schemas.microsoft.com/sqlserver/2004/07/showplan')
    
    
       6:  SELECT stmt.value('(@StatementText)[1]', 'varchar(max)') AS SQL_Text ,
    
    
       7:         t.value('(ScalarOperator/Identifier/ColumnReference/@Schema)[1]',
    
    
       8:                 'varchar(128)') AS SchemaName ,
    
    
       9:         t.value('(ScalarOperator/Identifier/ColumnReference/@Table)[1]',
    
    
      10:                 'varchar(128)') AS TableName ,
    
    
      11:         t.value('(ScalarOperator/Identifier/ColumnReference/@Column)[1]',
    
    
      12:                 'varchar(128)') AS ColumnName ,
    
    
      13:         ic.DATA_TYPE AS ConvertFrom ,
    
    
      14:         ic.CHARACTER_MAXIMUM_LENGTH AS ConvertFromLength ,
    
    
      15:         t.value('(@DataType)[1]', 'varchar(128)') AS ConvertTo ,
    
    
      16:         t.value('(@Length)[1]', 'int') AS ConvertToLength ,
    
    
      17:         query_plan
    
    
      18:  FROM sys.dm_exec_cached_plans AS cp
    
    
      19:         CROSS APPLY sys.dm_exec_query_plan(plan_handle) AS qp
    
    
      20:         CROSS APPLY query_plan.nodes('/ShowPlanXML/BatchSequence/Batch/Statements/StmtSimple')
    
    
      21:         AS batch ( stmt )
    
    
      22:         CROSS APPLY stmt.nodes('.//Convert[@Implicit="1"]') AS n ( t )
    
    
      23:         JOIN INFORMATION_SCHEMA.COLUMNS AS ic ON QUOTENAME(ic.TABLE_SCHEMA) = t.value('(ScalarOperator/Identifier/ColumnReference/@Schema)[1]',
    
    
      24:                                                               'varchar(128)')
    
    
      25:                                                  AND QUOTENAME(ic.TABLE_NAME) = t.value('(ScalarOperator/Identifier/ColumnReference/@Table)[1]',
    
    
      26:                                                               'varchar(128)')
    
    
      27:                                                  AND ic.COLUMN_NAME = t.value('(ScalarOperator/Identifier/ColumnReference/@Column)[1]',
    
    
      28:                                                               'varchar(128)')
    
    
      29:  WHERE t.exist('ScalarOperator/Identifier/ColumnReference[@Database=sql:variable("@dbname")][@Schema!="[sys]"]') = 1

代码清单4.找出隐式转换的执行计划

对于本例的结果如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-01-28-sql-server/sql-server-281201015195190.png)](//images0.cnblogs.com/blog/35368/201501/281201006597762.png)

图1.找出隐式转换的结果

### 小结

本篇文章提供了通过执行计划缓存找出对性能影响的隐式转换，在出现问题之前进行调优。对于开发人员来讲，注意书写T-SQL的数据类型可以在后续避免很多问题。

注：由于代码清单4使用了XQuery，因此在执行计划缓存很大时，会比较慢。

参考资料：<http://sqlblog.com/blogs/jonathan_kehayias/archive/2010/01/08/finding-implicit-column-conversions-in-the-plan-cache.aspx>

<http://www.cnblogs.com/shanksgao/p/4254942.html>
