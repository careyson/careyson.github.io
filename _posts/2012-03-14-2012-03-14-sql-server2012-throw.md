---
layout: post
title: "SQL Server2012中的Throw语句尝试"
date: 2012-03-14
categories: blog
tags: [博客园迁移]
---

### 简介

SQL SERVER2012实现了类似C\#抛出异常的Throw语句。相比较于SQL Server2005之前使用@@ERROR,和SQL Server2005之后使用RAISERROR\(\)引发异常都是一个不小的进步，下面来看一下Throw的用法。

### RAISERROR和THROW比较

在SQL Server2005/2008中，使用RAISERROR和TRY…CATCH语句来抛出异常相比较根据@@ERROR进行判断来讲已经进步了很多。但是使用RAISERROR有一个非常不好的一点是无法返回真正出错的行数。如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-14-sql-server2012-throw/sql-server2012-throw-201203141201159798.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/20120314120111783.png)

图1.使用RAISERROR返回错误行数不正确

而如果我们需要具体的错误信息，可能还需要这么写，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-14-sql-server2012-throw/sql-server2012-throw-201203141201187582.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203141201177157.png)

图2.错误信息写法比较麻烦

而使用SQL SERVER2012新增的THROW语句，则变得简单很多。并且能正确返回出错的行，对于比较长的T-SQL语句来说，这节省了不少时间，如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-14-sql-server2012-throw/sql-server2012-throw-20120314120124891.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/20120314120119830.png)

图3.THROW正确返回出错行和出错信息

我们也可以为THROW语句指定参数来返回自定义错误信息，但不能再标识出正确的错误行，如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-14-sql-server2012-throw/sql-server2012-throw-201203141201277496.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203141201252428.png)

图4.为THROW语句指定参数

### 小结

因此使用THROW语句可以带来如下好处

1.更简洁优雅的代码

2.可以正确的标识出出错的行数，对于大量T-SQL来说，这点可以节省不少时间
