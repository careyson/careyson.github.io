---
layout: post
title: "理解SQL Server中的权限体系(下)----安全对象和权限"
date: 2012-04-12
categories: blog
tags: [博客园迁移]
---

在开始阅读本文之前，请确保你已经阅读过上一篇文章，文章地址:

[理解SQL Server中的权限体系\(上\)----主体](http://www.cnblogs.com/CareySon/archive/2012/04/10/MSSQL-Security-Principal.html)

### 简介

在上一篇文章中，我对主体的概念做了全面的阐述。本篇文章接着讲述主体所作用的安全对象以及所对应的权限。

### 理解安全对象\(Securable\)

安全对象，是SQL Server 数据库引擎授权系统控制对其进行访问的资源。通俗点说，就是在SQL Server权限体系下控制的对象，因为所有的对象\(从服务器，到表，到视图触发器等\)都在SQL Server的权限体系控制之下，所以在SQL Server中的任何对象都可以被称为安全对象。

和主体一样，安全对象之间也是有层级，对父层级上的安全对象应用的权限会被其子层级的安全对象所继承。SQL Server中将安全对象分为三个层次,分别为:

  * 服务器层级
  * 数据库层级
  * 构架层级



这三个层级是从上到下包含的，如图1所示：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-12-sql-server/sql-server-201204120831102311.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204120831094852.png)

图1.安全对象层级之间的包含关系

对于SQL Server对于层级的详细划分，可以参看MSDN\(<http://msdn.microsoft.com/zh-cn/library/ms190401.aspx>\)。SQL Server中全部的安全对象如图2和图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-12-sql-server/sql-server-201204120831101373.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204120831107818.png)

图2.服务器层级的安全对象

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-12-sql-server/sql-server-201204120831113226.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204120831115767.png)

图3.数据库和构架层级的安全对象

### 理解权限\(Permission\)

权限是连接主体和安全对象的纽带。SQL Server 2008中,权限分为权利与限制,分别对应GRANT语句和DENY语句。GRANT表示允许主体对于安全对象做某些操作，DENY表示不允许主体对某些安全对象做某些操作。还有一个REVOKE语句用于收回先前对主体GRANT或DENY的权限。

在设置权限时，尤其要注意权限在安全对象上的继承关系。对于父安全对象上设置的权限，会被自动继承到子安全对象上。主体和安全对象的层级关系如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-12-sql-server/sql-server-201204120831121175.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204120831124588.gif)

图4.主体和安全对象之间的层级关系

比如，我给予主体CareySon\(登录名\)对于安全对象CareySon-PC\(服务器\)的Select\(权限\),那么CareySon这个主体自动拥有CareySon-PC服务器下所有的数据库中表和视图等子安全对象的SELECT权限。如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-12-sql-server/sql-server-201204120831135536.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204120831134174.png)

图5.主体对于安全对象的权限在层级上会继承

此时，主体CareySon可以看到所有数据库极其子安全对象,如图6所示

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-12-sql-server/sql-server-201204120831141882.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204120831145503.png)

图6.主体对于安全对象的权限在层级上会继承

### 使用T-SQL语句进行权限控制

在理解了主体，安全对象和权限的概念之后，使用T-SQL语句进行权限控制就非常简单了。使用GRANT语句进行授予权限，使用DENY语句限制权限，使用REVOKE语句收回之前对于权限的授予或者限制。

GRANT在MSDN的原型为: 
    
    
    [GRANT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GRANT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) { [ALL](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ALL&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [ [PRIVILEGES](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=PRIVILEGES&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ] }
          | permission [ ( [column](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=column&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [ ,...n ] ) ] [ ,...n ]
          [ [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [ class :: ] securable ] [TO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=TO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) principal [ ,...n ] 
          [ [WITH](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=WITH&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [GRANT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GRANT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [OPTION](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=OPTION&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ] [ [AS](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=AS&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) principal ]

  
对于GRANT语句的理解就像造句一样 GRANT 某种权限 ON 安全对象类型::安全对象 TO 主体。如果指定了WITH GRANT OPTION,则被授予权限的主体可以授予别的主体同样的权限。

对于DENY语句在MSDN中的原型和GRANT大同小异:
    
    
    [DENY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DENY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) { [ALL](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ALL&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [ [PRIVILEGES](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=PRIVILEGES&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ] }
          | permission [ ( [column](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=column&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [ ,...n ] ) ] [ ,...n ]
          [ [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [ class :: ] securable ] [TO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=TO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) principal [ ,...n ] 
          [ [CASCADE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CASCADE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)] [ [AS](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=AS&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) principal ]

  
值得注意的是CASCADE选项表示拒绝主体对于安全对象的访问权限同时决绝主体授予其他主体对于安全对象的权限。

而REVOKE语句用于收回原来授予或拒绝某个主体对于安全对象的权限。REVOKE在MSDN中的原型如下：
    
    
    [REVOKE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=REVOKE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [ [GRANT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GRANT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [OPTION](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=OPTION&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [FOR](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=FOR&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ]
          { 
            [ [ALL](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ALL&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [ [PRIVILEGES](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=PRIVILEGES&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ] ]
            |
                    permission [ ( [column](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=column&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [ ,...n ] ) ] [ ,...n ]
          }
          [ [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [ class :: ] securable ] 
          { [TO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=TO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) | [FROM](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=FROM&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) } principal [ ,...n ] 
          [ [CASCADE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CASCADE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)] [ [AS](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=AS&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) principal ]

  


一个进行权限控制的例子如下:
    
    
    [grant](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=grant&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [select](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=select&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)--权限
     [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [Schema](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=Schema&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)::SalesLT--类型::安全对象
      [to](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=to&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) careyson--主体
    
    [deny](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=deny&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [select](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=select&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)--权限
     [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [Schema](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=Schema&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)::SalesLT--类型::安全对象
      [to](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=to&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) careyson--主体
    
    [revoke](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=revoke&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [select](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=select&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)--权限
     [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [Schema](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=Schema&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)::SalesLT--类型::安全对象
      [to](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=to&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) careyson--主体

  


控制权限的时候需要注意如下几点:

  * GRANT会移除主体作用于安全对象上的DENY和REVOKE
  * DENY和REVOKE移出主体作用于安全对象上的GRANT
  * REVOKE会移除主体作用于安全对象上的DENY和GRANT
  * 在高层级上的DENY会覆盖任何子层级的GRANT。比如说，你对于Schema进行Deny,对其包含的表进行Grant,则表的GRANT会被Schema的Deny锁覆盖,如图7所示。



[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-12-sql-server/sql-server-201204120831158436.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204120831147389.png)

图7.父层级的Deny覆盖子层级的Grant

  * 对于主体作用于高层级的GRANT会被其子Deny所覆盖，还是上面的例子，我对于Schema进行Grant,对于表进行Deny,最后结果还是Deny，如图8所示。



[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-12-sql-server/sql-server-201204120831154225.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204120831152306.png)

图8.子层级的Deny覆盖父层级的Grant

  * SQL Server不对sysadmin组的成员做任何权限验证操作。换句话说，sysadmin组的成员可以为所欲为



而对于何种的安全对象可以进行何种对应权限的GRANT,REVOKE,DENY,请参看MSDN（<http://msdn.microsoft.com/zh-cn/library/ms191291.aspx>）

### 总结

本文接着上篇文章讲述了安全对象以及相应的权限。对于权限控制时，理解权限的继承和权限的覆盖会在设置权限时减少很多问题。
