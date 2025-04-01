---
layout: post
title: "SQL Server的Execute As与连接池结合使用的测试"
date: 2014-12-05
categories: blog
tags: [博客园迁移]
---

### 简介

在SQL Server中，Execute As关键字允许当前账户在特定上下文中以另一个用户或登录名的身份执行SQL语句，比如用户张三有权限访问订单表，用户李四并没有权限访问订单表，那么给予用户李四访问订单的表的权限就有些过头了，因为李四可能只有在很特定的上下文环境中才需要访问订单表，因此可以在特定上下文中使用Execute As Login 张三，暂时以张三的身份访问订单表，从而保证更安全的权限控制。

另一方面，应用程序通过网络与数据库连接是需要在传输层通过TCP协议，而TCP协议在建立连接的阶段的成本会比较高（1.同步请求 2同步请求+Ack 3.确认 这三个阶段），因此减少TCP连接可以很大程度上提升性能。因此当应用程序与数据库建立连接后，在一定空闲时间内不在TCP协议上切断连接，而是保持连接，连接的断开操作仅仅是逻辑上断开，当新的请求由应用程序发送到客户端时，复用之前建立在应用程序与数据库上的连接，从而极大的提升了连接性能。

当在连接池上使用Execute As切换连接的安全上下文时则可能产生的情况我们通过下述几种实验来得出结论。

### 在使用连接池的情况下使用Execute As切换安全上下文

试验中所用的连接字符串全部为：
    
    
       1: data source=.;database=test;uid=GetMembers;pwd=sa;pooling=true;Connection Timeout=30
    
    
       2:  
    
    
       3:  

**实验一：使用动态SQL，切换安全上下文**

该实验分别使用两个连接，第一次连接中，用户为GetMembers，将安全上下文切换为系统最大权限登录名SA，连接断开时保持SA安全上下文，应用程序端发送的SQL代码如代码1：
    
    
       1: EXECUTE AS LOGIN = 'sa';SELECT * FROM dbo.Higher;"

代码1.第一次连接数据库执行的语句

在将身份切换为SA后，正常查询GetMembers没有的dbo.Higher表的权限，执行完代码1所示的SQL后，连接正常关闭。第二次连接使用连接池复用第一次连接所建立的连接，执行的SQL如代码2： 
    
    
       1: SELECT * FROM Higher

代码2.第二次连接使用的SQL

在Asp.net端看到的查询结果如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-12-05-sql-server-execute-as/sql-server-execute-as-051634384987801.png)](//images0.cnblogs.com/blog/35368/201412/051634379366672.png)

图1.两次连接在Asp.net中的信息

由图1可以看出，当复用连接池时，由于第一次连接以GetMembers登录名登录，安全上下文切换到SA并没有切换回来，第二次再次登录时就会报错，报的错对应在SQL Server日志里如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-12-05-sql-server-execute-as/sql-server-execute-as-051634392486172.png)](//images0.cnblogs.com/blog/35368/201412/051634388736986.png)

图2.SQL Server端报错

结论：由此看出，当连接池复用时，第一次连接切换了上下文第二次连接复用时就会直接报错，这也是期待的结果，从而保证了安全性，如果希望采用这种方式结合连接池，则必须在第一次连接完使用Revert将安全上下文转换回登录时的安全上下文。

**实验二：在存储过程中使用Execute As转换安全上下文**

还是两次连续的连接，第一次在存储过程中执行Execute As转换上下文为SA，代码如代码3所示：
    
    
       1: CREATE PROCEDURE [dbo].[GetMembers]
    
    
       2:  
    
    
       3: AS
    
    
       4:  
    
    
       5: EXECUTE AS USER = 'sa'

代码3.在存储过程中执行Execute As

第二次连接进来的查询执行一个非常简单的Select语句，但没有对应权限，执行结果如图3所示：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-12-05-sql-server-execute-as/sql-server-execute-as-051634401237271.png)](//images0.cnblogs.com/blog/35368/201412/051634396868870.png)

图3.第二次连接不会受第一次在存储过程中改变上下文的影响

在数据库端对应的跟踪如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-12-05-sql-server-execute-as/sql-server-execute-as-051634408894170.png)](//images0.cnblogs.com/blog/35368/201412/051634404833228.png)

图4.对应的跟踪

因此可以看出，在存储过程中改变安全上下文对连接池无影响，安全上下文仅仅在存储过程中有效。

**实验三：连接池对隔离级别的影响**

在实验3中对连接的默认隔离级别更改，更改为可序列化级别，SQL语句如代码4所示。
    
    
       1: SET TRANSACTION ISOLATION LEVEL SERIALIZABLE

代码4.改变连接的隔离级别

随后的连接查询并返回当前连接的隔离级别，结果如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-12-05-sql-server-execute-as/sql-server-execute-as-051634419983199.png)](//images0.cnblogs.com/blog/35368/201412/051634414207840.png)

图5.改变隔离级别导致复用连接池中的连接隔离级别改变

结论：使用连接池对修改Session级别的隔离级别用完必须改回默认连接，否则可能导致后续连接在不正确的隔离级别下运行。

**实验四：在存储过程中改变隔离级别的连接复用的影响**

下面我们在存储过程中改变隔离级别，代码如代码5所示：
    
    
       1: create PROCEDURE [dbo].[TestIslation]
    
    
       2: AS
    
    
       3:  SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED
    
    
       4:  
    
    
       5:  SELECT CASE transaction_isolation_level 
    
    
       6: WHEN 0 THEN 'Unspecified' 
    
    
       7: WHEN 1 THEN 'ReadUncommitted' 
    
    
       8: WHEN 2 THEN 'ReadCommitted' 
    
    
       9: WHEN 3 THEN 'Repeatable' 
    
    
      10: WHEN 4 THEN 'Serializable' 
    
    
      11: WHEN 5 THEN 'Snapshot' END AS TRANSACTION_ISOLATION_LEVEL 
    
    
      12: FROM sys.dm_exec_sessions 
    
    
      13: where session_id = @@SPID

代码5.在存储过程中更改隔离级别，并显示当前的隔离级别

在随后的连接中，在非存储过程中调用显示当前Session隔离级别的语句，并打印，结果如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-12-05-sql-server-execute-as/sql-server-execute-as-051634430145554.png)](//images0.cnblogs.com/blog/35368/201412/051634425143640.png)

图6.

由图6可以看出，第三次连接在存储过程内改变隔离级别，第四次连接的隔离级别并不受影响。

结论：在存储过程内改变隔离级别不会影响后续连接池的使用。

### 小结

本文对在使用连接池情况下数据库中的一些细节场景进行了实验，可以看到对于连接池复用来说，改变隔离级别可能会存在隐性的风险，其他情况SQL Server都能够显式处理。因此使用连接池对修改Session级别的隔离级别用完必须改回默认连接，或者在语句级别修改隔离等级而不是Session级别。
