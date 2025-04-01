---
layout: post
title: "SQL Server中灾难时备份结尾日志(Tail of log)的两种方法"
date: 2012-02-23
categories: blog
tags: [博客园迁移]
---

### 简介

在数据库数据文件因各种原因发生损坏时，如果日志文件没有损坏。可以通过备份结尾日志（Tail of log\)使得数据库可以恢复到灾难发生时的状态。

例如:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-23-sql-server-tail-of-log/sql-server-tail-of-log-201202231537293720.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202231536417693.gif)

上图中。在DB\_1中做了完整备份，在Log\_1,Log\_2处做了日志备份。在Log\_2备份之后不久，发生了故障。从Log\_2备份到灾难发生时之间的日志。就是结尾日志\(Tail of log\)。如果不能备份尾端日志，则数据库只能恢复到Log\_2备份的点。尾端日志期间所做的改动全部丢失。更详细的概念可以查看我之前关于[日志](http://www.cnblogs.com/CareySon/archive/2012/02/23/2364572.html)的博文。

下面我们分别来看在SQL Server实例运行良好和SQL Server实例崩溃状态下，备份结尾日志方法。

### 

### SQL Server实例运行正常时，结尾日志的备份

下面来模拟一次灾难下结尾日志的备份:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-23-sql-server-tail-of-log/sql-server-tail-of-log-201202231538246414.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202231537349746.png)

现在数据库TestBackUp有了一个完整备份和一个日志备份，而最后那条”日志备份后的测试数据”是在上次日志备份之后的，被结尾日志所包含。

接下来模拟数据库文件所在磁盘损坏（日志文件完好）

1.停掉Server SQL服务

2.删除数据库文件\(MDF文件\)

此时在SSMS中访问数据库TestBackUp会出现不可用:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-23-sql-server-tail-of-log/sql-server-tail-of-log-201202231538305264.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202231538261822.png)

此时，因为SQL Server实例可用，通过在T-SQL语句指定NO\_TRUNCATE选项（必须指定，否则无法备份尾端日志），备份尾端日志:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-23-sql-server-tail-of-log/sql-server-tail-of-log-201202231538344867.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202231538326636.png)

依次进行完整备份恢复，和两次事务日志恢复，可以看到数据已经成功恢复到灾难点:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-23-sql-server-tail-of-log/sql-server-tail-of-log-201202231538405320.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/20120223153835242.png)

### 当SQL Server实例崩溃时，结尾日志的备份

此时由于各种原因，所处的SQL Server实例也崩溃，无法通过T-SQL来备份结尾日志。此时数据库文件损坏，而事务日志文件保持正确。

假设情况和上面例子一样，此时我手里有一个完整备份\(TestBackUp\_FULL.bak\)和一个日志备份\(TestBackUp\_log1.bak\),还有一个日志文件\(ldf\)。

这时我将这几个文件拷贝到其他拥有SQL Server实例的机器上。

新建一个和原数据库名一样的数据库。设置为脱机:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-23-sql-server-tail-of-log/sql-server-tail-of-log-201202231538442349.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202231538409714.png)

删除新建数据库的MDF文件。

将需要备份的数据库的日志文件替换掉原有的LDF文件。

此时直接备份结尾日志，成功:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-23-sql-server-tail-of-log/sql-server-tail-of-log-201202231539011090.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202231539006271.png)

原有Sql server实例恢复后一次恢复完整备份和两个日志备份。成功恢复到灾难发生点。

### 总结

我相信看到这篇文章的人都不希望碰到用到上面两种方法的情况。但是，墨菲定律（事情如果有变坏的可能，无论这种可能性有多小，它总会发生）是残酷的，事先练习一下总是比真正遇到情况用生产数据练习惬意的多：-）
