---
layout: post
title: "在SQL Server中将数据导出为XML和Json"
date: 2015-02-06
categories: blog
tags: [博客园迁移]
---

有时候需要一次性将SQL Server中的数据导出给其他部门的也许进行关联或分析，这种需求对于SSIS来说当然是非常简单，但很多时候仅仅需要一次性导出这些数据而建立一个SSIS包就显得小题大做，而SQL Server的导入导出工具其中BUG还是蛮多的，最简单的办法是BCP。

# 数据导出为XML

在SQL Server 2005之后提供了一个for xml子句在关系数据库中原生支持XML。通过该命令可以将二维关系结果集转换为XML，通过BCP就可以将数据存为XML了。

例如下面的数据：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-02-06-sql-server-xml-json/sql-server-xml-json-061209338748293.png)](//images0.cnblogs.com/blog/35368/201502/061209326248577.png)

我们可以通过如下BCP命令（注意不能有回车）将其导出为XML文件，并保存：
    
    
    BCP "SELECT TOP 30 [bom_no],[LEVEL] FROM [sqladmin].[dbo].[bom] FOR XML path,TYPE, ELEMENTS ,ROOT('RegionSales')" QUERYOUT "d:\temp\test.XML" -c -t -T -S localhost

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-02-06-sql-server-xml-json/sql-server-xml-json-061209344685407.png)](//images0.cnblogs.com/blog/35368/201502/061209341716850.png)

执行完成后查看Test.XML文件，如下图所示。可以看到文件格式非常清晰，很容易就可以导入到其他系统了。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-02-06-sql-server-xml-json/sql-server-xml-json-061209351404779.png)](//images0.cnblogs.com/blog/35368/201502/061209348901236.png)

# 数据导出为JSON

如果希望将SQL Server中数据导出为Json，虽然这种操作在应用程序里已经有非常成熟的方法，但SQL Server其实并没有原生支持这种方式（小道消息，下个版本会支持）。我推荐使用这篇帖子的方式：<http://jaminquimby.com/servers/95-sql/sql-2008/145-code-tsql-convert-query-to-json>来做。将该帖子所提供的存储过程建立完成后，使用如下BCP命令：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-02-06-sql-server-xml-json/sql-server-xml-json-061209366099793.png)](//images0.cnblogs.com/blog/35368/201502/061209355155593.png)

执行完成后，得到结果如下图：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-02-06-sql-server-xml-json/sql-server-xml-json-061209377968724.png)](//images0.cnblogs.com/blog/35368/201502/061209372345151.png)
