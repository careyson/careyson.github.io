---
layout: post
title: "SSIS连接SAPBI"
date: 2013-10-11
categories: blog
tags: [博客园迁移]
---

SSIS默认的连接管理器是没有连接到Oracle或SAPBI的，因此如果希望SSIS调用SAP RFC的话，可以使用微软提供的连接管理器插件。

有关这一点的详细信息可以参考MSDN的官方文档：

<http://technet.microsoft.com/en-us/library/ms140203.aspx>

而具体的连接管理器地址可以在：

<http://www.microsoft.com/zh-cn/download/details.aspx?id=16978>

下载到。

当下载并完成安装后，就可以在SSIS中看到连接管理器中包含SAP BI，如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-10-11-ssis-sapbi/ssis-sapbi-11132949-cf66a55915774519b560a6ffc4ddedb9.png)](//images0.cnblogs.com/blog/35368/201310/11132949-fcacc4e108084f988057a9a5909d6ee8.png)

图1.包含SAPBI连接管理器的SSIS

值得注意的是，如果SQL Server是评估版的话，连接管理器的安装可能会由于不满足先决条件而无法安装。
