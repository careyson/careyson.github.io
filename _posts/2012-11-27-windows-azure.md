---
layout: post
title: "Windows Azure虚拟机概览"
date: 2012-11-27
categories: blog
tags: [博客园迁移]
---

Windows Azure自从2012预览版开始添加了新的虚拟机功能。作为这个新功能的一部分，Windows Azure发布了一个新版本的Windows Azure管理门户,这个门户在原有的基础上增加了额外的新功能。

这篇文章提供了作为Windows Azure中提供新服务的新基础构架的预览。

  * Windows Azure虚拟机 
  * Windows Azure虚拟网络 
  * 迁移Windows Azure虚拟机需考虑事项 
  * 使用Windows Azure虚拟机时的高可用性和灾难恢复 



### Windows Azure虚拟机

您可以使用下述三种方法之一在Windows Azure中创建虚拟机:

  * **使用平台提供的虚拟镜像** :您可以直接使用由Windows Azure管理门户提供的镜像画廊作为模版创建您自己的虚拟机。使用这种方法不需要上传任何您在本地创建的Windows Server或是Linux镜像。您可以通过管理门户，PowerShell或是可编程的API接口（REST）甚至是为Mac或Linux桌面提供的命令行程序。当虚拟机创建成功后，您可以登录到虚拟机并对其进行管理。对于运行Windows Server曹旭哦系统的虚拟机来说，您可以在管理门户中点击“连接”按钮来开始远程桌面连接。对于运行Linux操作系统的虚拟机，您可以使用安全Shell\(SSH\)客户端来登录，关于如何在Windows,Max,Linux创建、部署、管理虚拟机的详细信息，请参阅WindowsAzure.com网站。

  * **使用您自己的镜像** :您可以使用由Windows Azure软件开发包（SDK）所提供的CSUpload命令行工具来上传作为镜像的VHD文件到Windows Azure。您仅仅需要将镜像上传到您的Blob存储账户后使用这个镜像来实例化一个虚拟机。更多信息，请参阅[Creating and Uploading a Virtual Hard Disk that Contains the Windows Server Operating System](https://www.windowsazure.com/en-us/manage/windows/common-tasks/upload-a-vhd/)。

  * **使用您自己的磁盘** :操作系统镜像实际上就是一个您可以用于作为模版创建虚拟机的虚拟硬盘文件。镜像仅仅是一个文件是因为其并没有设置诸如用户账户信息等配置文件。但是如果您的程序需要一些已经在本地配置好的的配置信息才能运行您或许就不能通过模版创建虚拟机文件了。在这种情况下，您可以使用CSUpload命令行工具上传作为磁盘的VHD文件。举个例子，您的磁盘中已经安装了SQL Server,此时如果您依然从模版创建虚拟机，那您就的负责授权文件的配置。




在您初始化虚拟机镜像之后，您就需要为操作系统和软件的打补丁、配置和维护。Windows Azure会定期更新Windows Azure平台提供的基本镜像文件。但是Windows Azure并不会强制已经由客户部署的操作系统对应升级。类似的，Linux系统镜像也会定期更新。更多关于价格的详细信息和服务级别协议，请在WindowsAzure.com参阅Windows Azure法律信息。注意您可以在下面列表中查看有关镜像和磁盘定义的重要信息。

下述列表是在Windows Azure上运行的虚拟机所支持的程序。

程序 | 细节  
---|---  
Microsoft SQL Server | 

  * 您上传的镜像所支持的版本: SQL Server 2008, SQL Server 2008 R2, and SQL Server 2012所有版本 
  * 镜像画廊致辞后的版本: SQL Server 2012评估版 
  * 支持的程序: SQL Server Database Engine, SQL Server Analysis Services, SQL Server Reporting Services, SQL Server Integration Services, SQL Server 管理工具, SQL 连接 SDK, SQL Server安装升级和迁移工具，比如DAC，备份，还原，分离和附加，注意主数据服务当前还不支持。 

  
Windows Server 活动目录 | 支持版本:Windows Server 2008 R2。  
Microsoft SharePoint | 支持版本:SharePoint 2010 的所有版本。  
Linux Support | 您可以上传一个Linux虚拟硬盘\(VHD\)文件到Windows Azure中，更多关于Windows Azure支持Linux的版本的信息，请参阅Windows Azure管理门户 。  
  
对于最新关于Windows Auzre虚拟机中支持的微软的软件信息，请参阅[微软服务器软件支持部门](http://support.microsoft.com/kb/2721672)。

关于虚拟机的基础信息，请参阅MSDN中关于[虚拟机](http://msdn.microsoft.com/en-us/library/windowsazure/jj156003.aspx)的主题。

关于如何在Windows Azure中管理虚拟机的细节信息，请参阅管理中心，这部分信息也可以在WindowsAzure.com网站下载到。站点中还有how-to指南，PowerShell命令集合以及您可以在Windows,Mac,Linux平台上使用的命令行工具。您还可以使用REST API和PowerShell命令行工具来管理您的程序和虚拟机。更多洗洗，请在MSDN中参阅WIndows Azure服务管理API参考和Windows Azure管理命令集合。

**重要概念的列表**

  * 操作系统镜像是一个您可以用来作为模版创建新的虚拟机的虚拟硬盘文件。镜像被成为模版是由于其上不像配置好的虚拟机那样有特定的配置，这些配置包括电脑名称和用户账户设置。 
  * 虚拟机磁盘是可以被当作一个当前的操作系统装载和启动的虚拟硬盘。磁盘还可以被作为独立于操作系统磁盘的磁盘附加到一个运行中的实例中。当您在Windows Azure管理门户创建了一个虚拟机之后就会默认为操作系统创建一个磁盘。我们推荐您为您的数据和日志文件创建一块额外的磁盘。更多信息，请参阅[How to Attach a Data Disk to a Virtual Machine](https://www.windowsazure.com/en-us/manage/windows/how-to-guides/attach-a-disk/) 和 [How to Detach a Data Disk from a Virtual Machine](https://www.windowsazure.com/en-us/manage/windows/how-to-guides/detach-a-disk/)。 
  * 您可以将正在运行的虚拟机捕获为一个镜像，但这个操作并不会捕获附加磁盘。被捕获的虚拟机可以用于创建多个虚拟机。最终结果是在相同的存储账户中多了一个刚捕获的虚拟机操作系统所在磁盘的镜像。更多关于捕获虚拟机的镜像的相关信息，请参阅[How to Capture an Image of a Virtual Machine Running Windows Server 2008 R2](https://www.windowsazure.com/en-us/manage/windows/how-to-guides/capture-an-image/) 和 [How to Capture an Image of a Virtual Machine Running Linux](https://www.windowsazure.com/en-us/manage/linux/how-to-guides/capture-an-image/)。 
  * 一个Windows Azure程序可以存在多个虚拟机。您在Windows Azure中创建的虚拟机都可以和在同一个Could Service或是虚拟网络的其它虚拟机使用私有网络通道进行交互。Windows Azure允许您在这多个虚拟机之间进行负载均衡。[Windows Azure Training Kit](http://www.microsoft.com/en-us/download/details.aspx?id=8396)中 _ntroduction to Windows Azure Virtual Machines Hands-on-Lab_ 这篇文章阐述了如何连接到多个Windows Azure虚拟机,除此之外，您还应该看看下面的指南: 
    * [How to Connect Virtual Machines in a Cloud Service](https://www.windowsazure.com/en-us/manage/windows/how-to-guides/connect-to-a-cloud-service/)
    * [How to Set Up Communication with a Virtual Machine](https://www.windowsazure.com/en-us/manage/windows/how-to-guides/setup-endpoints/)
    * [Load Balancing Virtual Machines](https://www.windowsazure.com/en-us/manage/windows/common-tasks/how-to-load-balance-virtual-machines/)



### Windows Azure虚拟网络

作为新的Windows Azure预览版功能的一部分，Windows Azure提供了一个新的网络虚拟化集合以及基于VPN跨域的站点到站点的网络。您可以通过Windows Azure管理门户或是一个网络配置文件来提供和管理虚拟网络。Windows Auzre虚拟网络提供了下述功能:

  * **在云端的分支办事处或是专用的私有虚拟网络** :您可以通过VPN将您企业网络的一部分扩展到Windows Azure上。通过配置VPN设备连接到Windows Azure VPN网关，您可以为您的企业网络和Windows Azure之间建立一个安全的站对站连接。您在Windows Azure上的虚拟机可以加入到您运行在企业内部的域。更多关于建立安全的跨域解决方案的信息，请参阅:[Windows Azure Virtual Network](http://msdn.microsoft.com/library/windowsazure/jj156007.aspx) and [About VPN Devices for Virtual Network](http://msdn.microsoft.com/library/windowsazure/jj156075)。 
  * **为虚拟机配置静态的IPV4地址** :您可以为您在Windows Azure上运行的虚拟机设置IPV4地址空间。当您创建虚拟网络时，你可以为机器指定IPV4地址空间。虚拟机接收的IP地址是静态的并且不会随着虚拟机的重启而改变。IP地址会被DNS记录并且您可以通过主机名来连接虚拟机。更多关于创建虚拟网络的信息，请参阅:[Windows Azure Virtual Network](http://msdn.microsoft.com/library/windowsazure/jj156007.aspx)。 
  * **对于虚拟网络的名称解析\(DNS\)** :有很多方式可以为您的虚拟网络提供名称解析。您可以使用Windows Azure的名称解析方案或是您可以使用自己的DNS服务器。更多关于名称解析和Windows Azure的解决方案，请参阅:[Windows Azure Virtual Network](http://msdn.microsoft.com/library/windowsazure/jj156007.aspx) 和 [Windows Azure Name Resolution Overview](http://msdn.microsoft.com/library/windowsazure/jj156088.aspx)。 
  * **Windows Azure虚拟机上的活动目录** : 您可以在云上利用企业内部现有的活动目录和DNS服务器。Windows Azure虚拟机特性允许您通过企业内部的活动目录服务使得运行在Windows Azure上的虚拟机加入到企业内部的域。更多信息，请参阅:[Guidelines for Deploying Active Directory on Windows Azure Virtual Machines](http://msdn.microsoft.com/en-us/library/jj156090)。



下图展示了Windows Azure虚拟机使得客户可以轻松的将企业网络延伸到Windows Azure上。这使得将现有的程序迁移到Windows Azure上变得很有优势。您可以更简单的支持横跨云端和企业内部的混合应用程序。您还可以管理Windows Azure中您自己的虚拟网络并通过VPN网关建立企业内部和云端的连接。因此您就可以使运行在Windows Azure上的虚拟机加入到运行在企业内部的域。

如图所示，在Windows Azure虚拟网络中，您可以设立活动目录域并开启DNS服务同时SQL Server安装在另一个虚拟机中。然后您的程序代码可以托管到在另一台Windows Azure虚拟机中Windows Azure Web角色中。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-11-27-windows-azure/windows-azure-201211270923038106.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201211/201211270923024419.gif)

关于更详细的虚拟网络指南以及How-to指南，请参阅WindowsAzure.com的[Networking](https://www.windowsazure.com/en-us/manage/services/networking/)。

### 当迁移到Windows Azure虚拟机时需要考虑的方面

使用Windows Azure虚拟机可以消除程序对某些资源的依赖。您可以将应用程序直接作为虚拟机迁移以便快速直接的利用Windows Azure的优势。除此之外，您可以连接诸如Web Sites或是Cloud Services Web或是Worker角色的虚拟机。

下面例子是可以利用Windows Azure优势的一些模式:

  * 迁移存在的非关键数据库程序
  * 由于Windows Azure SQL Database并不支持SQL Server所有的特性，所以将程序部署到虚拟机中的SQL Server当中
  * 为新的数据库应用程序快速简单的部署开发和测试环境
  * 对于企业内部数据库程序的备份方案
  * 对于企业内部高峰期的一个扩展方案
  * 客服企业内部虚拟化平台效率过低的解决方案
  * 对于需要的某些资源比如SQL Server,互动目录，MongoDB，MySQL,SharePoint等依赖于虚拟机的解决方案



当您考虑将企业内部的程序迁移到云平台时，我们推荐您自习的计划好每一步。通常来讲这些步骤会包括分析阶段、应用程序迁移阶段、数据迁移阶段、测试和优化阶段、操作和管理阶段。关于每一个步骤的更详细信息，请参阅:[Overview of the Migration Life Cycle in Windows Azure](http://msdn.microsoft.com/en-us/library/windowsazure/jj156161.aspx)。

我们推荐通过在MSDN中[Migrating to SQL Server in a Windows Azure Virtual Machine](http://msdn.microsoft.com/en-us/library/windowsazure/jj156165.aspx)章节所描述的方式将您的SQL Server数据库以及其中的数据迁移到Windows Azure的虚拟机中。然后，上传和附加包含数据的数据盘到虚拟机中，或是附加一个空盘。您可以使用数据磁盘存储SQL Server的日志和数据文件，比如说看[Windows Azure Training Kit](http://www.microsoft.com/en-us/download/details.aspx?id=8396)的 _Connecting a PAAS application to an IAAS Application with a Virtual Network Hands-on-Lab_ 章节。这个动手实验营讲述了如何附加一个空盘以及如何更新数据库的位置以便使用刚刚附加的空盘。除此之外，您还可以看WindowsAzure.com站点的下述指南：

  * [How to Attach a Data Disk to a Virtual Machine](https://www.windowsazure.com/en-us/manage/windows/how-to-guides/attach-a-disk/)
  * [How to Detach a Data Disk from a Virtual Machine](https://www.windowsazure.com/en-us/manage/windows/how-to-guides/detach-a-disk/)
  * [Provisioning a SQL Server Virtual Machine on Windows Azure](http://www.windowsazure.com/en-us/manage/windows/common-tasks/install-sql-server/)



在Windows Azure虚拟机上的性能取决于多个因此，包括VM的大小、磁盘的数量和配置、网络、数据库软件的配置以及应用程序负载。我们推荐开发人员在不同大小的VM测试性能基线。关于更多在虚拟机中使用SQL Server时需要考虑的性能问题，请参阅:[Running SQL Server in Windows Azure Virtual Machine - Performance Guidelines for Preview](http://sqlcat.com/sqlcat/b/technicalnotes/archive/2012/06/08/running-sql-server-in-windows-azure-virtual-machine-performance-guidelines-for-preview.aspx)。对于虚拟机中使用SQL Server的入门指导，请参阅:[Getting started with SQL Server on a Windows Azure Virtual Machine](http://www.windowsazure.com/en-us/manage/windows/common-tasks/sql-server-on-a-vm/)。

### 使用Windows Azure虚拟机时的高可用性和灾难恢复 

为了给数据和磁盘提供灾难恢复,Windows Azure利用最近发布的Windows Azure Storage中的Geo-Replication功能。所有由程序或者客户对于客户自己磁盘所做的操作都会被保留以便在硬件失败的情况下进行恢复，通过使用Windows Azure Blob Storage,正如在[Introducing Geo-replication for Windows Azure Storage](http://go.microsoft.com/fwlink/?LinkId=243171)这篇博文所述的那样，Windows Azure 中的Blob和表会在同一个大陆上的不同数据中心进行复制，这样就可以在不为客户增加额外成本的基础上提供了额外的数据持久性保障。当启动虚拟机时，Windows Azure Storage会自动将您的操作系统和数据磁盘复制到另一个地理位置。

除此之外，您还要保证虚拟机处于同一个可用集合。同一个可用集合中的多个虚拟机可以保证在网络故障，本地硬盘故障以及计划内的停机故障时程序依然可用。

关于使用在Windows Azure虚拟机中的SQL Server所涉及的高可用性和数据恢复技术,请参阅[Migrating to SQL Server in a Windows Azure Virtual Machine](http://msdn.microsoft.com/en-us/library/windowsazure/jj156165.aspx)。
