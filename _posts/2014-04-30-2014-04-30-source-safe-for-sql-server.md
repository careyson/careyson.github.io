---
layout: post
title: "使用Source Safe for SQL Server解决数据库版本管理问题"
date: 2014-04-30
categories: blog
tags: [博客园迁移]
---

### 简介

在软件开发过程中，版本控制是一个广为人知的概念。因为一个项目可能会需要不同角色人员的参与，通过使用版本控制软件，可以使得项目中不同角色的人并行参与到项目当中。源代码控制使得代码可以存在多个版本，而不会将代码库变得混乱，典型的场景包括Bug修复、添加新功能、版本整合等。

虽然在开发层面的版本控制软件已经非常成熟，但目前国内还没有专门针对数据库层面的版本控制软件来帮助不同角色的人员在数据库层面进行团队协作、变更代码管理以及对数据库的变更进行查看和比对。在数据库层面版本控制工具的缺乏可能会出现如下场景：

  * 无法在数据库层面进行团队协作：开发人员A对存储过程的修改导致开发人员B创建的存储过程被覆盖，从而无法比对和追踪 
  * 开发人员-开发DBA-测试人员难以协作：SVN等版本工具是基于文件的，很难在数据库层面进行版本控制 
  * 数据库发生的变更难以追踪：现有的技术无法追踪由谁、在什么时间、对数据库修改了什么，当发生由数据库引起的报错或性能下降时，难以排查 
  * 无法记录对数据库变更的过程资产：数据库变更的历史记录只有数据库运维人员了解，当该相关人员离职或调岗，这些过程资产难以继承 
  * 难以审计数据库：现有的数据库审计功能往往依赖于日志，对性能造成很大影响。 
  * SQL脚本无法有效管理：现有的做法往往是将SQL以文件形式保存，无法有效管理和共享 
  * 无法查看被加密的数据库对象：当需要对加密的数据库对象进行修改时，如果无法找到对象定义的原始记录，则必须重写该对象 
  * SVN建立和使用复杂：SVN使用流程对于数据库人员过于繁琐，为数据库人员增加了额外的工作负担 



由于数据库是整个业务应用的核心，上述问题无论是在开发环境还是在生产环境如果得不到有效的解决，会造成生产力低下、过程资产无法得到管理、数据库审查无法进行、难以排查由数据库变更导致的问题等情况。

下面来介绍一下Source Safe for SQL Server如何解决该类问题。

### 软件的安装

[软件的官网](http://www.grqsh.com/products.htm?tab=sourcesafe-for-sql-server)下载完Source Safe的安装包后一路下一步，安装完成后打开Management Studio，在需要加入到源代码控制器的某个数据库服务器上右键，在弹出菜单中选择“添加数据库到版本控制”，如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923037671511.png)](//images0.cnblogs.com/blog/35368/201404/300923022056467.png)

图1.将数据库添加到版本控制

然后设置相关的选项，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923064861943.png)](//images0.cnblogs.com/blog/35368/201404/300923050806712.png)

图2.添加数据库到版本控制相关设置

现在再来看，整个数据库都已经在版本控制之下了，如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923092985701.png)](//images0.cnblogs.com/blog/35368/201404/300923077982443.png)

图3.查看受版本控制的数据库

至此，Source Safefor SQL Server就安装配置完成了。

### 典型应用场景

Source Safe可以解决下述问题：

**开发团队进行版本控制**

在一个开发团队中，对于数据库对象的每一次变更都会自动覆盖上一个版本，导致上一个版本对象定义的丢失。比如说开发人员A创建了存储过程“ProcA”，然后开发人员B修改了存储过程“ProcA”，开发人员A创建的存储过程将会被开发人员B所做的修改覆盖，造成之前定义存储过程的丢失和无法回滚。使用Source Safe可以轻松解决该类问题。

通过图4，我们看到存储过程“ProcA”由开发人员“Jack”创建后，开发人员“CareySon”对其进行了修改，Source Safe可以完整的记录由谁，在什么时间，做了哪些修改，如图所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923110028488.png)](//images0.cnblogs.com/blog/35368/201404/300923099558301.png)

图4.查看存储过程“ProcA”被修改的历史记录

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923136421961.png)](//images0.cnblogs.com/blog/35368/201404/300923122983218.png)

图5.查看存储过程 “ProcA”两个版本的差异部分

**开发里程碑标记**

在开发过程中，往往需要对开发里程碑进行迭代，每一个开发里程碑导致的数据库对象变更都可以完整的被记录和文档化。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923165489449.png)](//images0.cnblogs.com/blog/35368/201404/300923150339420.png)

图6.里程碑版本以及涉及到的对象变更

**生产环境变更管理**

在生产环境中，程序的升级、程序或人为对数据库对象的更改有可能导致数据库出现问题，例如应用程序报错或数据库性能下降。通过SourceSafe可以快速比较出数据库之前版本和当前数据库定义中存在差异的部分，并根据具体情况回滚导致数据库出现问题的对象，从而快速排除错误并保证数据库持续稳定运行。如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923200021038.png)](//images0.cnblogs.com/blog/35368/201404/300923179554679.png)

图7.选择需要版本比较的对象

**常用脚本管理**

无论是开发人员还是数据库的运维人员，都会有常用脚本需要保存。过去的做法往往是将SQL代码以文件的形式保存，这样既不方便使用，也不方便分类管理。利用Source Safe的代码管理功能，可以方便的将SQL代码的管理无缝集成到SQL Server Management Studio中。如图8所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923220339625.png)](//images0.cnblogs.com/blog/35368/201404/300923210026210.png)

图8、使用Source Safe的脚本管理功能对SQL进行管理

此外，Source Safe特别设定了默认文件夹“工具栏快捷方式”，用户可以将频繁使用的SQL代码置于此处，在该分类下的脚本会自动出现在Management Studio的工具栏中，如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923262201371.png)](//images0.cnblogs.com/blog/35368/201404/300923241735012.png)

图9、将常用脚本置于“工具栏快捷方式”中

**对选定的对象进行版本归类**

虽然Source Safe每次同步之后都会生成一个基于变更的版本号，但在某些特殊情况下，比如需要对库中某些变更进行管理、对库中的版本进行归类的情况下会需要额外的标签。如图10所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923332675590.png)](//images0.cnblogs.com/blog/35368/201404/300923310487945.png)

图10、利用标签标出某个业务版本涉及到的数据库对象

**与SVN的无缝集成**

SourceSafe的版本内容和历史记录可以直接导出到SVN、TFS、VSS中，从而打通数据库版本控制和现有的SVN系统。在数据库中我们对存储过程dbo.TestProc做了三次变更，如图11所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923376429092.png)](//images0.cnblogs.com/blog/35368/201404/300923365958906.png)

图11.对存储过程的3次变更

接下来将历史记录导出到SVN，如图12所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923396738680.png)](//images0.cnblogs.com/blog/35368/201404/300923390029308.png)

图12.将SourceSafe记录导出到SVN

导出完成后，通过SVN客户端软件可以看到对应SQL文件的在数据库中对应图10的三次变更，如图13所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-04-30-source-safe-for-sql-server/source-safe-for-sql-server-300923426736197.png)](//images0.cnblogs.com/blog/35368/201404/300923408921153.png)

图13.SVN对应SourceSafe中的3次变更

### 软件的下载

软件的下载可以在软件的官网下载，下载地址请[猛击这里\(http://www.grqsh.com/products.htm?tab=sourcesafe-for-sql-server\)](http://www.grqsh.com/products.htm?tab=sourcesafe-for-sql-server)。
