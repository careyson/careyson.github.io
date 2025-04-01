---
layout: post
title: "【译】SQL Server误区30日谈-Day13-在SQL Server 2000兼容模式下不能使用DMV"
date: 2012-10-31
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

**误区 \#13.在SQL Server 2000兼容模式下不能使用DMV**

错误

****

**** 对于兼容模式已经存在了很多误解。80的兼容模式的数据库是否意味着能够附加或恢复到SQL Server 2000数据库?当然不是。这只是意味着一些T-SQL的语法，查询计划的行为以及一些其它方面和SQL Server 2000中行为一样（当然，如果你设置成90兼容模式则和SQL Server 2005中一样）。

在SQL Server 2008中，你可以使用ALTER DATABASE SET COMPATIBILITY\_LEVEL命令来改变兼容模式,对于SQL Server 2008之前的版本，则使用系统存储过程sp\_dbcmptlevel\(译者注：比如sp\_dbcmptlevel @dbname='AdventureWorks',@new\_cmptlevel=100\)，对于这两种方式如何用，请看:

  * 对于SQL Server 2008,BOL入口[ALTER DATABASE Compatibility Level](http://msdn.microsoft.com/en-us/library/bb510680.aspx)
  * 对于SQL Server 2005,BOL入口[sp\_dbcmptlevel \(Transact-SQL\)](http://msdn.microsoft.com/en-us/library/ms178653\(SQL.90\).aspx). 



兼容模式对于数据库的实际版本毫无影响,数据库的实际版本会随着对于数据库的升级而升级，这个升级会阻止更新版本的数据库恢复或附加到之前的数据库,因为之前版本的实例无法理解新版本数据库的版本。如果想看详细内容，请看我的一篇博文:[Search Engine Q&A \#13: Difference between database version and database compatibility level](http://www.sqlskills.com/BLOGS/PAUL/post/Search-Engine-QA-13-Difference-between-database-version-and-database-compatibility-level.aspx).还有如果当你附加新版数据库到老版本实例时所遇到的错误信息:[Msg 602, Level 21, State 50, Line 1](http://www.sqlskills.com/BLOGS/PAUL/post/Msg-602-Level-21-State-50-Line-1.aspx)。

在SQL Server 2005中设置为80兼容模式，貌似DMV就不能用了，运行下面代码创建测试数据库:

CREATE DATABASE DMVTest;   
GO   
USE DMVTest;   
GO   
CREATE TABLE t1 \(c1 INT\);   
CREATE CLUSTERED INDEX t1c1 on t1 \(c1\);   
INSERT INTO t1 VALUES \(1\);   
GO

EXEC sp\_dbcmptlevel DMVTest, 80;   
GO

SELECT \* FROM sys.dm\_db\_index\_physical\_stats \(   
DB\_ID \('DMVTest'\), -- database ID   
OBJECT\_ID \('t1'\), -- object ID **< <<<<< Note I'm using 1-part naming**   
NULL, -- index ID   
NULL, -- partition ID   
'DETAILED'\); -- scan mode   
GO

你会得到如下报错信息:

消息 102，级别 15，状态 1，第 3 行   
'\(' 附近有语法错误。   


看上去这足以证明80兼容模式不支持DMV。但其实并不是那样。

编者:写到这里之后，我突然意识到我陷入了一个悖论。DMV在80兼容模式下是完全支持的，但不支持的是在80兼容模式下调用函数作为DMV的参数。

下面是一个可以在80兼容模式下使用函数作为DMV参数的技巧，不得不说是神来之笔。那就是在一个90以上兼容模式的数据库下额外调用80兼容模式下的数据库，看下面代码:

USE master   
SELECT \* FROM sys.dm\_db\_index\_physical\_stats \(   
DB\_ID \('DMVTest'\), -- database ID   
OBJECT\_ID \('DMVTest..t1'\), -- object ID <<<<<< Note I'm using 3-part naming here now   
NULL, -- index ID   
NULL, -- partition ID   
'DETAILED'\); -- scan mode   
GO   


虽然DMVTest数据库工作在80兼容模式下，但上述代码依然可用。

但是有一点值得注意的是,你一定要保证Object参数的正确,如果你仅仅让第二个参数还是OBJECT\_ID \('t1'\), 那么这个函数会尝试在Master数据库中找表t1,正常来说这就会返回NULL，这就导致刚才那个DMV以NULL作为参数，从而返回了所有DMVTest表下的索引状态.而如果Master表中也有一个DMV，那就更不幸了，你将得到错误的信息。

还有，sys.dm\_db\_index\_physical\_stats并不算是一个真正的DMV，而是一个在后台处理大量信息后返回相关信息的DMF，因此如果你以NULL作为参数返回所有的索引信息的话，那代价会非常高昂，你可以看我最近的博文[Inside sys.dm\_db\_index\_physical\_stats](http://www.sqlskills.com/BLOGS/PAUL/post/Inside-sysdm_db_index_physical_stats.aspx)，这篇文章会对细节和代价进行详细的解释。

还有一种在80兼容模式下使用DMV的方式是不再DMV中以函数作为参数，而是传变量进去，代码如下:

DECLARE @databaseID INT;   
DECLARE @objectID INT; 

SELECT @databaseID = DB\_ID \('DMVTest'\);   
SELECT @objectID = OBJECT\_ID \('t1'\); 

SELECT \* FROM sys.dm\_db\_index\_physical\_stats \(   
@dbid, -- database ID   
@objid, -- object ID   
NULL, -- index ID   
NULL, -- partition ID   
'DETAILED'\); -- scan mode   
GO

嗯，又揭示了一个误区。****
