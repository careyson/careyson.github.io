---
layout: post
title: "SQL Server 2012中的Contained Database尝试"
date: 2012-03-13
categories: blog
tags: [博客园迁移]
---

### 简介

SQL Server 2012新增的Contained Database是为了解决数据库在不同SQL Server实例之间迁移的问题。在以往的情况下，数据库本身并不包含一些实例级别的配置参数（比如:数据库的一些metadata和登录名之类的）将数据库从一台服务器迁移到另一台服务器使用备份和恢复\(或分离和附加\)使得需要额外工作来设置这些数据库实例级别的metadata,而使用Contained Database,可以将这类信息包含在数据库中，从而大大减少这类工作的工作量。

下面我们从配置Contained Database开始。

### 配置Contained Database

在开始使用Contained Database之前，首先要通过Sp\_config或SSMS来配置实例级别的参数开启Contained Database.如代码1和图1所示。
    
    
    --开启允许配置Contained database
    [sp_configure](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=sp_configure&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 'show advanced options',1 [reconfigure](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=reconfigure&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    [go](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=go&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 
    [sp_configure](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=sp_configure&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 'contained database authentication',1 [reconfigure](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=reconfigure&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 
    [go](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=go&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)

  


代码1.通过sp\_configure开启Contained Database

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-13-sql-server-2012-contained-database/sql-server-2012-contained-database-201203131343307028.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/20120313134311612.png)

图1.通过SSMS开启Contained Database

在实例级别开启允许使用Contained Database后，通过对希望变为Contained Database的数据库在SSMS中进行设置。如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-13-sql-server-2012-contained-database/sql-server-2012-contained-database-201203131343475178.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203131343457918.png)

图2.Contained Database在数据库级别的设置

下面我们在数据库级别设置用户,如图3所示.

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-13-sql-server-2012-contained-database/sql-server-2012-contained-database-201203131343524334.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203131343499648.png)

图3.在数据库级别添加用户

同时我们为用户在成员身份中指定到db\_owner组。现在，我们就能通过SSMS连接到这个Contained Database了。如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-13-sql-server-2012-contained-database/sql-server-2012-contained-database-201203131344001873.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203131343549402.png)

图4.使用刚刚在数据库级别创建的用户进行登录

用我们刚刚创建的用户登录，在选项中指定连接数据库为刚才设置为Contained Database的数据库，如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-13-sql-server-2012-contained-database/sql-server-2012-contained-database-201203131344058836.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203131344039034.png)

图5.指定设置为Contained Database的数据库（Test数据库）

连接成功后，我们可以看到，作为数据库级别设置的用户，是无法访问实例中的其它数据库的。而在图6中我们可以看到，实例不不包含刚刚创建的登录名的，而是包含在数据库级别。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-13-sql-server-2012-contained-database/sql-server-2012-contained-database-201203131344136549.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203131344091995.png)

图6.两种连接方式对比

### 备份和恢复Contained Database

当然，Contained Database最大的作用是在备份和恢复时的便利性。下面，我们将刚才的Contained Database进行备份，然后在另一个实例中进行恢复。如图7和图8所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-13-sql-server-2012-contained-database/sql-server-2012-contained-database-201203131344197907.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203131344142829.png)

图7.备份数据库

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-13-sql-server-2012-contained-database/sql-server-2012-contained-database-201203131344268194.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203131344205790.png)

图8.在另一个实例中恢复数据库

这里要注意的是，在另一个实例必须也是sql server 2012并且在实例级别开启了”启用包含数据库”选项。我们尝试登录另一台服务器后，可以看到Contained Database,如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-13-sql-server-2012-contained-database/sql-server-2012-contained-database-201203131344564567.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203131344516109.png)

### 总结

本文简单讲述了Contained Database,使用Contained Database大大减少数据库在实例之间的迁移工作。但Contained Database真正的强大之处是和AlwaysOn结合使用，我将在后续文章中讲到。
