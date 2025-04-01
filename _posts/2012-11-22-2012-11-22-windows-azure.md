---
layout: post
title: "【译】实现为Windows Azure制定的迁移计划"
date: 2012-11-22
categories: blog
tags: [博客园迁移]
---

Windows Azure是一个由微软数据中心提供的一个Internet级别的计算和服务平台。因为通过使用Windows Azure,微软会维护所有底层的操作系统、硬件、网络、存储资源并且会不断的更新这个平台，因此开发和系统管理人员不再需要为底层的软件和硬件基础构架操心。

由于Windows Azure和企业内平台有很大的区别。我们强烈推荐您在将程序迁移到云端之后，就像新部署程序时一样对程序进行功能和性能的测试。您需要在实现迁移的过程中考虑下述重要部分：

  * 构建验证测试环境 
  * 同步数据库以减少转移时间 
  * 备份和还原 
  * 转移到Windows Azure 



本篇主题的重点是Windows Azure Cloud Services.而关于将SQL Server迁移到Windows Azure虚拟机的初步指导，请参阅[Migrating with Windows Azure Virtual Machines](http://msdn.microsoft.com/en-us/library/windowsazure/jj156159.aspx)。

### 构建验证测试环境

在将程序迁移到云端的时候，您必须知道如何测试和调试您的程序以便保证您的程序在云端和在本地一致。下述列表展示了您可以用于测试您的程序的方法：

  * **Windows Azure Tools for Microsoft Visual Studio** :在您创建程序后，您可以使用计算和存储模拟器在本地对程序进行调试。这使得您可以在将程序发布到Windows Azure之前在本地开发程序。Windows Azure Tools for Microsoft Visual Studio对Visual Studio 2010进行扩展使得额外添加的计算和扩展模拟器包含了Windows Azure的大部分功能，从而您可以在本地对程序进行测试。我们推荐您在功能测试的早期就进行这类测试。更多信息，请参阅:[Windows Azure Tools for Microsoft Visual Studio](http://msdn.microsoft.com/library/ee405484.aspx)。 
  * **SQL Server数据工具** :SQL Server Data Tools \(SSDT\) 在Visual Studio 2010中提供了集成开发环境，您可以使用这个工具来设计数据库、创建和编辑数据库对象和数据，或是对其支持的所有SQL平台执行查询语句;这包括在云端的Windows Azure SQL Database和非云端的Microsoft SQL Server 2012。这个工具允许您检查程序中数据访问模块。无论这部分数据是本地默认数据库还是Windows Azure SQL Database,这个工具都可以用来测试您的数据库项目解决方案。更多信息，请参阅[SQL Server Data Tools](http://msdn.microsoft.com/library/bb401006.aspx):**注意** :Windows Azure Tools for Microsoft Visual Studio和SSDT都可以用于对在线和离线的数据源进行基本的功能和兼容性测试。但是为了真正从功能、性能可扩展性的角度测试运行在云端的程序，您还需要在您程序运行的Windows Azure上进行测试。 
  * **自动化测试框架** :很多程序已经存在可以用来保证程序的模块和功能正常工作的自动化测试框架。当程序在Windows Azure上运行时，这类自动化测试框架是否可以正常运行取决于这类框架是如何设计的。如果这类框架需要在企业内部运行但可以通过定义好的端点连接Windows Azure，这类框架就有可能在云端正常工作。否则，我们建议您将自动化测试框架和程序本身都迁移到Windows Azure上以避免丢失连接和网络延迟问题。 
  * **Visual Studio负载测试** :如果程序当前并不存在自动化测试框架，我们推荐您创建一个新的自动化测试框架并使用Visual Studio负载测试来模拟多用户负载。更多信息，请参阅:[Using Visual Studio Load Tests in Windows Azure Roles](http://msdn.microsoft.com/en-us/library/windowsazure/hh674491.aspx)。 



### 同步数据库以减少转移时间

您应该尽量减少在测试、数据移动和生产之间的转换时间。将企业内部的数据上传到Windows Azure可能会需要数个小时甚至数天。您不会希望在这段时间内您的程序不可用。这也是为什么您需要一个减少停机时间的计划。注意转移时间意味着将企业内部程序迁移到Windows Azure的最终步骤所需的时间。在转移之前，看看哪些表中的数据在迁移过程中不改变而哪些表中的数据在迁移的过程中可能改变。对于静态数据来说，您不需要在转移时间内转移这部分数据，如果您不能确定某些特定表中的数据是否会在转移时间内改变，您应该在系统中添加将改变的数据迁移到云端的程序。我们还推荐您考虑是否所有企业内部的数据都需要迁移到云端才能使得在Windows Azure上的程序上线。如果您的程序只有部分数据存在云端就能上线，那就会大大减少停机时间。

但如果是程序在Windows Azure上线之前，云端数据需要和企业内部数据保持一致，那就考虑减少在转移时间内所转移的数据量。在某些情况下，可以在转移时间之前就先转移部分数据，在实际的转移时间内转移另外一部分数据。在这种情况下，您需要区分哪些数据是可以提前转移的，而哪部分数据需要在转移时间内转移，这样做的好处是允许您的程序在Windows Azure中上线的过程中因为只转移部分数据而减少停机时间，您可以使用下述方式在转移时间之前同步数据:

**Windows Azure SQL Data Sync**

**** Windows Azure SQL 数据同步服务提供了为Windows Azure SQL Databases同步数据的功能，这个服务目前有两个主要功能:

  * 同步企业内部的SQL Server数据库和Windows Azure SQL Database实例之间的数据，使得企业内部和基于云端的程序可以使用相同的数据。 
  * 同步Windows Azure SQL Database实例之间的数据，被同步的实例可以在同一个数据中心，不同的数据中心，甚至是不同的区域。 



对于下述情况，用Windows Azure SQL 数据同步服务来同步企业内部数据库和Windows Azure SQL Database实例之间的数据是一个很好的选择:

  * 您需要对程序进行并行测试。 
  * 在将企业内部的所有数据迁移到Windows Azure之前您的程序需要继续运行，在迁移之后将这部分改变的数据迁移到Windows Azure。 
  * 在迁移到Windows Azure之前，您企业内部的程序需要继续运行，同时还需要减少停机时间。 
  * 程序同时使用了云端和企业内部数据库作为混合解决方案的。 



值得注意的是，SQL Data同步服务使用改变跟踪表用于跟踪被改变的表来使得这些改变的数据被同步。当使用SQL数据同步服务时，您必须为这个改变跟踪表预留空间。除此之外，您最好不要修改被同步表的表结构或是主键，除非您重新初始化同步组。但对于需要中介和实时数据同步的情况下SQL Data同步服务就不是那么理想了，更多信息，请参阅[SQL Data Sync](http://msdn.microsoft.com/en-us/library/windowsazure/hh456371.aspx)。警告:SQL Data Sync当前仅仅是预览版，仅仅是为了未来的版本收集反馈信息，所以不应该被用到生产环境中。

**复制、镜像、事务日志传送**

您可以使用复制、镜像、事务日志来将企业内部的一个SQL Server实例中的数据同步到另一个企业内部的SQL Server实例或是Windows Azure虚拟机上的实例。但是这些选项都不能将数据移入或移出Windows Azure SQL Database中。更多信息，请参阅:[Replication and Log Shipping](http://msdn.microsoft.com/library/ms151224.aspx) and [Database Mirroring and Log Shipping](http://msdn.microsoft.com/library/ms187016.aspx)。

**自定义抽取、转换、装载\(ETL\)**

为了减少在转移时间内转移数据所需的时间，您应该尽量在转移时间之前尽可能多的转移数据。您可以使用自定义ETL job来将那些被改变的数据从企业内部的SQL Server转移到Windows Azure环境中。当从SQL Server 2008之后的版本中迁出数据时，我们推荐使用CDC功能来确保仅仅那些改变的数据从企业内部的数据库中转移到Windows Azure SQL Database实例中。更多关于CDC的信息，请参阅BOL上的[Track Data Changes](http://msdn.microsoft.com/library/bb933994\(v=sql.110\).aspx)。但对于那些没有CDC的数据库，您需要创建一个数据跟踪系统来追踪那些被迁移之后改变的数据。总之，在实际的转移时间迁移最小量的数据会大大减少停机时间。

**导出数据层应用程序\(DAC\)**

通过DAC,您可以将SQL Server实例中的数据导出并将其存入Windows Azure Blob 存储中并稍后还原到Windows Azure SQL Database。通过DAC，您可以设置只有需要的表被导入或导出的表级别过滤器，但无法设置行级别的过滤器。这也是为什么DAC适合整个表都在单独数据库中的情况而不适合联合数据库。DAC还不适合需要实时同步的程序，更多信息，请在BOL中参阅[Export a Data-tier Application](http://msdn.microsoft.com/library/hh213241\(v=sql.110\).aspx)。

### 备份和还原

创建数据库备份是为了从管理错误、程序错误以及数据中心中出问题导致的数据丢失中进行还原。在Windows Azure SQL Database中备份和还原数据和在企业内部的SQL Server中并不一样，因此需要和可用的资源和工具共同使用。因此为了进行可靠的恢复而进行的备份还原Windows Azure SQL Database就需要一个的备份和还原策略。需要Windows Azure SQL Database进行数据恢复的场景主要分为下述三类:

  * **基础构架和硬件失败** :数据中心可能出现硬件故障，比如说为您的数据提供Windows Azure SQL Database服务的硬件节点故障。 
  * **程序或用户所产生的问题和故障** :用户或程序有可能对数据产生意料之外的操作，这类操作需要进行恢复。比如说，某个用户错误的修改了一个客户的信息，等等。 
  * **数据中心设备损坏** :当前的Windows Azure SQL Database服务协议指定了在微软控制之外的原因比如说灾难发生所导致的问题是免责的。在灾难发生时，数据中心可能出现数据库无法从复制或是在线备份中恢复的损害。 



最终您需要决定对于存储在Windows Azure SQL Database数据中心的数据能够损失的程度。有关可用备份和还原工具以及围绕其所建立的灾难恢复策略，请参阅MSDN中的[Business Continuity in SQL Database](http://msdn.microsoft.com/en-us/library/windowsazure/hh852669.aspx)。

### 转移到Windows Azure

当您真正开始将您的程序迁移到Windows Azure时，您可以遵循下述两种方式:

  * **并行运行** :使用这种方式，您的程序同时在企业内部和Windows Azure上运行。这使得您可以在程序完全依赖云端运行之前在Windows Azure进行在线测试。您的测试应该包含但不仅限于:功能测试,性能测试,扩展性测试。当完成对Windows Azure上新系统的完整测试后，将剩余部分数据迁移到云端，最终关闭企业内部的系统。 
  * **暂停和转移** :这种方式适用于系统在Windows Azure上线之前所有的数据都需要被同步。使用这种方式需要首先完成在Windows Azure上的功能和性能测试，然后使用上面提到的数据同步方式将数据同步到Windows Azure。我们推荐本地和云端的数据尽量保持一致以减少最终数据同步或ETL操作所需的时间。最终转移到Windows Azure时，关闭企业内的系统，并做最后一次数据同步，然后将Windows Azure上的程序上线。 



\-----------------------------------

本文翻译自Windows Azure官方指南，全部系列翻译完后会集结成PDF放在Technet的Community Content中。
