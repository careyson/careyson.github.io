---
layout: post
title: "SQL Server Accelerated Database Recovery调研"
date: 2024-02-18
categories: blog
tags: [博客园迁移]
---

# 背景

作为RDS for SQL Server团队，我们给用户提供核心的商业数据库服务，而数据库服务的SLA至关重要，而RTO又是数据库SLA的重要部分，但最近对于一些使用大规格实例的GC6以上客户，出现过一些由于重启/HA导致花费较长时间在数据库恢复过程，从而导致长时间服务不可用，严重影响了我们给用户承诺的SLA，因此我们探索微软提供的最新技术，从原理、测试角度进行评估。

自SQL Server 2019开始，引擎上推出了功能Accelerated Database Recovery（下文全部简称ADR），用于解决大库在重启/HA之后的Recovery过长问题，这个痛点我相信对于Azure来说也同样的痛，所以才有该功能的问世。

在ADR功能出现之前，微软在SQL Server引擎就已经做过减少Recovery时间的努力。比如2016 引入了parallel recovery for secondary replica，但效果一言难尽，甚至我们需要对特定用户通过undocument flag关闭该功能，我们遇到过的问题包括但不限于：

  * parallel线程之间死锁

  * parallel线程hang

  * parallel线程打满，和其他用户库资源争抢导致实例active session过多




历史上我们出现过比较多该类场景，例如出现过某南方大客户10T数据库，重启一次停机3小时，对此我们只能推荐用户从业务上做拆分，当然绝大多数场景这不现实。

因此本文主要是对ADR功能做测试，看未来针对大客户推荐启用该功能，以及对应的Trade off，从而最终帮助客户减少停机时间，满足我们云厂商提供的SLA。

# ADR基本原理

本篇原理，根据论文“Constant Time Recovery in Azure SQL Database”通读解析。

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218114438434-437100089.png)

## 历史

首先，传统的Crush Recovery使用的技术是ARISE机制，也就是基于Write Ahead log做三阶段的Recovery，1992的论文：《A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging》提到的方式，SQL Server、MySQL、DB2都严格使用这种方式，整个生命周期如图描述：

但这种方式最大的问题是恢复时间可能非常长，需要完整的3阶段过程，恢复时间取决于最早的活动事务以及对应需要扫描的事务日志大小。

我以前做DBA的时候，如果避免这种长时间的Recovery都会写到DBA运维规范中，比如我们曾经有过如下规定：

  1. 重启时必须检查活动事务，活动事务存在时间不允许超过1小时

  2. 重启的运维窗口前一小时内不允许做任何运维操作（建索引、重建索引等高消耗动作）

  3. 运维窗口之前通知各业务方停止批量的数据操作，比如ETL操作、跑批操作，洗数据操作。




这些提到的都是主动发起的“计划内运维”，计划外运维，例如宕机等场景，我们只能通过购买昂贵的商业设备尽量保证不出现“计划外停机”，比如更贵的IBM PC Server，存储使用昂贵的EMC等。

## 现状

今天的数据库服务，尤其是云服务，云厂商不可能要求业务方在运维窗口的行为，而控制成本原因以及下层经常需要failover，稳定性也不可能像使用昂贵的商业设备能减少计划外停机的概率，因此数据库内核自身的事故逃逸能力则更为重要。

因此ADR技术，将传统的Arise与MVCC结合，实现快速的Recovery。

### 快照隔离

快照隔离基本上即使行版本控制，当一个事物修改数据后，会直接更新数据，并把老版本的数据存到链表中，老版本的数据与修改数据的事务ID关联，其他并发查询会比对TimeStamp，展示合适的版本数据，如果行版本对应的事务提交，则行版本将不再可见，会被清除，示意图如下：

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218114513084-1957047143.png)

因此启用ADR之后，所有的DML操作都会被行版本存储，该存储会存在用户数据库中，SQL Server内称之为PVS（Persistent Version Store）

SQL Server会存两种数据，一种是In-Row，一种是Off-Row

#### In-Row

In-Row是每次修改仅修改小部分数据，比如一行10列，仅修改一列，那修改只需记录这一列的变化，这种行版本会存储在In-Row Data中，从原理可以看出，这会带来额外的性能成本，因为B-Tree特点，行版本多了导致空间占用多，数据修改可能导致更多的Page-split（同时还要维护B-Tree结构，比如导致父节点Split），对于高频DML这个开销非常高。

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218133921992-2030726554.png)

红字部分是行额外增加的部分，如果一个行本身很长，这个增加可能影响不大，但行如果本身很小，这个成本将会显著提高。

#### Off-Row

如果改动比较大，超过定义的某个阈值，就会将行版本存储在一个额外的存储表中，该表结构没有索引，为并发写入单独优化，当然也有空间占用以及额外的数据操作成本。

#### Logical Revert

每次对于数据的修改，都是存储旧数据到行版本中，并以事务ID关联，因此对于事务回滚，不再需要传统的compensation log，比如，传统的WAL模式如果删除3条数据，对应的回滚示意应该如下：

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218133948292-96897181.png)

可以看到绿色部分会实际进行操作，这也是为什么一个大事务如果回滚，甚至回滚时间会超过已执行时间的原因。

而启用ADR之后，回滚可以变为逻辑回滚

使用逻辑回滚，示意图如下:

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134009935-105405564.png)

相比于通过补偿操作，修改页内数据，该方式在Rollback时，只需要将当前页的指针重新由“Aborted Version”这一页指向上一个事务提交修改的“Commited Version”，这个操作是元数据操作，而不涉及物理的页内数据修改，因此速度应该是几何级提升，验证部分在下文。

同时Aborted Version由于没有引用，变为“Unreferenced Version”，这部分行版本页会被额外的Clean Up现成在后续检查点进行回收。

#### SLOG（Secondary Log）

除了大部分可以版本化的数据之外，还有部分数据无法版本，这类数据包括：

  * 系统元数据页（比如PFS空间分配页）

  * 系统启动使用的关键页数据（这些数据有了才能执行ADR恢复过程）




这部分数据的恢复被单独记录到一个日志流中，相比如传统的事务日志，该部分日志极小，因此扫描成本非常低，例如，一个大事务日志可能上百GB，而该SLOG仅记录对系统数据的修改，因此涉及的操作可能是一些DDL操作，或是对数据库属性的修改操作。

例如曾经做一个经典问题，一个表INT值不够了，要修改为BIGINT，如果做这个DDL变更，需要修改所有表中的数据，一般该操作可能对应几十GB的事务日志，但SLOG仅记录锁和元数据的变更信息，因此成本会非常低。

涉及到SLOG的整体恢复流程如下，相比于使用事务日志进行阶段2和阶段3，使用SLOG成本会低2个数量级，因此恢复时间也同样会低2个数量级。

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134029537-659031423.png)

# ADR验证

## 收益

### 快速Recovery

微软官方文档描述:[https://learn.microsoft.com/en-us/azure/azure-sql/accelerated-database-recovery?view=azuresql](https://learn.microsoft.com/en-us/azure/azure-sql/accelerated-database-recovery?view=azuresql) 已经很清楚了。对于SQL Azure和Management Instance来说，这个ADR是Default On的，我个人认为这意味着该功能相对成熟了。

没有ADR的过程，我们看到Recovery分为3个阶段，第一个阶段由于CheckPoint通常1分钟一次，分析时间最短：

但第二和第三阶段就得看运气了，一个巨大的长事务没有提交可能导致非常长的Recovery时间，例如我的测试实例，我写一个写2000万数据的长事务，在不提交事务的情况下重启：

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134101318-1235697070.png)

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134113637-1052498761.png)

可以看到1阶段 9ms，二阶段156S， 三阶段209S，这段时间加起来就是不可用时间，这还仅仅是我的测试实例，如果用户真有长事务，重启停机时间通常是噩梦。

如果启用了ADR，整个恢复过程

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134123822-1419748656.png)

通过启用ADR，重复上面步骤，发现Recovery时间从364S，变为1S
    
    
    ALTER DATABASE testrecovery SET ACCELERATED_DATABASE_RECOVERY = ON;
    GO

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134155436-2100286891.png)

结论: ADR的确能够将Recovery时间缩短2个数量级。

|  Recovery时间  
---|---  
启用ADR |  1S  
未启用ADR |  365S  
  
### 急速RollBack

没有启用ADR的数据库，插入200万数据

回滚使用了18秒

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134230076-1259919462.png)

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134247434-853105328.png)

下面是启用ADR的截图

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134307515-2072633470.png)

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134319673-16018696.png)

下面是单个SQL插入200万数据的测试语句
    
    
    begin tran
    insert into t11 
    select top 2000000 newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid(),newid() 
    from sys.columns a cross join sys.columns b  cross join sys.columns c
    
    --这里测试Rollback性能
    rollback

|  插入时间 |  回滚时间  
---|---|---  
大量小SQL启用ADR |  324S |  0S  
大量小SQL未启用ADR |  88S |  18S  
单个大SQL启用ADR |  19S |  0S  
单个大SQL未启用ADR |  14S |  15S  
  
### 减少日志占用

我们重新设计一个场景，在启用ADR和非ADR的数据库，启用事务后插入200万事务不提交，在过去这部分活动日志无法被截断，

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-79a778ce-7580-4d4e-a4ff-2b9e0dcb28b8.png)

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-d384ce69-8128-45f8-8650-15fbcc274c6e.png)

可以看到，启用ADR的数据库，活动日志不再会阻塞日志截断

## 成本

### 增加空间占用

前面提到PVS（Persistent Version Store）需要额外的空间，我们将ADR内容放到单独文件组，观察文件组大小，就可以观察PVS的空间。
    
    
    ALTER DATABASE TestRecovery ADD FILEGROUP [VersionStoreFG];
    GO
    
    
    
    ALTER DATABASE TestRecovery ADD FILE ( NAME = N'VersionStoreFG'
    , FILENAME = N'E:\SQLDATA\MSSQL\VersionStore.ndf'
    , SIZE = 8192KB , FILEGROWTH = 65536KB )
    TO FILEGROUP [VersionStoreFG];
    GO
    
    ALTER DATABASE TestRecovery SET ACCELERATED_DATABASE_RECOVERY = ON
    (PERSISTENT_VERSION_STORE_FILEGROUP = [VersionStoreFG]);

通过千万数据插入，并没有发现空间有明显增加的问题，后续需要在复杂场景、高吞吐生产实例上持续观测。

### 增加DML开销

基于“极速Rollback”部分的案例，我们可以看到插入时间相比未启用ADR急剧升高，由88S->324S，现在我们重新设计一个单行插入语句，以便更容易衡量绝对成本。下·

启用ADR的大批量插入：

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134408299-2038773532.png)

未启用ADR的大语句插入：

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134419025-931820169.png)

可以看到几乎没有差别，只是IO稍微增高，我怀疑是额外的In-Row Data导致，CPU开销略微增加和微软论文中类似。

### 额外的行版本Clean Up

这部分成本难以衡量，目前直接使用论文中的结论

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134538518-523848350.png)

Delete和Insert成本比较低，只需要标记元数据，而Update需要完整操作数据，成本比较高。Clean Up效率看上去绝大多数场景来看，可接受

### 查询成本的额外增加

由于需要遍历可能的多个行版本，因此在行版本没有被清理之前，查询成本是需要增加的。

# 小结

根据微软文档，TPCC和TPCE在启用ADR后较小列长和较大列长的场景性能下降如下图，

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2024-02-18-sql-server-accelerated-database-recovery/sql-server-accelerated-database-recovery-35368-20240218134515111-1715476629.png)

根据测试，对于有高频写入的小事务，启用ADR会有较多性能开销，但从数据库可用性角度、回滚风险角度来看，该功能对于较大实例的收益会大于风险。

现在该功能在2022中得到进一步增强，由于没有大规模实践验证，我们还不知道该功能的质量是否能够不引入额外的问题，到哪根据下面两点，我认为该功能已经可以达到推荐启用的阶段：

  * SQL Azure和Managed instance已经默认启用，通常默认启用的功能已经经历过大考

  * 该功能在2022中进一步严谨迭代，已经属于V2




因此后续我们会考虑对大客户定向推动建议启用该选项。

# 附录: 在RDS SQL Server上如何启用该选项：

参考该文档：在“高级属性部分”，将accelerated\_database\_recovery 属性设置为ON

[https://help.aliyun.com/zh/rds/apsaradb-rds-for-sql-server/database-advanced-feature-management](https://help.aliyun.com/zh/rds/apsaradb-rds-for-sql-server/database-advanced-feature-management?spm=a2c4g.11186623.0.0.2a595400ly9hX4)

也可以使用OpenAPI实现:

参考文档:[https://help.aliyun.com/zh/rds/developer-reference/api-rds-2014-08-15-modifydatabaseconfig](https://help.aliyun.com/zh/rds/developer-reference/api-rds-2014-08-15-modifydatabaseconfig?spm=a2c4g.11186623.0.i13)
