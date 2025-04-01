---
layout: post
title: "【译】Windows Azure迁移生命周期概览"
date: 2012-11-17
categories: blog
tags: [博客园迁移]
---

迁移生命周期是一套能够将你的程序或数据一步一步迁移到Windows Azure的标准指南。迁移的主要步骤分为分析阶段、应用程序迁移阶段、数据迁移阶段、测试和优化阶段以及操作和管理阶段，如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-11-17-windows-azure/windows-azure-201211170702547336.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201211/201211170702512894.gif)

图1.迁移到Windows Azure的各个步骤

本文对会对各个阶段进行详尽的解释并提供了相关信息的链接。

### 分析阶段

这个阶段的目标是明白需要Windows Azure解决方案的业务需求。在定义好业务目标之后，通过对现有的应用程序构架进行查看以便通过云端构架和现有应用程序的构架的差异来确定是否需要对企业内部应用的构架进行重构来满足Windows Azure的业务需求。下面的任务和问题可以帮助你确定迁移计划。

**定义业务需求**

**** 当应用程序运行在Windows Azure上时，不同的业务场景会引发很多问题:

  * 在Windows Azure上的解决方案是否面向新的用户或者客户 
  * 是否需要通过多租户方式来支持多个客户 
  * 将数据部署在微软数据中心而不是客户自己的服务器上是否符合公司的规定 
  * 哪一类应用程序更适合云端构架和策略 
  * 什么样的迁移方式更适合我的应用程序？是将整个应用以及相关依赖完全迁移到Windows Azure上，还是将部分应用迁移到云端而部分资源依然在企业内部，亦或是将应用迁移到Windows Azure上而相关的依赖放到Windows Azure虚拟机上 



回答上述问题的答案会影响为Windows Azure平台上设计的程序的行为。

**根据特性差异做决定**

你是否能在不修改现有应用程序的基础上将应用程序迁移到Windows Azure上呢？举个例子，Windows Azure SQL Database并不支持所有非云端SQL Server上的所有功能。如果你本地的SQL Server使用了CLR对象，你就需要将这部分CLR逻辑转移到应用程序层或是转移成标准的T-SQL代码，这是由于当前的Windows Azure SQL Database并不支持SQL CLR。

自从Windows Azure预览版开始,Windows Azure添加了新的虚拟机功能。通过虚拟机功能，你可以在不修改任何代码的情况下将现有的基于Windows Server的SQL Server应用程序无缝迁移到Windows Azure平台。在Windows Azure的虚拟机环境下，传统的SQL Server功能在云环境下依然可用。但在虚拟机环境下的关系数据库的性能就取决于下面几点，包括虚拟机大小、磁盘的数量和配置、网络、数据库软件的配置以及应用程序的负载。我们推荐开发人员在不同的虚拟机对程序进行性能基准测试以确定最佳性能，更多信息请查看:[Migrating to SQL Server in a Windows Azure Virtual Machine](http://msdn.microsoft.com/en-us/library/windowsazure/jj156165.aspx)。

**根据性能和可扩展性做一个计划**

很多遗留的应用程序都被设计成业务逻辑和数据访问紧密耦合。对于旧有的应用程序,为了部署到Windows Azure有更好的性能和可扩展性，将这种耦合解耦是非常有必要的。如果你的程序和数据库的交互非常密切，那么可以考虑使用[Windows Azure Caching Service](http://msdn.microsoft.com/library/windowsazure/gg278356.aspx)或是实现你自己的缓存机制来将应用程序和数据库的交互放到一个批处理中以减少应用程序和数据库的交互次数。将数据库迁移到Windows Azure SQL Database有可能需要重新设计数据模型，因为单个数据库实例每秒能够处理的事务数量和数据库的大小都是有限的。所以考虑使用多个实例进行scale-out构架或是SQL Server Database Federation而不是昂贵的Scale-Up构架。

**根据软件的生命周期管理做一个计划**

在Windows Azure上应用程序的版本和升级是需要被考虑在内的事。根据服务协定,你的应用程序可能需要不同的版本来服务不同层次的客户,你当然也想在Windows Azure升级应用程序时尽量减少停机时间。我们推荐你在Windows Azure上维护软件升级过程中的中间版本和生产环境的版本，以便在遇到兼容性问题时可以回滚。你升级的回滚首先要可以回滚应用程序，其次是数据库。

在这个阶段之后，我们推荐你建立一个试点工程。

### 应用程序迁移阶段

**** 当你决定将应用程序迁移到Windows Azure之后,为你的程序建立只有少量数据的试点版本先部署到云端进行尝试。首先根据业务和技术角度你的应用程序代码做出修改以适合云端，然后将这部分代码部署到Windows Azure中适当的角色中。

通常情况下，企业内部应用可以在少量修改或不修改代码的情况下直接迁移到Windows Azure中，但这有可能引起性能，扩展性或是安全方面的问题。为了实现更好的性能和可扩展性，我们推荐您在迁移到Windows Azure之前基于多角色来重新设计您的应用程序，请看[Development Considerations for Windows Azure Cloud Services](http://msdn.microsoft.com/en-us/library/windowsazure/jj156146.aspx)。我们推荐您首先将应用程序迁移到Windows Azure Cloud Service中，然后迁移数据，如果由于性能、安全或是其它原因，您的应用程序的一部分还需要放在企业内部，这就需要混合解决方案，关于混合解决方案，请看[Building Hybrid Solutions with Windows Azure](http://www.windowsazure.com/en-us/develop/net/fundamentals/hybrid-solutions/)。

如果您决定在Windows Azure VM中使用SQL Server的，将现有的应用程序的连接指向部署在Windows Azure的SQL Server上，除此之外，在下面两种迁移方式中选择一种:

  * 您的程序已经部署在了VM之上，如果是这样的话只需要将整个VM迁移到Windows Azure中，此时您的程序配置和数据都已经在虚拟机之中了，但这有可能需要您上传一个非常大的.vhd文件到Windows Azure中。另外，这个虚拟机有可能存在对驱动或是硬件的依赖，而这部分驱动或是硬件在Windows Azure中有可能并不存在 
  * 您可以直接在Windows Azure中建立虚拟机，您可以通过存在的镜像模版来初始化一个虚拟机。您可以挑选一个已经包含SQL Server的镜像，然后将您的应用程序安装到这个虚拟机之中。这不仅会减少上传时间，还可以避免驱动和硬件的依赖，但也需要安装应用和上传数据 



对于如何将现有的SQL Server迁移到Windows Azure的虚拟机中的更多信息，请看[Building Hybrid Solutions with Windows Azure](http://www.windowsazure.com/en-us/develop/net/fundamentals/hybrid-solutions/)。

### 数据迁移阶段

如果使用Windows Azure Cloud Service,将关系型数据由企业内部的SQL Server迁移到Windows Azure SQL Database中，将非结构数据迁移到Windows Azure Storage中。更多信息请看[Migrating Data to Tables, Blobs, and Drives in Windows Azure](http://msdn.microsoft.com/en-us/library/windowsazure/jj156168.aspx)和[Migrating SQL Server Databases to Windows Azure SQL Database](http://msdn.microsoft.com/en-us/library/windowsazure/jj156160.aspx)。

**** 如果您决定在Windows Azure虚拟机上使用SQL Server,你可以使用如下两种迁移方式中的一种:

  * 您可以在虚拟机中存在数据，您可以直接上传.vhd到Windows Azure 
  * 您可以在Windows Azure中建立虚拟机，然后您可以将.vhd中的数据作为数据磁盘上传到Windows Azure中。您可以使用数据磁盘存储SQL Server的日志和数据文件,除此之外，您还可以使用在[Migrating to SQL Server in a Windows Azure Virtual Machine](http://msdn.microsoft.com/en-us/library/windowsazure/jj156165.aspx)主题中所阐述的工具将已经存在的SQL Server数据库迁移到Windows Azure虚拟机中 



### 测试和优化阶段

在您将程序和数据迁移到Windows Azure之后,对您的程序进行功能上和性能上的测试。在这个阶段，在云上测试您的应用程序来确认程序符合预期。然后，对部署在企业内和云上的程序对性能方面进行对比。然后，对云上应用程序的功能，性能，扩展性所暴漏出来的问题进行解决，更多信息，请看[Implementing the Migration Plan for Windows Azure](http://msdn.microsoft.com/en-us/library/windowsazure/jj156155.aspx)。

### 操作和管理阶段

在测试和优化阶段之后，通过Windows Azure Diagnostics来对应用程序进行追踪和监测。您可以通过Windows Azure Diagnostics对运行在Windows Azure上的应用程序进行诊断数据的收集。您可以用收集到的数据进行排错和调试、性能测试、资源使用检测、流量分析以及容量规划和审查。更多信息，请看MSDN的[Diagnostics and Debugging in Windows Azure](http://msdn.microsoft.com/en-us/library/windowsazure/hh694035.aspx)。

如果您需要对企业内部的SQL Server和Windwos Azure上的SQL Server进行数据同步，或是对Windows Azure上不同的SQL Server实例进行数据同步，您可以设立和配置[SQL Data Sync](http://msdn.microsoft.com/en-us/library/windowsazure/hh456371.aspx)服务。另外，我们推荐您建立一个数据恢复计划以防在用户错误操作以及其它灾难时可以恢复数据。更多信息，请看[High Availability and Disaster Recovery Considerations with Windows Azure SQL Database](http://msdn.microsoft.com/en-us/library/windowsazure/jj156170.aspx)。

\-----------------------------------

本文翻译自Windows Azure官方指南，全部系列翻译完后会集结成PDF放在Technet的Community Content中。
