---
layout: post
title: "SQL Server中生成测试数据"
date: 2012-02-20
categories: blog
tags: [博客园迁移]
---

### 简介

在实际的开发过程中。很多情况下我们都需要在数据库中插入大量测试数据来对程序的功能进行测试。而生成的测试数据往往需要符合特定规则。虽然可以自己写一段程序来进行插入数据，但每一个项目就写一个插入数据的程序并不明智。本文主要介绍使用VS2010的数据生成计划在SQL Server中生成测试数据。

### 生成测试数据的方法

**1.手动编辑**

在开发过程中，非常少量的数据可以手动插入。这个方法的缺点可想而知….插入100条数据就够你忙乎一上午了。

**2.写程序 &T-SQL语句进行插入**

这个缺点也是显而易见的，开发效率同样底下。对于再次开发不同的程序时，程序需要修改或者重写。甚至对于每一个表就要写一段代码，并且生成的数据灵活性并不高！

比如对一个表生成1000条数据我可能就需要写这么多T-SQL:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-20-sql-server/sql-server-201202201430539189.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202201430529647.png)

可以看出，这种方法不仅麻烦，生成的测试数据也可能不符合我们需要的。

**3\. 使用已经上线的系统的数据**

嗯，这个方法貌似不错.简单容易，数据量足。但先抛开新系统或完全不同的系统表结构改变可能无法使用已经上线的数据这个因素之外。拿客户的商业数据进行测试..这个也太没节操了吧……

### 使用VS2010的数据生成计划来生成测试数据

VS2010提供的数据生成计划是一个强大的工具。它可以高效的生成测试数据，其中内置的数据生成规则可以很容易的让我们实现生成所需数据。下面来看一个实际的例子:

为了简便起见，所生成的数据的构架只有两个表\(员工表和部门表\),用外键连接:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-20-sql-server/sql-server-201202201430576238.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202201430579237.png)

在VS2010创建数据库项目，添加SQL Server 2008数据库项目,然后添加数据生成计划:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-20-sql-server/sql-server-201202201430581387.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202201430584353.png)

在VS2010中建立数据库连接，添加新项，在数据生成计划中，可以看到这两个表了:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-20-sql-server/sql-server-201202201430593994.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202201430597309.png)

通过指定列的属性，我可以调整我所生成的数据的规范:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-20-sql-server/sql-server-201202201431001029.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202201431002075.png)

下面，我为Employee表的几个列数据进行指定,Name列，我指定最小长度为4，最大长度为6.Gender列只允许有两个值，男和女.而Email按照正则表达式，生成符合Email地址规范的值:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-20-sql-server/sql-server-201202201431018063.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202201431017474.png)

性别列指定只有男和女

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-20-sql-server/sql-server-201202201431029558.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202201431012556.png)

邮件列指定邮件的正则表达式

在数据生成计划中，VS2010提供的强大功能还有外键约束生成数据。上面两个表中，假设公司有1000名员工，有10个部分，对应的每生成一个部门数据则生成100个员工数据，我可以在“相关表”和“相关表设置里进行”:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-20-sql-server/sql-server-201202201431034357.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202201431027115.png)

一切准备就绪后，我可以通过按F5生成数据:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-20-sql-server/sql-server-201202201431042264.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202201431037771.png)

在SSMS中查看数据:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-20-sql-server/sql-server-20120220143105968.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202201431043410.png)

可以看到，数据基本符合我所需要生成的数据
