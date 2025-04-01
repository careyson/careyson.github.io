---
layout: post
title: "使用SQL Server Audit记录数据库变更"
date: 2015-01-05
categories: blog
tags: [博客园迁移]
---

最近工作中有一个需求，就是某一个比较重要的业务表经常被莫名其妙的变更。在SQL Server中这类工作如果不事前捕获记录的话，无法做到。对于捕获变更来说，可以考虑的选择包括Trace，CDC。但Trace的成本比较大，对于负载量较高的系统并不合适，而CDC需要影响业务库，因此SQL Server Audit就是一个比较好的选择。

 在SQL Server中，如果只是希望获得表的更新时间，只需要看表的聚集索引的最后更新时间即可，代码如下：

SELECT OBJECT\_NAME\(OBJECT\_ID\) AS DatabaseName, last\_user\_update,\*   
FROM sys.dm\_db\_index\_usage\_stats   
WHERE database\_id = DB\_ID\( 'DateBaseName'\)   
AND OBJECT\_ID=OBJECT\_ID\('TableName'\)

但这种方式并不能看到由某人在某个时间修改了某个表，在此使用Server Audit。Server Audit底层采用的是扩展事件，且存储结构可以以单独文件独立于用户库，因此不仅性能较好，也不会对用户库产生影响。

下面是启用审核的T-SQL代码：

USE master   
CREATE SERVER AUDIT audit1 TO FILE \(FILEPATH='D:\SQLAudit'\)   
USE AdventureWorks2012   
CREATE DATABASE AUDIT SPECIFICATION SerialPic FOR SERVER AUDIT audit1   
ADD\(UPDATE,INSERT,DELETE ON Person.Address by dbo\)

USE master   
CREATE SERVER AUDIT audit1 TO FILE \(FILEPATH='D:\SQLAudit'\)   
USE AdventureWorks2012   
CREATE DATABASE AUDIT SPECIFICATION SerialPic FOR SERVER AUDIT audit1   
ADD\(UPDATE,INSERT,DELETE ON Person.Address by dbo\)

上述代码首先创建服务器级别的审核，并存入D：\SQLAudit中，然后对应创建数据库级别的审核。在数据库级别的审核中，跟踪Person.Address表的Update，Insert，Delete操作。

接下来尝试修改数据库Person.Address，在安全-审核下查看审核日志，如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-01-05-sql-server-audit/sql-server-audit-051700132034534.png)](//images0.cnblogs.com/blog/35368/201501/051700122813150.png)

图1.查看审核日志

结果如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-01-05-sql-server-audit/sql-server-audit-051700144688047.png)](//images0.cnblogs.com/blog/35368/201501/051700137036447.png)

图2.数据库审核记录

这样就可以看到谁在什么时间曾经对该表做过哪些修改。当然除了UI方式，也可以通过T-SQL方式查看审核记录。

SELECT \* FROM   
fn\_get\_audit\_file\('D:\SQLAudit\audit1\_B8A7821A-D735-446D-B6FA-DF582AB80375\_0\_130648999540780000.sqlaudit', default, default\) 
