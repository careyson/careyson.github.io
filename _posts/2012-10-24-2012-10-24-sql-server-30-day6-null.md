---
layout: post
title: "【译】SQL Server误区30日谈-Day6-有关NULL位图的三个误区"
date: 2012-10-24
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

NULL位图是为了确定行中的哪一列是NULL值，哪一列不是。这样做的目的是当Select语句后包含存在NULL值的列时，避免了存储引擎去读所有的行来查看是否是NULL，从而提升了性能。这样还能减少CPU缓存命中失效的问题\(点击这个[链接](http://en.wikipedia.org/wiki/MESI_protocol)来查看CPU的缓存是如何工作的以及MESI协议\)。下面让我们来揭穿三个有关NULL位图的普遍误区。

**误区 \#6a:NULL位图并不是任何时候都会用到**

正确

就算表中不存在允许NULL的列，NULL位图对于数据行来说会一直存在\(数据行指的是堆或是聚集索引的叶子节点\)。但对于索引行来说（所谓的索引行也就是聚集索引和非聚集索引的非叶子节点以及非聚集索引的叶子节点）NULL位图就不是一直有效了。

下面这条语句可以有效的证明这一点:
    
    
    CREATE TABLE NullTest (c1 INT NOT NULL);   
    CREATE NONCLUSTERED INDEX 
    NullTest_NC ON NullTest (c1);   
    GO   
    INSERT INTO NullTest VALUES (1); 
      
    GO
    
    
    
    
    EXEC sp_allocationMetadata 'NullTest';   
    GO

  


你可以通过我的博文:[Inside The Storage Engine: sp\_AllocationMetadata - putting undocumented system catalog views to work](http://www.sqlskills.com/blogs/paul/post/Inside-The-Storage-Engine-sp_AllocationMetadata-putting-undocumented-system-catalog-views-to-work.aspx).来获得sp\_allocationMetadata 的实现脚本。

让我们通过下面的script来分别查看在堆上的页和非聚集索引上的页:
    
    
    DBCC TRACEON (3604);   
    DBCC PAGE (foo, 1, 152, 3); -- page ID from SP output 
    where Index ID = 0   
    DBCC PAGE (foo, 1, 154, 1); -- page ID from SP output 
    where Index ID = 2   
    GO

  


首先让我们来看堆上这页Dump出来的结果
    
    
    Slot 0 Offset 0x60 Length 11
    
    
    
    
    Record Type = PRIMARY_RECORD Record Attributes = NULL_BITMAP   
    Memory Dump 
    @0x685DC060

  


再来看非聚集索引上的一页Dump出来的结果:
    
    
    Slot 0, Offset 0x60, Length 13, DumpStyle BYTE
    
    
    
    
    Record Type = INDEX_RECORD Record Attributes = <<<<<<< 
    **No null bitmap**   
    Memory Dump @0x685DC060

  


**误区 \#6b: NULL位图仅仅被用于可空列**

错误

__ 当NULL位图存在时，NULL位图会给记录中的每一列对应一位，但是数据库中最小的单位是字节，所以为了向上取整到字节，NULL位图的位数可能会比列数要多。对于这个问题.我已经有一篇博文对此进行概述，请看:[Misconceptions around null bitmap size](http://www.sqlskills.com/BLOGS/PAUL/post/Misconceptions-around-null-bitmap-size.aspx).

**误区 \#6c:给表中添加额外一列时会立即导致SQL Server对表中数据的修改**

错误

****

只有向表中新添加的列是带默认值，且默认值不是NULL时，才会立即导致SQL Server对数据条目进行修改。总之，SQL Server存储引擎会记录一个或多个新添加的列并没有反映在数据记录中。关于这点，我有一篇博文更加深入的对此进行了阐述:[Misconceptions around adding columns to a table](http://www.sqlskills.com/BLOGS/PAUL/post/Misconceptions-around-adding-columns-to-a-table.aspx).
