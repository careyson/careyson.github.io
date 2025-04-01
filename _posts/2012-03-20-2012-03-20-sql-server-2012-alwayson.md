---
layout: post
title: "SQL Server 2012中的AlwaysOn尝试"
date: 2012-03-20
categories: blog
tags: [博客园迁移]
---

### 简介

SQL Server2012中新增的AlwaysOn是一个新增高可用性解决方案。在AlwaysOn之前，SQL Server已经有的高可用性和数据恢复方案,比如数据库镜像，日志传送和故障转移集群.都有其自身的局限性。而AlwaysOn作为微软新推出的解决方案，提取了数据库镜像和故障转移集群的优点。本文旨在通过实现一个AlwaysOn的实例来展现AlwaysOn。

### 配置AlwaysOn

虽然AlwaysOn相比较之前版本的故障转移集群而言，步骤已经简化了许多。但配置AlwaysOn依然是一件比较麻烦的事，不仅需要你对SQL Server比较熟悉，还需要对Windows Server有所了解。本文配置AlwaysOn分为两个板块，分别为:配置Windows和配置SQL Server。

在开始说道配置Windows之前，首先简单介绍一下测试环境。

我搭了三台Windows Server 2008的虚拟机（SQL SERVER 2012比较麻烦，必须2008 sp2以上版本windows server才能安装）,如图1所示。其中将活动目录和DNS服务器安在了Windows Server2008 Server 1.没有启用DHCP服务器，三台服务器的IP分别为192.168.100.1/24,192.168.100.2/24,192.168.100.3/24。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-20-sql-server-2012-alwayson/sql-server-2012-alwayson-201203201227364180.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203201227365085.png)

图1.三台装有Windows Server2008的测试虚拟机

三台服务器都加入了由Windows Server 2008 Server1作为AD建立域SQL2012.TEST。三台虚拟机的名称分别为SQLServerTest1,SQLServerTest2,SQLServerTest3。

### 配置Windows Server

首先在分别在三台测试服务器上安装故障转移集群的功能，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-20-sql-server-2012-alwayson/sql-server-2012-alwayson-201203201227372096.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203201227379098.png)

图2.在测试服务器上安装故障转移集群的功能

在安装好故障转移集群的功能之后，在Server1上进行对集群的配置.如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-20-sql-server-2012-alwayson/sql-server-2012-alwayson-201203201227398933.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203201227386490.png)

图3.在故障转移集群管理中创建集群

然后在接下来的步骤中，将三台服务器加入集群，如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-20-sql-server-2012-alwayson/sql-server-2012-alwayson-201203201227406325.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203201227399423.png)

图4.将三台测试服务器加入集群

点击下一步，进行测试,如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-20-sql-server-2012-alwayson/sql-server-2012-alwayson-20120320122740686.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203201227401276.png)

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-20-sql-server-2012-alwayson/sql-server-2012-alwayson-201203201227418635.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203201227419225.png)

图5.对集群进行验证测试

点击下一步，添加集群名称,如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-20-sql-server-2012-alwayson/sql-server-2012-alwayson-201203201227428536.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203201227421078.png)

图6.添加集群IP和集群名称

然后点击下一步确认后，最后完成集群的创建，如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-20-sql-server-2012-alwayson/sql-server-2012-alwayson-201203201227439309.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203201227431535.png)

图7.完成集群的创建

### 配置SQL Server

在配置完Windows Server之后，就该配置SQL SERVER了。分别在三台测试机上安装SQL Server 2012,所安装的功能如图8所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-20-sql-server-2012-alwayson/sql-server-2012-alwayson-201203201227442275.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203201227448404.png)

图8.SQL Server 2012安装的功能

安装完SQL Server 2012之后,运行SQL Server配置管理器，如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-20-sql-server-2012-alwayson/sql-server-2012-alwayson-20120320122745780.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203201227443322.png)

图9.运行SQL Server 配置管理器

然后在SQL Server实例中开启alwaysOn选项，如图10所示.

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-20-sql-server-2012-alwayson/sql-server-2012-alwayson-201203201227465698.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203201227456603.png)

图10.开启AlwaysOn

未完待续….
