---
layout: post
title: "SQL Server2012 T-SQL对分页的增强尝试"
date: 2012-03-09
categories: blog
tags: [博客园迁移]
---

### 简介

SQL Server 2012中在Order By子句之后新增了OFFSET和FETCH子句来限制输出的行数从而达到了分页效果。相比较SQL Server 2005/2008的ROW\_Number函数而言，使用OFFSET和FETCH不仅仅是从语法角度更加简单，并且拥有了更优的性能\(看到很多人下过这个结论，但我测试有所偏差，暂且保留意见\)。

MSDN上对于OFFSET和FETCH的详细描述可以在（<http://msdn.microsoft.com/en-us/library/ms188385%28v=SQL.110%29.aspx>）找到。

### OFFSET和FETCH

这两个关键字在MSDN原型使用方式如代码1所示。
    
    
    [ORDER](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ORDER&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) order_by_expression
        [ [COLLATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=COLLATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) collation_name ] 
        [ [ASC](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ASC&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) | [DESC](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DESC&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ] 
        [ ,...n ] 
    [ <offset_fetch> ]
    
    
    <offset_fetch> ::=
    { 
        OFFSET { integer_constant | offset_row_count_expression } { ROW | [ROWS](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ROWS&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) }
        [
          [FETCH](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=FETCH&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) { [FIRST](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=FIRST&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) | [NEXT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=NEXT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) } {integer_constant | fetch_row_count_expression } { ROW | [ROWS](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ROWS&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) } [ONLY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ONLY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
        ]
    }

  


代码1.OFFSET和FETCH在MSDN的原型

可以看到，OFFSET使用起来很简单，首先在OFFSET之后指定从哪条记录开始取。其中，取值的数可以是常量也可以是变量或者表达式。而Row和ROWS在这里是一个意思。

然后通过FETCH关键字指定取多少条记录。其中，FIRST和NEXT是同义词，和前面的ROW和ROWS一样，它们可以互相替换。同样，这里取的记录条数也可以是常量或者变量表达式。

下面通过一个例子来看OFFSET和FETCH的简单用法。首先创建测试数据，这里我就偷懒了，使用我[上篇文章](http://www.cnblogs.com/CareySon/archive/2012/03/09/2387475.html)的测试数据，创建表后插入100万条测试数据，这个表非常简单，一个自增的id字段和一个int类型的data字段，创建表的语句我就不贴了，插入测试数据的代码如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-09-sql-server2012-t-sql/sql-server2012-t-sql-201203091620364271.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203091620351056.png)

图1.插入测试数据

下面，我要取第500000到500100的数据，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-09-sql-server2012-t-sql/sql-server2012-t-sql-201203091620401857.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203091620388500.png)

图2.取50万到500100之间的数据

可以看到，使用OFFSET和FETCH关键字使分页变得如此简单。

### OFFSET…FETCH分页对性能的提升

OFFSET和FETCH语句不仅仅是语法糖，还能带来分页效率上的提升。下面我们通过一个例子进行比较SQL Server 2012和SQL Server 2005/2008不同分页方式的分页效率。我们同样取50万到500100之间的数据，性能对比如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-09-sql-server2012-t-sql/sql-server2012-t-sql-201203091621077655.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203091621024006.png)

图3.SQL Server 2012分页和SQL Server 05/08之间分页效率对比

但是，查询计划中我看到SQL Server2012中FETCH..NEXT却十分损耗性能。这和前面的测试结果严重不符，如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-09-sql-server2012-t-sql/sql-server2012-t-sql-201203091621349733.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203091621099409.png)

图4.两种方式的执行计划

通过对比扫描聚集索引这步，我发现对于估计执行行数存在严重偏差,如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-09-sql-server2012-t-sql/sql-server2012-t-sql-201203091626488982.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203091621363189.png)[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-09-sql-server2012-t-sql/sql-server2012-t-sql-201203091626521584.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203091626506242.png)

图5.存在偏差的执行计划

上图中，第一张图片是使用OFFSET…FETCH进行分页的。估计行数居然占到了500100，严重不符。这令我十分费解，暂时还没有找出原因，求各路大神指导….

### 总结

SQL Server 2012带来的分页效果十分强大，使得大大简化在SQL Server下的分页。对于性能的影响，由于出现了上述执行计划的偏差，暂且不下结论。待日后研究有了进展再来补上。
