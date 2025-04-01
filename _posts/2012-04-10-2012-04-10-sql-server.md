---
layout: post
title: "理解SQL Server中的权限体系(上)----主体"
date: 2012-04-10
categories: blog
tags: [博客园迁移]
---

### 简介

权限两个字，一个权力，一个限制。在软件领域通俗的解释就是哪些人可以对哪些资源做哪些操作。在SQL Server中，”哪些人”，“哪些资源”,”哪些操作”则分别对应SQL Server中的三个对象，分别为主体\(Principals\),安全对象\(Securables\)和权限\(Permissions\)，而权力和限制则是对应了SQL Server中的GRENT和DENY。对于主体，安全对象和权限的初步理解，见图1.

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-10-sql-server/sql-server-201204101226071714.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204101225057172.png)

图1.简单理解主体,安全对象和权限的关系

对于图1中的造句来说，并没有主语，也就是并没有说谁给予的权限（难道是上帝?）。你可以理解为SA账户在最开始时给予了其他主体对于安全对象的权限。

### SQL Server中的验证方式

在给予别人权限之前，或是检查你是否有某项权限之前，SQL Server首先要知道“你”这个主体是否是你自己号称的那个主体。比如武侠小说中接头时对的暗号”天王盖地虎，宝塔镇河妖…”就是验证身份的一种方式。而对于SQL Server,是在你连接SQL Server时SQL Server就需要确认你是谁。SQL Server提供了两种身份验证模式:

**Windows身份验证模式**

**** Windows身份验证模式就像其名称所示那样，由Windows来验证主体，SQL Server并不参与验证。SQL Server完全相信Windows的验证结果。所以用此方式登录SQL Server时并不需要提供密码。虽然如此，但Windows身份验证模式要更加安全，因为Windows身份验证模式使用了Kerberos\(这一名词来源于希腊神话“三个头的狗——地狱之门守护者”\)协议。这也是微软推荐的最安全的做法。

但Windows身份验证模式在由域控制器控制网络访问的情况下才得以使用\(当然了，单机也包括在内\)。

**SQL Server和Windows身份验证模式（混合模式）**

我一直觉得这种模式的名称应该改为SQL Server或Windows身份验证模式更容易理解。这种模式即允许由Windows来验证主体身份，又允许SQL Server来验证主体身份，当由SQL Server验证主体身份时，需要用户名和密码来确认主体身份，和使用什么Windows账户半毛钱关系都没有。这些用户信息被加密后存在Master数据库中。

**设置验证模式**

设置验证模式非常简单。既可以在安装的时候进行设置，也可以在安装之后通过右键点击实例，选择属性，在安全性选项卡中进行改变，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-10-sql-server/sql-server-201204101226164660.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204101226128678.png)

图2.安装完SQL Server之后改变身份验证方式

### 理解主体

“主体”是可以请求 SQL Server 资源的实体。主体可以是个体，组或者进程。主体可以按照作用范围被分为三类:

  * Windows级别主体 
  * 服务器级别主体 
  * 数据库级别主体 



Windows 级别的主体包括Windows 域登录名和Windows 本地登录名。

SQL Server级的主体包括SQL Server 登录名和服务器角色。

数据库级的主体包括数据库用户和数据库角色以及应用程序角色。

**登录名**

**** 登录名是服务器级别的主体，但无论是上述哪个层级的主体，因为需要登录到SQL Server实例，所以每一个层级的主体都需要一个与之对应的登录名。对于Windows级别的主体来说，Windows用户会映射到登录名。对于数据库级别的主体来说，其用户必须映射到登录名中。而登录名可以不映射到数据库用户，如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-10-sql-server/sql-server-201204101226575252.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204101226429935.png)

图3.登录名的映射关系

在图3中实例层级的登录名中，我们看到除了自定义添加的用户之外，还有一些由系统添加的登录名。首先，以”\#\#”开头和结尾的用户是SQL Server内部使用的账户，由证书创建，不应该被删除。其次是sa账户，sa登录名拥有一切特权，可以在SQL Server中为所欲为，并且不能够被删除。因此sa作为分配权限的起点（也就是图1中所说的主语）.因此对于Sa的密码要设置的尽可能复杂，否则Sa登录名被盗取后果不堪设想。还有NT AUTHORITY\NETWORK SERVICE和NT AUTHORITY\SYSTEM账户是和启动SQL Server这个Windows服务的账户有关，如果使用本地登录账户或是网络账户启动SQL Server服务，请不要删除这两个账户，如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-10-sql-server/sql-server-20120410122706947.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204101227057491.png)

图4.以本地系统账户启动服务

最后BUILDIN\Administrator账户是与本地管理员组关联的登录名，默认属于sysadmin角色。这个账户使得任何属于本地管理员的账户都可以获得对SQL Server的完全控制权。

**数据库用户  
** 数据库用户是数据库级别的主体,被用于访问数据库层面的对象。每一个数据库用户都必须要一个与之对用的登录名。数据库用户的信息存在数据库中，而登录名存在实例级别的Master数据库中\(但SQL SERVER2012的Contained Database允许将登录名也存在数据库级别\)。通常来说，数据库层级的用户可以和映射的登录名不一致，但由于这种做法会引起混淆，因此并不推荐。如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-10-sql-server/sql-server-201204101227125336.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204101227114073.png)

图5.可以让用户名和登录名不一致，但并不推荐

默认情况下，每个数据库都带有4个内置用户，如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-10-sql-server/sql-server-201204101227171777.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204101227148203.png)

图6.数据库带的内置用户

dbo用户是Database Owner的简称，如果说SA是实例级别的老大，那DBO就是数据库级别的老大。这个用户也同样不能被删除，每一个属于sysadmin的服务器角色都会映射到数据库的dbo用户。每一个表创建时如果没有指定Schema，则默认在dbo这个schema下。

guest用户是一个来宾账户，这个账户允许登录名没有映射到数据库用户的情况下访问数据库。默认情况下guest用户是不启用的，你可以通过代码1来启用或不启用guest用户。
    
    
    --允许guest用户连接权限
    GRANT CONNECT TO guest
    --收回guest的连接权限
    REVOKE CONNECT TO guest

  


代码1.启用或回收guest用户的连接权限

你也可以给guest用户分配角色来控制guest的权限\(如图7所示\)，但是这有可能造成潜在的安全问题，最佳做法是单独创建数据库用户。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-10-sql-server/sql-server-201204101227507437.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204101227213016.png)

图7.为guest用户分配角色

而INFORMATION\_SCHEMA用户和sys用户拥有系统视图，因此这两个数据库用户不能被删除，如图8所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-10-sql-server/sql-server-201204101228009695.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204101227511209.png)

图8.INFORMATION\_SCHEMA和sys用于访问系统视图

**角色**

**** 角色是方便对主体进行管理的一种举措。SQL Server中的角色和Windows中的用户组是一个概念。属于某个角色的用户或登录名就会拥有相应的权限，这不难理解，就好比你在公司当经理，你就可以报销多少钱的手机费用。而比你低一个层级的开发人员则没有这个待遇。用户或登录名可以属于多个角色，这也同样不难理解，就像你在公司中可以是项目经理，也同时兼任高级工程师一样。

角色在SQL Server中被分为三类，分别为:

内置角色----这类角色在服务器安装时已经默认存在，其权限是固定的，并且不能被删除

用户自定义角色----这类角色由用户按照需求自定义创建

应用程序角色----这类特殊角色用于管理应用程序的数据访问

内置角色是在安装SQL Server时就固定的，无论是服务器角色还是数据库角色，其对应的权限都是固定的。具体每个角色对应的权限请查看MSDN（固定服务器角色<http://msdn.microsoft.com/zh-cn/library/ms175892.aspx>,固定数据库角色<http://msdn.microsoft.com/zh-cn/library/ms189121.aspx>）,但这里要注意一个特殊的角色: public角色。

public角色不同于其它角色，其权限可以被调整,如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-10-sql-server/sql-server-201204101228254852.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204101228174041.png)

图9.Public角色不同于其它角色在于其权限可以被修改

可以将Public角色理解为访问数据库或实例的最小权限，Public所拥有的权限自动被任何主体继承，所以对于Public角色的权限修改要格外小心。

而用户自定义角色是按照用户自己的需求组成的角色，由用户创建。

而应用程序角色并不包含任何用户，应用程序角色与其说是角色，不如说是一个特殊的用户。这是为应用程序专门准备的角色，仅仅为应用程序提供数据库访问权限。这个角色并不提供给用户，而是由应用程序的连接字符串嵌入角色名称和密码来激活对应权限。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-10-sql-server/sql-server-201204101228389288.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204101228337864.png)

图10.不同于其它数据库角色，应用程序角色需要设置密码

### 理解构架

构架（Schmea）是在SQL Server 2005之后的版本被引入的。可以将构架理解为一个命名空间。在SQL Server2000中其实也有构架的概念，但概念并不同。因为SQL Server 2000中的构架是和用户绑定的，比如我新建用户Jack,SQL Server自动分配一个叫Jack构架，用户Jack并不能改变这个选项，而由Jack所建的任何对象都在Jack之下，比如新建一个表，则为Jack.Table1。当Jack如果离职时，这对管理来说简直是一场噩梦。

在SQL Server 2005之后，SQL Server允许用户和构架分离。使得利用构架去拥有一些数据库层级的对象，比如说:表，视图等。

下面几种选择方式，比如当我默认构架是Sales,时，我可以用代码2中第一种写法，不用构架:
    
    
    [SELECT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SELECT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) * [FROM](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=FROM&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) Customer
    
    [SELECT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SELECT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) * [FROM](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=FROM&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) sales.Customer
    
    [SELECT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SELECT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) * [FROM](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=FROM&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) AdventureWorks.sales.Customer

  


代码2.引用对象的几种不同写法

因此，假如Customer表是由Jack建的，我可以将其分配给Sales构架，引用时使用Sales.Customer,而不是Jack.Customer。这无疑大大方便了管理，此外，可以针对构设置权限，这我会在本系列文章后续的文章中讲到。

### 总结

本文简单讲述了SQL Server的权限体系。以及主体的概念。理解SQL Server的安全性要首先理解这三大方面。下一篇文章中我将接着讲述安全对象。
