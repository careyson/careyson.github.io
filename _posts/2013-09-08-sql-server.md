---
layout: post
title: "再谈SQL Server中日志的的作用"
date: 2013-09-08
categories: blog
tags: [博客园迁移]
---

### 简介

之前我已经写了一个关于SQL Server日志的简单系列文章。本篇文章会进一步挖掘日志背后的一些概念，原理以及作用。如果您没有看过我之前的文章，请参阅：

[浅谈SQL Server中的事务日志\(一\)----事务日志的物理和逻辑构架](http://www.cnblogs.com/CareySon/archive/2012/02/13/2349751.html)

[浅谈SQL Server中的事务日志\(二\)----事务日志在修改数据时的角色](http://www.cnblogs.com/CareySon/archive/2012/02/14/2351149.html)

[浅谈SQL Server中的事务日志\(三\)----在简单恢复模式下日志的角色](http://www.cnblogs.com/CareySon/archive/2012/02/17/2355200.html)

[浅谈SQL Server中的事务日志\(四\)----在完整恢复模式下日志的角色](http://www.cnblogs.com/CareySon/archive/2012/02/23/2364572.html)

[浅谈SQL Server中的事务日志\(五\)----日志在高可用和灾难恢复中的作用](http://www.cnblogs.com/CareySon/archive/2013/06/16/3138742.html)

### 数据库的可靠性

在关系数据库系统中，我们需要数据库可靠，所谓的可靠就是当遇见如下两种情况之一时保证数据库的一致性:

  * 在系统崩溃/故障等情况下，保证数据库的一致性 
  * 数据不能在多个DML语句同时修改数据的情况下，导致不一致或数据损坏 



实际上，上述第二种情况就是并发性所需要解决的问题，传统关系数据库中，我们用锁来解决这个问题，而对于内存数据库或带有乐观并发控制的数据库系统，通过多版本并发控制（MVCC）来解决这个问题。因为本篇文章的主旨是讨论日志而不是并发，因此对于上述第二种情况不会详细解释。

我们上面还多次提到了一致性（Consistence），在开始了解日志如何维持一致性之前，我们首先要明白什么是一致性。一致性在数据库系统中所指的内容比较广，一致性不仅仅需要数据库中的数据满足各种约束，比如说唯一约束，主键约束等，还需要满足数据库设计者心中的隐式约束，简单的业务约束比如说性别这列只允许男或女，这类隐式约束通常使用触发器或约束来实现，或是在数据库所服务的应用程序中进行约束。

下面我们把一致性的范围缩减到事务一致性，事务一致性的概念学术上的解释为：

> 如果事务执行期间没有出现系统错误或其他事务错误，并且数据库在事务开始期间是数据一致的，那么在该事务结束时，我们认为数据库仍然保证了一致性。

因此，引申出来事务必须满足原子性，也就是事务不允许部分执行。事务的部分执行等同于将数据库置于不一致的境地之下。此外多事务并发执行也可能导致数据库不一致，除非数据库系统对并发进行控制。

关于上面的显式约束，由数据库系统来实现，比如说违反了一致性约束的语句会导致数据库系统报错并拒绝执行。但一些隐式的事务约束，比如说写语句的开发人员对系统设计者所设计的规则并不了解，导致了违反业务规则的数据修改，这种情况在数据库端很难探查。但是这种问题通常可以规则到权限控制的领域，我们认为授予某个用户修改特定数据的权限，就认为这个用户应该了解数据库中隐式和显式的规则。

除去这些业务上的数据不一致之外，我们需要在系统崩溃等情况下保证数据的一致性，而可能导致这类数据不一致的情况包括但不限于下面这些情况：

  * 存储系统损坏，比如说磁盘上字节级别的损坏，这类问题通常可以通过磁盘上的奇偶校验发现，另外还有一些大一些的问题，比如说整个存储系统崩溃。这类问题的修复手段取决于前期工作，比如说备份策略，高可用性架构，SAN Replication等技术。 
  * 机房整体损坏，这类问题比较极端，只有异地机房容灾可以解决。 
  * 系统故障，修改数据的进程都需要事务作为上下文，和其他概念一样，事务也是有状态的。而事务状态通常存储在易丢失的主存中，因此，当出现系统故障、进程崩溃等系统失败时，可能导致事务状态的丢失，此时，我们就无法得知事务中的哪部分已经执行而哪部分还未执行，重新运行事务并不会解决这类问题，因为有可能导致事务中某部分的重复执行。因此解决这类问题的方式就是将事务的状态以及对数据库修改的详细步骤与内存中的数据分开存放，并存储于磁盘等稳定的介质中，当系统故障等情况下，我们可以通过这些记录来将系统恢复到一致性的状态之下，我们对这类存储，称之为日志。 



### 

SQLServer中的日志

SQL Server中靠日志来维护一致性（当然，日志的作用非常多，但一致性是日志的基本功能，其他功能可以看作是额外的功能）。通常我们创建数据库的时候，会附带一个扩展名为ldf的日志文件。日志文件其实本质上就是日志记录的集合。在SQL Server中，我们可以通过DBCC LOGINFO来看这个日志的信息，如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-08-sql-server/sql-server-08221924-77546462baa3426db960ef457f00bdba.png)](//images0.cnblogs.com/blog/35368/201309/08221924-83527c34128a44488195d034fc6e7542.png)

图1.DBCC LOGINFO

该命令可以从VLF的角度从一个比较高的层级看日志。其中值得注意的列是VLF大小，状态（2表示使用，0表示从未使用过），偏移量。对于这些信息对我们规划VLF数量的时候很有帮助，因为VLF过多可能引起严重的性能问题，尤其是在复制等Scale-Out或HA环境下。

然后，事务对数据库中每次修改都会分解成多个多个原子层级的条目被记录到持久存储中，这些条目就是所谓的日志记录（Log Record），我们可以通过fn\_dblog来查看这些条目。如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-08-sql-server/sql-server-08221926-007c2029141e435db3af66b33effa5f1.png)](//images0.cnblogs.com/blog/35368/201309/08221925-77a7ee545eb943c481b2fe8253a815d2.png)

图2.Fn\_dblog

每个日志记录都会被背赋予一个唯一的顺序编号，这个编号大小为10字节，由三部分组成，分别为：

  * VLF顺序号（4字节） 
  * Log Block顺序号（4字节） 
  * Log Block内的顺序编号（2字节） 



因此，由于VLF是不断递增的（同一个VLF被复用会导致编号改变），因此LSN序号也是不断递增的。因此，通过上面的LSN结构不难发现，如果比VLF更小的粒度并不是直接对应LOG RECORD，而是LOG Block。Log Block是日志写入持久化存储的最小单位，Log Block的大小从512字节到60K不等，这取决于事务的大小，那些在内存还未被写入持久化存储的Log Block也就是所谓的In-Flight日志。以下两个因素决定Log Block的大小：

  * 事务提交或回滚 
  * Log Block满60K会强制Flush到持久化存储，以保证WAL 



因此当一个事务很大时（比如说大面积update），每60K就会成为一个Log Block写入持久化存储。而对于很多小事务，提交或回滚就会称为一个Block写入持久化存储，因此根据事务的大小，LOG Block的大小也会不同。值得疑惑的是，因为磁盘上分配单元的大小是2的N次方，因此最接近LOG BLOCK的大小应该是64K，而SQL Server为什么不把Log Block设定为64K呢。这样可以更优化IO。

VLF和Log Block和Log Record的关系如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-08-sql-server/sql-server-08221926-5f461cabf69747da93656288b86b195c.png)](//images0.cnblogs.com/blog/35368/201309/08221926-3786143ae56f43fa822171282d251b0f.png)

图3.三者之间的关系

从比较高的层级了解了日志之后，我们再仔细了解日志中应该存储的关键信息，每条Log Record中都包含下面一部分关键信息：

  * LSN 
  * Log Record的Context 
  * Log Record所属的事务ID（所有的用户事务都会存在事务ID） 
  * Log Record所占的字节 
  * 同一个事务中上一条Log Record的LSN（用于Undo） 
  * 为Undo所保留的日志空间 



当然，这些仅仅是日志的一小部分内容。通过Log Record所记录的内容，就能够精确的记录对数据库所做的修改。

### 

### 日志用于Undo

在了解为了Undo，日志所起的作用之前，我们首先可以了解一下为什么需要事务存在回滚：

  * 因为事务可能失败，或者死锁等原因，如果希望事务不违反原子性而造成数据库不一致的话，则需要通过回滚将已经部分执行的事务回滚掉。 
  * 根据业务需求，如果在某些关联业务失败等情况下，回滚数据。 



因此，Log Record会为这些列保存一些字节来执行数据库回滚，最简单的例子莫过于执行插入后Rollback事务，则日志会产生一条所谓的Compensation Log Record来反操作前面已经插入的事务，如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-08-sql-server/sql-server-08221927-7dd284b7030f48af98b2b672aa9a5bcc.png)](//images0.cnblogs.com/blog/35368/201309/08221927-6cdb2665d3ea4d3c86733926fb917e7e.png)

图4.Compensation Log示例

图4执行的是一个简单的Insert语句，然后回滚。我们看到，SQL Server生成了一个Compensation Log Record来执行反向操作，也就是Delete操作。值得注意的是，为了防止这些回滚操作，SQL Server会保留一些空间用于执行回滚，我们看到LOP\_INSERT\_ROWS保留的74字节空间被下面的Compensation Log Record所消耗。Compensation Log record还有一个指向之前LSN的列，用于回滚，直至找到LOP\_BEGIN\_XACT的事务开始标记。另外，Compenstion Log Record只能够用于Redo，而不能用于Undo。

那假设我们某一个事务中删除了多条数据怎么办?比如说，某一个事务中一个Delete语句删除了10行，则需要在Log Record对应10个LOP\_DELETE\_ROWS（引申一下，由此我们可以看出某一个语句可能导致N个Log Record，这么多Log Record在复制，镜像时都需要在另一端Redo，因此需要额外的开销），如果我们此时RollBack了该事务，则Redo的顺序是什么呢，如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-08-sql-server/sql-server-08221928-7b0e59ebc0ff41acaa6201c1418b447a.png)](//images0.cnblogs.com/blog/35368/201309/08221928-2e81ff6a811041d2a85674ab82048eba.png)

图5.回滚事务

图5中，删除3条数据后，进行回滚，首先从删除3开始，生成对应的反向Compensation Log Record，并指向删除2，再对应删除2生成反向Compensation Log Record并指向删除1，以此类推，最终回滚事务指回开始事务。

### 日志用于Redo

与Undo不同，在计算机存储体系中，辅助存储通常是带有磁头的磁盘。这类存储系统的IOPS非常低，因此如果对于事务对数据库执行的修改操作，我们积累到一定量再写入磁盘，无疑会提高IO的利用率。但是在数据在主存还没有持久化的辅助存储的期间，如果遭遇系统故障，则这部分数据的丢失则可能导致数据库的不一致状态。

因此，使用日志使得该问题得到解决。与日志Undo方面的不同之处在于：Undo用于解决事务未完成和事务回滚的情况，而Redo则是为了保证已经提交的事务所做的修改持久化到辅助存储。

Redo则引申出了WAL，即事务日志会在COMMIT或COMMIT之前写入持久化存储中，然后事务对数据本身的修改才能生效。因此就能够保证在系统故障时可以通过读取日志来Redo日志的持久化操作。因此对于最终用户可以显示事务已经提交而暂时不用将所修改的数据写入持久化存储。由于数据在日志未写入持久化存储之前无法持久化，则需要更大的主存作为BUFFER空间。

因为日志既要用于Undo，又要用于Redo，因此为了能够成功生成Compensation Log Record，需要日志既记录被修改前的数据，又记录被修改后的数据，比如我们在图6中做一个简单的更新。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-08-sql-server/sql-server-08221928-ca934f301bad443bba662f9868b17017.png)](//images0.cnblogs.com/blog/35368/201309/08221928-ad483cd457d84eedb20001f6ab34ced1.png)

图6.记录更新之前和之后的数据

值得注意的是，如果修改的值是聚集索引键，则由于修改该数据会导致存储的物理位置改变，所以SQL Server并不会像这样做即席更新，而是删除数据再插入数据，从而导致成本的增加，因此尽量不要修改聚集索引键。

### Undo/Redo Recovery

当SQL Server非正常原因关闭时，也就是在没有走CheckPoint（会在下面提到）时关闭了数据库，此时数据库中数据本身可能存在不一致的问题。因此在数据库再次启动的时候，会去扫描日志，找出那些未提交却写入持久化存储的数据，或已提交却未写入持久化存储的数据，来进行Undo和Redo来保证事务的一致性。Undo/Redo Recovery遵循以下规则：

  * 按照由早到晚的顺序Redo该已提交却未写入持久化存储的数据 
  * 按照由晚到早的顺序Undo未提交，却写入持久化存储的数据 



图7中，我们进行一个简单测试，在启动过程中，首先禁用了CheckPoint以防止自动CheckPoint，然后我们修改数据，不提交，并持久化到磁盘。另一个线程修改数据并提交，但未持久化到磁盘。为了简单起见，我把两个线程写到一个窗口中。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-08-sql-server/sql-server-08221929-2c57fe770a4a4f92b60e06760d543c3d.png)](//images0.cnblogs.com/blog/35368/201309/08221929-4996424a33ef47e398c9c35dd581b9c1.png)

图7.需要Undo和Redo的两个事务

此时我们强制杀死SQL Server进程，导致数据本身不一致，此时在SQL Server的重启过程中，会自动的Redo和Undo上面的日志，如图８所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-08-sql-server/sql-server-08221930-5cb8cf1fe64045b595d4b3dc77e2592c.png)](//images0.cnblogs.com/blog/35368/201309/08221929-d69ae2c4659d4176910ac2ec577d6449.png)

图8.实现Redo和Undo

**那么，什么是CheckPoint?**

图８给出的简单例子足以说明Recovery机制。但例子过于简单，假如一个非常繁忙的数据库可能存在大量日志，一个日志如果全部需要在Recovery过程中被扫描的话，那么Recovery过程所导致的宕机时间将会成为噩梦。因此，我们引入一个叫CheckPoint的机制，就像其名称那样，CheckPoint就是一个存档点，意味着我们可以从该点继续开始。

在Undo/Redo机制的数据库系统中，CheckPoint的机制如下：

１.将CheckPoint标记写入日志（标记中包含当前数据库中活动的事务信息），并将Log Block写入持久化存储

2.将Buffer Pool中所有的脏页写入磁盘，所有的脏页包含了未提交事务所修改的数据

3.将结束CKPT标记写入日志，并将Log Block写入持久化存储

我们在日志中可以看到的CheckPoint标记如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-09-08-sql-server/sql-server-08221930-e8a424fcfc5346e98b995c678571271a.png)](//images0.cnblogs.com/blog/35368/201309/08221930-b66235ecb2904e7893aeb3986e91c0bf.png)

图9.CheckPoint标记

其中，这些Log Record会包含CheckPoint的开始时间，结束时间以及MinLSN，用于复制的LSN等。由图９中我们还可以看到一个LOP\_XACT\_CKPT操作的Log Record，该操作符的上下文如果为NULL的话，则意味着当前：

  * 包含未提交事务 
  * 该Log Record记录包含未提交事务的个数 
  * 包含未提交的事务所涉及的LSN 



由CheckPoint的机制可以看出，由于内存中的数据往往比持久化存储中的数据更新，而CheckPoint保证了这部分数据能够被持久化到磁盘，因此CheckPoint之前的数据一定不会再需要被Redo。而对于未提交的事物所修改的数据写入持久化存储，则可以通过Undo来回滚事务（未提交的事物会导致CheckPoint无法截断日志，因此这部分日志可以在Recovery的时候被读取到，即使这部分日志在CheckPoint之前）。

此时，我们就可以100%的保证，CheckPoint之前的日志就可以被安全删除（简单恢复模式）或归档了（完整恢复模式），在Recovery时，仅仅需要从CheckPoint开始扫描日志，从而减少宕机时间。

### 小结

本篇文章深入挖掘了数据库中日志为保护数据一致性的的作用、实现原理。日志在这些功能之外，也是为了用于实现高可用性，因此了解这些原理，可以更好的帮助我们在搭建高可用性拓扑以及设计备份计划时避免一些误区。
