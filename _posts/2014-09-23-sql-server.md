---
layout: post
title: "找到SQL Server数据库历史增长信息"
date: 2014-09-23
categories: blog
tags: [博客园迁移]
---

很多时候，在我们规划SQL Server数据库的空间，或向存储方面要空间时，都需要估算所需申请数据库空间的大小，估计未来最简单的办法就是看过去的趋势，这通常也是最合理的方式。

通常来讲，一个运维良好的数据库都需要做定期基线（baseline），有了基线才会知道什么是正常。一个简单的例子例如，一些人的血压平常偏低，那么80的低压对他来说就是不正常了。但现实情况是大多数系统并没有采集基线的习惯，因此在需要规划空间想要看历史增长时，就没有过去精确的数据了。

一个解决办法就是通过查看历史备份的大小来看过去的数据增长趋势，数据库备份的时候不会备份整个文件，而只备份在FPS页中标记已经分配的页，可以出现数据库是20G，但备份只有3G的情况，因此数据库备份可以作为查看数据增长的依据。

数据库在每次备份时都会在msdb.dbo.backupset表中记录备份的相关信息，因此可以通过下述查看来聚合历史备份信息，从而对比数据库的增长：
    
    
    SELECT  
    [database_name] AS "Database",  
    DATEPART(month,[backup_start_date]) AS "Month",  
    AVG([backup_size]/1024/1024) AS "Backup Size MB"  
    FROM msdb.dbo.backupset  
    WHERE  
     [database_name] = N'Adventureworks2012'  
    AND [type] = 'D'  
    GROUP BY [database_name],DATEPART(mm,[backup_start_date]);

  


代码清单1.按月查看历史数据的增长

结果如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-09-23-sql-server/sql-server-231139365604725.png)](//images0.cnblogs.com/blog/35368/201409/231139355608553.png)

图1.历史数据的增长

其中，代码清单1中database\_name换成你需要查看的数据库名称即可。

注：SQL Server 2008之后引入了基于策略的管理，该策略会默认建立一个作业，如图2所示，该作业每天2点运行，会按照策略（历史记录保留天数，如图3所示）清理过期的历史记录。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-09-23-sql-server/sql-server-231139395602242.png)](//images0.cnblogs.com/blog/35368/201409/231139379204941.png)

图2.查看策略管理

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-09-23-sql-server/sql-server-231139436078944.png)](//images0.cnblogs.com/blog/35368/201409/231139414821329.png)

图3.历史记录保留天数，默认为0，既永不清理

该策略会对应建立一个作业（如图4所示）。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-09-23-sql-server/sql-server-231139457171790.png)](//images0.cnblogs.com/blog/35368/201409/231139442011761.png)

图4.清理历史记录的作业

如果该作业或人为建立的作业清除了msdb.dbo.backupset表中的数据，则代码清单1中的结果可能会受到一定影响。
