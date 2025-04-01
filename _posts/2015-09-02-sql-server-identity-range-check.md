---
layout: post
title: "SQL Server 合并复制遇到identity range check报错的解决"
date: 2015-09-02
categories: blog
tags: [博客园迁移]
---

最近帮一个客户搭建跨洋的合并复制，由于数据库非常大，跨洋网络条件不稳定，因此只能通过备份初始化，在初始化完成后向海外订阅端插入数据时发现报出如下错误：

Msg 548, Level 16, State 2, Line 2   
The insert failed. It conflicted with an identity range check constraint in database %s, replicated table %s, column %s. If the identity column is automatically managed by replication, update the range as follows: for the Publisher, execute sp\_adjustpublisheridentityrange; for the Subscriber, run the Distribution Agent or the Merge Agent.

## 原因？

在SQL Server中，对于自增列的定义是对于每一条新插入的行，都会自动按照顺序新生成一个递增的数字，改数字通常和业务无关且被用于作为主键。但如果该表用于可更新事务复制或者合并复制，那么该自增列的区间范围则由复制管理。

此时，复制可以保证自增列可控，因为复制代理插入行时不会导致自增列自增，只有用户显式插入时才会导致自增列自增。

让我们来做一个实验。首先创建表，表定义如下：
    
    
    CREATE TABLE [dbo].[Table_1](
    
    
        [c1] [int] IDENTITY(1,1),
    
    
        [c2] [int] NULL,
    
    
        [ROWGUID] [uniqueidentifier] NOT NULL,
    
    
        [rowguid4] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    
    
     CONSTRAINT [PK_Table_1] PRIMARY KEY CLUSTERED 
    
    
    (
    
    
        [c1] ASC
    
    
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
    
    
    ) ON [PRIMARY]

此时我们对创建合并复制，并把该表包含在内，并使用快照代理初始化复制，当完成该步骤时，我们发现该表上自动多了两个约束，如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-09-02-sql-server-identity-range-check/sql-server-identity-range-check-35368-20150902160913356-1296065027.png)](http://images2015.cnblogs.com/blog/35368/201509/35368-20150902160907825-1536154500.png)

图1.合并复制所加的约束 

我们看到该约束的定义只允许4002到5002以及5002到6002之间的数据被插入。

此时如果出现了一些BUG或者人为改动了该表自增列种子的值，则会报错，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-09-02-sql-server-identity-range-check/sql-server-identity-range-check-35368-20150902160915216-145061628.png)](http://images2015.cnblogs.com/blog/35368/201509/35368-20150902160914747-1068855426.png)

图2.改动种子值导致插入数据出错

该约束会由合并代理自动递增，比如说我们用如下代码插入2000条数据，则发现该约束会自动递增如图3所示。
    
    
    DECLARE @index INT=1
    
    
    WHILE @index<2000
    
    
    BEGIN
    
    
    INSERT INTO table_1(c2,ROWGUID) VALUES(2,NEWID())
    
    
    SET @index=@index+1
    
    
    END

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-09-02-sql-server-identity-range-check/sql-server-identity-range-check-35368-20150902160916544-167559663.png)](http://images2015.cnblogs.com/blog/35368/201509/35368-20150902160915935-1558294827.png)

图3.约束区间自动递增滑动

## 解决办法 

此时我已经找出了上面报错的原因，因为是由于从备份初始化，那么备份以及备份传输期间发布库又有新的数据插入，此时发布库比如说，该表的种子大小已经增加到了6000，而备份中该表大小还是5000，而约束已经滑动到了6000，那么在订阅端插入数据时就会发生这种问题。

### 解决办法1

在发布端使用sp\_adjustpublisheridentityrange 存储过程使得约束范围自动向后滑动，比如从6000-8000滑动到8000-10000。缺点自增值之间会有一个GAP。如果业务允许，推荐使用该做法。

sp\_adjustpublisheridentityrange @table\_name=’表名称‘

### 解决办法2

在发布端运行SELECT IDENT\_CURRENT\('表名称'\)，找到发布表的种子值。在订阅端通过DBCC CHECKIDENT \(表名称,RESEED, 设置为上面值\)命令将两端种子值设置为一致。

### 解决办法3

在订阅端运行合并代理，即可修复数据。如果此方法不行，则再次尝试上述方法。

### 解决办法4

不用自增列，而使用GUID列，但这涉及到表结构以及程序的修改，而且需要重新初始化复制，因此不是每一个环境都有条件这么做。

此时，就可以正常插入数据了。
