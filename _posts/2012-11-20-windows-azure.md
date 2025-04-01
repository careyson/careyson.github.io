---
layout: post
title: "【译】为迁移到Windows Azure制定规划"
date: 2012-11-20
categories: blog
tags: [博客园迁移]
---

当开始您的迁移计划时，您需要考虑比如成本、业务和技术需求、时间期限、在迁移后必要的测试计划等几个关键因素。本章提供了帮助您迁移到Windows Azure需要考虑的地方以及详尽的指导。

本文将会分为以下几个小节

> •为成本制定计划
> 
> •识别出Windows Azure可以解决的关键业务和技术问题
> 
>   
> •进行分析和设计
> 
>   
> •为迁移各部分计划制定时间规划
> 
>   
> •规划迁移过渡期
> 
>   
> •规划测试
> 
>   
> •找出出所需的资源
> 
>   
> •规划在Windows Azure上的程序管理

### 为成本制定计划

成本是在制定迁移计划时所需要认真对待的最重要的问题，所以我们极力推荐在对于企业内迁移到Windwos Azure做决策分析和计划制定的过程中先考虑成本问题。决定Windows Azure的价格取决于多个因素，比如网络流量、应用程序负载等。关于如何计算Windows Azure的价格超出了本文范围。我们推荐在迁移计划开始就使用Windows Azure价格计算器来计算成本，您可以在[这里](http://www.windowsazure.com/en-us/pricing/calculator/)找到Windows Azure价格计算器。

当计算成本时，不要忘了把开发和测试时使用Windows Azure的费用包括在内。在企业内的开发项目中，您也许需要为开发和测试的服务器付费，同样，在Windows Azure环境中，您也需要在这个过程中为是同Windows Azure的资源付费。除此之外，您还需要考虑培训和学习的费用。我们推荐您事先进行性能测试和容量规划以便在一开始就知道您的应用程序需要什么样的容量。这篇关于[Windows Azure成本评估](http://msdn.microsoft.com/en-us/library/windowsazure/jj136829.aspx)的文章可以帮助您了解一个典型的Windows Azure应用程序所需的费用。

### 确定Windows Azure可以解决的关键业务和技术问题

Windows Azure对于解决某些业务和技术问题非常有效，虽然下面的列表不完全，但如果您的应用程序有以下特点，那么会非常适合迁移到Windows Azure。

  * **用户分布离散** :Windows Azure的数据中心横跨多个大陆。当需要时，可以通过数据中心之间的数据交互来大大提高性能。Windows Azure所包含的例如内容分发网络\(CDN\)和数据同步服务可以使得将“热”数据分布到多个离用户更近的数据中心，这使得用户和数据中心之间的网络传输更快从而优化了用户体验。 
  * **负载变化大** :对于企业内网络来说，您需要购买大量硬件来使您的应用程序在面对高峰期时性能不至于下降。比如说吧，一个零售店通常需要买额外的服务器来应付节假日时的购物高峰。同样，一个会计部门需要购买额外的服务器应付月底和年终的负载。除了上述情况之外，其它大多时间服务器都不会被充分利用。而对于Windows Azure来说，在负载高峰时多启用一个应用程序的实例来应对负载，而在平时低负载时关闭这个实例，这样一来，您仅仅只要根据您的需要付费使用Windows Azure。 
  * **多租户** ：对于服务提供者来说，Windows Azure允许您使用相同应用程序构架为任何数量的客户提供服务，因此降低了运营成本。 
  * **更关注程序本身** :对于服务提供者来说更希望将精力和资源放到功能设计和程序开发上而不是去维护基础构架，Windows Azure可以帮助您从传统的企业内部程序中维护基础构架的工作中解脱出来，将资源放到功能设计和程序开发上。 
  * **减少对基础构架资源的需求** ：当您利用Windows Azure提供的弹性扩展来构架您的程序时，Windows Azure提供的角色实例都可以按需分配，因此您不再需要预先购买硬件和担心服务器面对负载峰值时的性能。 



Windows Azure除了具有面向服务的特性之外，还可以在其之上运行虚拟机。在Windows Azure之上的虚拟机可以运行任何其支持的操作系统，在虚拟机上部署的程序和在本地部署的程序的运行模式完全一样。对于Windows Azure虚拟机所支持的操作系统，请看[Overview of Windows Azure Virtual Machines](http://msdn.microsoft.com/en-us/library/windowsazure/jj156143.aspx)。虚拟机可以作为为程序构架提供服务的一部分。对于那些不是那么容易迁移到Azure的应用程序，虚拟机是一个不错的解决方案。更多信息，请看[Migrating with Windows Azure Virtual Machines](http://msdn.microsoft.com/en-us/library/windowsazure/jj156159.aspx)。

### 进行分析和设计

在分析和实现阶段，您首先需要了解希望迁移到云端的程序构架，然后设计在Windows Azure中的实现方法并出具实现计划。在这个阶段，您需要列出程序构架和时间点的大纲。

一些计划的关键元素比如:

  * **识别当前的挑战** :对于任何程序的重构，下面列表包含了您需要认真规划的点。 
    * **在当前构架的当前负载中，应用程序性能不尽人意** :比如说,SQL查询性能底下，在迁移之前您就应该进行性能调优。您还应该重新设计和横向扩展应用程序层的模块。 
    * **确定弹性扩展需求** :您需要识别出您的程序是否能够按功能分解成能够独立运行的可伸缩单元。 
    * **不均匀的负载模式** :您应该识别出程序不均匀的负载模式，并为高峰期制定横向扩展计划。相对平时的低负载，您需要为高峰期的高负载指定横向扩展计划。 
    * **增长预测** :通常，增长预测后IT部门首先需要知道模式要改变了。面对这个问题决定对哪一部分进行横向扩展 
  * **识别技术要求** :获知您程序的每个部分分别在忙时和闲时的需要。然后，为每个部分的可扩展性做一个计划。每个部分可能会有不同的可扩展性机制。技术要求可不仅仅是性能部分，举例来说，高可用性和灾难恢复的要求，对最大网络延迟的要求等这些都需要在规划迁移时决定，下面的列表列出了一些技术要求的例子 
    * **使用关系型存储** :查看数据是否应该被关系存储，那些数据需要关系存储和事务的数据应该存在关系存储中。您或许应该使用Windows Azure SQL Database或是运行在虚拟机中的SQL Server来存储这些数据,而对于其它非关系型的数据使用Windows Azure Tables, Windows Azure Blob storage, 或Windows Azure drives进行存储，我们推荐您要识别出程序中的各部分数据的存储方式。 
    * **选择关系型存储方式** :是使用Windows Azure SQL Database还是在虚拟机中的SQL Server取决于多个因素,如果您不想对高可用性、负载均衡和故障转移花费经历的话，Windows Azure SQL Database最为合适。但对于目前在Windows Azure SQL Database目前还没有的功能，在虚拟机中的SQL Server无疑更加合适.对于这个选择取决于具体的情况和不同的解决方案，下述列表就是做这个决定时一些需要考虑的方面。 
    * **数据库大小** :Windows Azure SQL Database WEB版大小限制是5G，而商业版大小限制是150G。如果需要大小超过这个限制,您可能需要使用federations或是分区。对于federations的指导方针和限制请看[Federation Guidelines and Limitations](http://msdn.microsoft.com/en-us/library/windowsazure/hh597469.aspx)。Federation对于获取数据更加有效，但同时对于连接和聚合操作就有了限制,对此详细信息请看[Federations in SQL Database \(SQL Database\)](http://msdn.microsoft.com/en-us/library/windowsazure/hh597452.aspx)。对于最新的SQL Database的大小限制和版本信息，请看[Accounts and Billing in SQL Database](http://msdn.microsoft.com/en-us/library/windowsazure/ee621788.aspx)。 
    * **数据库数量** :默认情况下，SQL Database每个订阅支持6个数据库，每个实例包括master数据库在内最多支持150个数据库。当然如果您需要超过这个限制也是可以的，有关此的更多信息，请联系微软在线客户服务的客服代表 
    * **跨库查询** :SQL Database当前还不支持跨库数据库连接以及其它跨库查询，如果您需要Union或是Join来自多个数据库的数据，你只能通过在应用程序层实现。 
    * **CLR对象** ：SQL Database当前并不支持CLR存储过程、聚合、触发器和函数。如果您需要实现上述这些功能，只能通过在SQL Database中使用Transact-SQL来实现。例如聚合等复杂的聚合或操作无法通过在数据库层面使用Transact-SQL实现的，你需要将这部分功能移到应用程序层。 
    * **数据类型** ：SQL Database并不支持一些SQL Server的系统数据类型。最新的相关信息，请在MSDN中查看[Data Types \(SQL Database\)](http://msdn.microsoft.com/en-us/library/windowsazure/ee336233.aspx)。 
    * **复制** ：SQL Database并不支持例如事务日志复制和合并复制等复制类型，对于上述复制类型您可以在Windows Azure虚拟机上运行的SQL Server中实现。您还可以使用SQL数据同步服务来同步SQL Database实例之间的数据。但SQL Data 同步服务或许不能解决事务日志一致性和数据冲突的问题。**警告** :SQL Data同步服务当前还只是Preview版本，这意味这当前只是为了未来的版本收集反馈，因此不应该被用到生产环境中。 
    * **全文索引** :Windows Azure SQL Database当前还不支持全文索引。如果您的应用程序使用了全文索引，您可以考虑将程序迁移到Windows Azure虚拟机的SQL Server中。更多关于Windows Azure虚拟机中的SQL Server预览版的相关信息，请看:[Migrating to SQL Server in a Windows Azure Virtual Machine](http://msdn.microsoft.com/en-us/library/windowsazure/jj156165.aspx)。 
    * **授权** ：SQL Database按照数据库大小按月收费，但是对于运行在Windows Azure SQL Database中的SQL Server是需要授权的。 
    * **登录和安全** ：SQL Database不支持Windows验证方式，但是在Windows Azure虚拟机中是支持的。更多关于安全的指导方针和SQL Database中有关安全的限制，请看[Security Guidelines and Limitations \(SQL Database\)](http://msdn.microsoft.com/en-us/library/windowsazure/ff394108.aspx)。 
    * **功能的区别** ：更多关于SQL Server和SQL Database的相同点和不同点，请看[SQL Database Overview](http://msdn.microsoft.com/en-us/library/windowsazure/ee336241.aspx)。 
  * **登录和用户安全** ：随着Windows Azure中新的网络功能的提升，您可以将企业内部的活动目录域扩展到Windows Azure。更多信息，请看[Migrating with Windows Azure Virtual Machines](http://msdn.microsoft.com/en-us/library/windowsazure/jj156159.aspx)。关于SQL Database安全管理的细节信息，请看[Managing Databases and Logins in SQL Database](http://msdn.microsoft.com/en-us/library/windowsazure/ee336235.aspx)。 
  * **按功能将应用程序分块** :找出程序中可以按功能分割的单元进行分割，这样就可以将这些不同的单元分到不同的Windows Azure角色或虚拟机中。这样做的好处是程序更容易进行弹性扩展，并且程序更容易和其它程序整合，对于云计算来说，这种分块更加合适。 
  * **支付卡行业（PCI）和其它需求** :再将应用程序或程序的模块迁移到Windows Azure之前，首先检查当前业务所需的证书符合规范，您或许需要在迁移到Windows Azure之前移除程序或是数据库的一部分，然后程序运行在混合模式下。这使得您程序的部分在遵循业务规范的情况下程序的其它部分仍然可以享受到Windows Azure和云计算所带来的好处。 
  * **程序中无法在Windows Azure平台上运行的关键模块** :由于某些原因，您或许不能将您程序中的部分程序迁移到公有云中。找出这些模块，使用混合构架，您可以将非关键的模块迁移到Windows Azure中而从而享受到Windows Azure和云计算带来的好处，同时您仍然可以使得程序的关机部分符合行业内的规范。 



### 为迁移各部分计划制定时间规划

当您确定所需迁移的部分之后，迁移计划中的每一步就变得很清晰。查看每一步中涉及的程序和数据并对此评估所需的时间和开发、测试和迁移所需的资源。当将您的程序分解之后，并行开发这些分解后的模块以适应弹性扩展构架。

在您的迁移计划中设置项目里程碑，比如说功能和性能测试，发布日期等。您的迁移计划可能由一系列步骤进行迭代直到所有的模块都已经为迁移到Windows Azure准备就绪。

### 规划迁移过渡期

当开发和迁移的时间规划设立好之后，要找出需要对当前程序和基础构架做的改变和所需的时间。这类计划可以使得在迁移完成之前程序可以正常运转。当做这份过渡计划时，找出当前系统最麻烦的地方并给出使得迁移过程中业务可以正常运转的解决方案。除此之外，找出使得业务正常运转所需的工作，通常来说这类工作往往非常简单，比如说调优一个SQL查询语句或是基于您的应用程序特性添加一个web服务器依赖。做一个应对突发突发的计划以避免预料之外的增长或负载。当做这类应对突发事件的计划时，看看是否可以将这类负载横向扩展到Windows Azure的虚拟机中以避免不必要的硬件投资。

### 规划测试

任何迁移计划都应该包括广泛的功能测试和负载测试。对于测试方法的概述超过了本文所涉及的范围。下面的列表展示了当测试时应该牢记的关键点:

  * 自动化测试脚本 
  * 测试程序的所有层和模块 
  * 按照程序正常应有的负载进行负载测试 
  * 按照您对程序的最高期望进行测试 



我们推荐您为建立和运行并修复测试所发现的错误规划时间。

### 找出所需的资源

当确定了业务和技术需求之后，找出迁移所需的资源。这些都是您在迁移过程中所需要的。这些资源从三个方面来看:

  * **人事上** :为了迁移成功，您或许需要拥有不同专业技能的各类人参与到程序迁移的过程。除此之外，迁移之后技术人员的技能需要更新，角色需要改变。比如说，考虑设立一个账户和服务管理员来管理登录名、访问权限、服务以及扩展等级。 
  * **工具上** ：找出开发、测试和部署Windows Azure程序所需的工具，更多信息，请看[Windows Azure Tools for Microsoft Visual Studio](http://msdn.microsoft.com/library/ee405484.aspx) and [Tools and Utilities Support \(SQL Database\)](http://msdn.microsoft.com/en-us/library/windowsazure/ee621784.aspx)。 
  * **咨询** ：您或许需要特定专家来帮助您进行迁移。迁移专家或许会帮您避免走歪路来节省大量的时间和钱。 



### 规划在Windows Azure上的程序管理

对于小型程序来说，Windows Azure Management Portal或许就足够来管理Windows Azure的部署。Windows Azure Management portal可以允许您近路并管理包括改变实例角色的数量、管理SQL Database实例等管理和部署工作。然而，对于复杂的程序和为客户提供服务的程序来说，Windows Azure Management portal 可能就不够了。

Windows Azure开放了REST API使得您可以通过编程的方式对程序和在Windows Azure上的虚拟机以及对Windows Azure storage的管理。您也可以自己写一个管理界面来规划和检测您的Windows Azure环境。您的迁移计划应该包括在迁移之后对程序的管理，尤其是这部分管理还包括自定义界面和自动化。

更多有关REST API对于Windows Azure部署的管理，请看[API References for Windows Azure](http://msdn.microsoft.com/library/ff800682.aspx)。

\-----------------------------------

本文翻译自Windows Azure官方指南，全部系列翻译完后会集结成PDF放在Technet的Community Content中。
