---
layout: post
title: "SQL Server中一个隐性的IO性能杀手-Forwarded record"
date: 2014-07-07
categories: blog
tags: [博客园迁移]
---

### 简介

最近在一个客户那里注意到一个计数器很高（Forwarded Records/Sec），伴随着间歇性的磁盘等待队列的波动。本篇文章分享什么是forwarded record，并从原理上谈一谈为什么Forwarded record会造成额外的IO。

### 存放原理

在SQL Server中，当数据是以堆的形式存放时，数据是无序的，所有非聚集索引的指针存放指向物理地址的RID。当数据行中的变长列增长使得原有页无法容纳下数据行时，数据将会移动到新的页中，并在原位置留下一个指向新页的指针，这么做的原因是由于使得当出现对Record的更新时，所有非聚集索引的指针不用变动。如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-07-07-sql-server-io-forwarded-record/sql-server-io-forwarded-record-070903253791235.png)](//images0.cnblogs.com/blog/35368/201407/070903207708959.png)

图1.Forwarded Record示意

这种由于数据更新，只在原有位置留下指针指向新数据页存放位置行，就是所谓的Forwarded Record。

### Forwarded Record如何影响IO性能？

那么Forwarded Record既然是为了提升性能存在的机制，为什么又会引起性能问题？Forwarded Record的初衷是为了对堆表进行更新时，堆表上存储位置的变化不会同时更新非聚集索引而产生开销。但对于查找来说，无论是堆表上存在表扫描，还是用于书签查找，都会成倍带来额外的IO开销，下面看一个例子。
    
    
    CREATE TABLE dbo.HeapTest ( id INT, col1 VARCHAR(800) )  
      
    DECLARE @index INT  
    SET @index = 0  
    BEGIN TRAN  
    WHILE @index < 100000   
        BEGIN   
            INSERT  INTO dbo.HeapTest  
                    ( id, col1 )  
            VALUES  ( @index, NULL )  
            SET @index = @index + 1  
      
        END  
    COMMIT

  


代码清单1.新建堆表并插入10万条数据

通过代码清单1创建测试表，并循环插入10万数据。此时我们来看该堆表所占用存储的页数，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-07-07-sql-server-io-forwarded-record/sql-server-io-forwarded-record-070903265517692.png)](//images0.cnblogs.com/blog/35368/201407/070903259737349.png)

图2.堆表空间占用

此时对该表进行更新，让原有行增长，产生Forwarded Record，此时再来看该堆表的存储。如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-07-07-sql-server-io-forwarded-record/sql-server-io-forwarded-record-070903280677721.png)](//images0.cnblogs.com/blog/35368/201407/070903274423364.png)

图3.产生8W+的forwarded record

此时我们注意到，虽然数据仅仅占到590页，但存在8W+的forwarded record，如果我们对该表进行扫描，则会看到虽然仅仅只有590页，但需要8W+的逻辑IO，大大提升了对IO的开销压力，此外由于forwarded record页与原页往往不物理连续，因此对IOPS也存在挑战。如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-07-07-sql-server-io-forwarded-record/sql-server-io-forwarded-record-070903291456151.png)](//images0.cnblogs.com/blog/35368/201407/070903285984051.png)

图4.不该产生的额外IO开销

而上面查询反映到性能计数器中，则呈现为如图5所示的结果。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-07-07-sql-server-io-forwarded-record/sql-server-io-forwarded-record-070903300821539.png)](//images0.cnblogs.com/blog/35368/201407/070903295206965.png)

图5.Forwarded Record计数器增长

### 如何解决

看到Forwarded Record计数器，就说明数据库中存在堆表，在OLTP系统中，所有的表上都应该有聚集索引。因此可以通过在表上增加聚集索引来解决该问题。

通常来讲，只有只写不读的表设置为堆表比较合适，但如果看到存在Forwarded Reocord，则说明堆表上存在读操作，那么找到该堆表，找一个合适的维护窗口时间创建聚集索引则是比较理想的选择。

如果由于其他原因无法创建聚集索引，则可以对堆表进行表重建。
