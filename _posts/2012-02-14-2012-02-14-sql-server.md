---
layout: post
title: "浅谈SQL Server中的事务日志(二)----事务日志在修改数据时的角色"
date: 2012-02-14
categories: blog
tags: [博客园迁移]
---

本篇文章是系列文章中的第二篇，以防你还没有看过第一篇.上一篇的文章地址如下:

[浅谈SQL Server中的事务日志\(一\)----事务日志的物理和逻辑构架](http://www.cnblogs.com/CareySon/archive/2012/02/13/2349751.html)

### 简介

每一个SQL Server的数据库都会按照其修改数据\(insert,update,delete\)的顺序将对应的日志记录到日志文件.SQL Server使用了Write-Ahead logging技术来保证了事务日志的原子性和持久性.而这项技术不仅仅保证了ACID中的原子性\(A\)和持久性\(D\),还大大减少了IO操作，把对数据的修改提交到磁盘的工作交给lazy-writer和checkpoint.本文主要讲述了SQL Server修改数据时的过程以及相关的技术。

### 预写式日志（Write-Ahead Logging \(WAL\)）

SQL Server使用了WAL来确保了事务的原子性和持久性.实际上，不光是SQL Server,基本上主流的关系数据库包括oracle,mysql,db2都使用了WAL技术.

WAL的核心思想是:在数据写入到数据库之前，先写入到日志.

因为对于数据的每笔修改都记录在日志中，所以将对于数据的修改实时写入到磁盘并没有太大意义，即使当SQL Server发生意外崩溃时，在恢复\(recovery\)过程中那些不该写入已经写入到磁盘的数据会被回滚\(RollBack\),而那些应该写入磁盘却没有写入的数据会被重做\(Redo\)。从而保证了持久性\(Durability\)

但WAL不仅仅是保证了原子性和持久性。还会提高性能.

硬盘是通过旋转来读取数据,通过WAL技术，每次提交的修改数据的事务并不会马上反映到数据库中，而是先记录到日志.在随后的CheckPoint和lazy Writer中一并提交,如果没有WAL技术则需要每次提交数据时写入数据库:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-14-sql-server/sql-server-201202141523044997.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/20120214152304503.png)

而使用WAL合并写入，会大大减少磁盘IO：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-14-sql-server/sql-server-201202141523084313.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202141523084280.png)

也许你会有疑问，那每次对于修改的数据还是会写入日志文件.同样消耗磁盘IO。上篇文章讲过，每一笔写入日志的记录都是按照先后顺序，给定顺序编号的LSN进行写入的，日志只会写入到日志文件的逻辑末端。而不像数据那样，可能会写到磁盘的各个地方.所以，写入日志的开销会比写入数据的开销小很多。

### SQL Server修改数据的步骤

SQL Server对于数据的修改,会分为以下几个步骤顺序执行:

1.在SQL Server的缓冲区的日志中写入”Begin Tran”记录

2.在SQL Server的缓冲区的日志页写入要修改的信息

3.在SQL Server的缓冲区将要修改的数据写入数据页

4.在SQL Server的缓冲区的日志中写入”Commit”记录

5.将缓冲区的日志写入日志文件

6.发送确认信息\(ACK\)到客户端\(SMSS,ODBC等）

可以看到,事务日志并不是一步步写入磁盘.而是首先写入缓冲区后，一次性写入日志到磁盘.这样既能在日志写入磁盘这块减少IO，还能保证日志LSN的顺序.

上面的步骤可以看出，即使事务已经到了Commit阶段，也仅仅只是把缓冲区的日志页写入日志，并没有把数据写入数据库.那将要修改的数据页写入数据库是在何时发生的呢?

### Lazy Writer和CheckPoint

上面提到，SQL Server修改数据的步骤中并没有包含将数据实际写入到磁盘的过程.实际上，将缓冲区内的页写入到磁盘是通过两个过程中的一个实现：

这两个过程分别为:

1.CheckPoint

2.Lazy Writer

任何在缓冲区被修改的页都会被标记为“脏”页。将这个脏页写入到数据磁盘就是CheckPoint或者Lazy Writer的工作.

当事务遇到Commit时，仅仅是将缓冲区的所有日志页写入磁盘中的日志文件:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-14-sql-server/sql-server-20120214152309508.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202141523089363.png)

而直到Lazy Writer或CheckPoint时，才真正将缓冲区的数据页写入磁盘文件:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-14-sql-server/sql-server-201202141523108971.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202141523093606.png)

前面说过，日志文件中的LSN号是可以比较的，如果LSN2>LSN1,则说明LSN2的发生时间晚于LSN1的发生时间。CheckPoint或Lazy Writer通过将日志文件末尾的LSN号和缓冲区中数据文件的LSN进行对比，只有缓冲区内LSN号小于日志文件末尾的LSN号的数据才会被写入到磁盘中的数据库。因此确保了WAL（在数据写入到数据库之前，先写入日志\)。

### Lazy Writer和CheckPoint的区别

Lazy Writer和CheckPoint往往容易混淆。因为Lazy Writer和CheckPoint都是将缓冲区内的“脏”页写入到磁盘文件当中。但这也仅仅是他们唯一的相同点了。

Lazy Writer存在的目的是对缓冲区进行管理。当缓冲区达到某一临界值时，Lazy Writer会将缓冲区内的脏页存入磁盘文件中，而将未修改的页释放并回收资源。

而CheckPoint存在的意义是减少服务器的恢复时间\(Recovery Time\).CheckPoint就像他的名字指示的那样，是一个存档点.CheckPoint会定期发生.来将缓冲区内的“脏”页写入磁盘。但不像Lazy Writer,Checkpoint对SQL Server的内存管理毫无兴趣。所以CheckPoint也就意味着在这个点之前的所有修改都已经保存到了磁盘.这里要注意的是：CheckPoint会将所有缓冲区的脏页写入磁盘，不管脏页中的数据是否已经Commit。这意味着有可能已经写入磁盘的“脏页”会在之后回滚（RollBack\).不过不用担心，如果数据回滚，SQL Server会将缓冲区内的页再次修改，并写入磁盘。

通过CheckPoint的运作机制可以看出，CheckPoint的间歇\(Recovery Interval\)长短有可能会对性能产生影响。这个CheckPoint的间歇是一个服务器级别的参数。可以通过sp\_config进行配置，也可以在SSMS中进行配置:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-14-sql-server/sql-server-201202141523142465.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202141523134907.png)

恢复间歇的默认参数是0，意味着由SQL Server来管理这个回复间隔。而自己设置恢复间隔也是需要根据具体情况来进行界定。更短的恢复间歇意味这更短的恢复时间和更多的磁盘IO，而更长的恢复间歇则带来更少的磁盘IO占用和更长的恢复时间.

除了自动CheckPoint之外，CheckPoint还会发生在Alter DataBase以及关闭SQL Server服务器时。sysadmin和db\_backupoperator组的成员以及db\_owner也可以使用CheckPoint指令来手动保存CheckPoint:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-02-14-sql-server/sql-server-201202141523158104.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201202/201202141523158071.png)

通过指定CheckPoint后的参数，SQL Server会按照这个时间来完成CheckPoint过程，如果时间指定的短，则SQL Server会使用更多的资源优先完成CheckPoint过程。

通常情况下，将“脏”页写入磁盘的工作，Lazy Writer要做的比CheckPoint会多出许多。

### 总结

本文简单介绍了WAL的概念和修改数据库对象时，日志所扮演的角色。还分别介绍了CheckPoint和Lazy Writer,对于这些概念的理解是理解SQL Server DBA工作的基础。下篇文章将会讲述在简单恢复模式下日志的机制。
