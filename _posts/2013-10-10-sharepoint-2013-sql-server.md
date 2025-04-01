---
layout: post
title: "SharePoint 2013连接非默认端口的SQL Server"
date: 2013-10-10
categories: blog
tags: [博客园迁移]
---

SharePoint 2013场在连接的时候不允许出现连接地址中包含端口号，否则场配置就会报错，在执行到配置场数据库时无法完成。

此时如果SQL Server不是用的默认端口1433的话，那么就需要挂上端口号。解决办法就是配置别名，但服务端的别名在64位SQL Server中并不生效，因此可以安装Native Client来解决该问题。对于复制使用了非默认端口也可以如此解决。

首先场Web服务器上需要安装Native Client。然后场服务器上执行cliconfg.exe，然后如图1所示配置端口即可。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-10-10-sharepoint-2013-sql-server/sharepoint-2013-sql-server-10162753-0a28f81e7ca841a78222d421b96a2912.png)](//images0.cnblogs.com/blog/35368/201310/10162752-276d0a0f1be84904bc4384856d0e4fd4.png)

图1.Native Client

因此，我们就可以使得连接字符串中不用再包含端口号。
