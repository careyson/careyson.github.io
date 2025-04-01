---
layout: post
title: "浅谈SQL SERVER中事务的ACID"
date: 2012-01-29
categories: blog
tags: [博客园迁移]
---

### 简介

ACID，是指在可靠数据库管理系统（DBMS）中，事务\(transaction\)所应该具有的四个特性：原子性（Atomicity）、一致性（Consistency）、隔离性（Isolation）、持久性（Durability）.这是可靠数据库所应具备的几个特性.下面针对这几个特性进行逐个讲解.

### 理解原子性\(Atomicity\)

原子性意味着数据库中的事务执行是作为原子。即不可再分，整个语句要么执行，要么不执行。

在SQL SERVER中，每一个单独的语句都可以看作是默认包含在一个事务之中:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-201201291407099129.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407094951.png)

所以，每一个语句本身具有原子性，要么全部执行，这么全部不执行，不会有中间状态:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-201201291407101180.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407106130.png)

上面说了，每一条T-SQL语句都可以看作是默认被包裹在一个事务之中的,SQL Server对于每一条单独的语句都实现了原子性，但这种原子粒度是非常小的，如果用户想要自己定义原子的大小，则需要包含在事务中来构成用户自定义的原子粒度:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-201201291407118214.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407105673.png)

对于用户来说，要用事务实现的自定义原子性往往是和业务相关的，比如银行转账，从A账户减去100，在B账户增加100，如果这两个语句不能保证原子性的话，比如从A账户减去100后，服务器断电，而在B账户中却没有增加100.虽然这种情况会让银行很开心，但作为开发人员的你可不希望这种结果.而默认事务中，即使出错了也不会整个事务进行回滚。而是失败的语句抛出异常，而正确的语句成功执行。这样会破坏原子性。所以SQL SERVER给予了一些选项来保证事务的原子性.

SQL SERVER提供了两大类方式来保证自定义事务的原子性：

** 1.通过SET XACT\_ABORT ON来设置事务必须符合原子性**

利用设置XACT\_ABORT选项设置为ON,来设置所有事务都作为一个原子处理.下面例子利用两个语句插入到数据库，可以看到开启SET XACT\_ABORT ON选项后，事务具有了原子性:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-201201291407115249.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407116295.png)

** 2.按照用户设置进行回滚\(ROLLBACK\)**

这种方式具有更高的灵活性，开发人员可以自定义在什么情况进行ROLLBACK,利用TRY CATCH语句和@@ERROR进行判断都属于这种方式.

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-20120129140713364.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407123886.png)

### 理解一致性\(Consistency\)

一致性,即在事务开始之前和事务结束以后，数据库的完整性约束没有被破坏。

一致性分为两个层面

**1.数据库机制层面**

**** 数据库层面的一致性是，在一个事务执行之前和之后，数据会符合你设置的约束（唯一约束，外键约束,Check约束等\)和触发器设置.这一点是由SQL SERVER进行保证的.

**2.业务层面**

**** 对于业务层面来说,一致性是保持业务的一致性.这个业务一致性需要由开发人员进行保证.很多业务方面的一致性可以通过转移到数据库机制层面进行保证.比如，产品只有两个型号，则可以转移到使用CHECK约束使某一列必须只能存这两个型号.

### 理解隔离性（Isolation\)

隔离性。事务的执行是互不干扰的，一个事务不可能看到其他事务运行时，中间某一时刻的数据。

在Windows中，如果多个进程对同一个文件进行修改是不允许的，Windows通过这种方式来保证不同进程的隔离性:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-20120129140714463.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407135414.png)

而SQL Server中，通过SQL SERVER对数据库文件进行管理，从而可以让多个进程可以同时访问数据库:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-201201291407143038.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407142132.png)

SQL Server利用加锁和阻塞来保证事务之间不同等级的隔离性.

一般情况下，完全的隔离性是不现实的，完全的隔离性要求数据库同一时间只执行一条事务，这样的性能可想而知.想要理解SQL Server中对于隔离性的保障，首先要了解事务之间是如何干扰的.

事务之间的互相影响的情况分为几种，分别为:脏读\(Dirty Read\)，不可重复读，幻读

**脏读**

**** 脏读意味着一个事务读取了另一个事务未提交的数据,而这个数据是有可能回滚的:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-201201291407156692.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407148610.png)

下面来看一个例子:

两个事务，事务A插入一条数据，但未提交，事务B在此期间进行了读取，读取到了事务A未提交的数据，造成脏读

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-201201291407161807.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407159789.png)

**不可重复读\(Unrepeatable Read\)**

不可重复读意味着，在数据库访问中，一个事务范围内两个相同的查询却返回了不同数据。这是由于查询时系统中其他事务修改的提交而引起的。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-20120129140717793.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407169888.png)

下面来看一个不可重复读的例子:

事务B中对某个查询执行两次，当第一次执行完时，事务A对其数据进行了修改。事务B中再次查询时，数据发生了改变:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-201201291407175876.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407176923.png)

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-201201291407189563.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/20120129140718926.png)

**幻读\(phantom read\)**

幻读,是指当事务不是独立执行时发生的一种现象，例如第一个事务对一个表中的数据进行了修改，这种修改涉及到表中的全部数据行。同时，第二个事务也修改这个表中的数据，这种修改是向表中插入一行新数据。那么，以后就会发生操作第一个事务的用户发现表中还有没有修改的数据行，就好象发生了幻觉一样.

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-201201291407193533.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407197960.png)

下面来看一个例子:

事务B更新表中所有的数据，在此期间事务A插入了一条数据，事务B再次查询后，发现居然还有没有修改的数据，产生幻读:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-20120129140720600.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407194679.png)

**理解SQL SERVER中的隔离级别**

**** 为了避免上述几种事务之间的影响,SQL Server通过设置不同的隔离等级来进行不同程度的避免。因为高的隔离等级意味着更多的锁，从而牺牲性能.所以这个选项开放给了用户根据具体的需求进行设置。不过默认的隔离等级Read Commited符合了99%的实际需求.

SQL Server隔离事务之间的影响是通过锁来实现的，这个概念比较繁杂，所以本文不会详细对这个概念进行讲解.通过阻塞来阻止上述效果

SQL Server提供了5种选项来避免不同级别的事务之间的影响

隔离等级由低到高分别为

Read Uncommited\(最高的性能，但可能出现脏读，不可重复读，幻读\)

Read commited\(可能出现不可重复读，幻读\)

Repeatable Read\(可能出现幻读\)

Serializable\(最低的性能，Range锁会导致并发下降\)

SNOPSHOT\(这个是通过在tempDB中创建一个额外的副本来避免脏读，不可重复读，会给tempDB造成额外负担，因为不是标准ANSI SQL标准，不详细讨论\)

总之，不同的隔离级别是通过加不同的锁，造成阻塞来实现的，来看一个例子:

SQL SERVER通过阻塞来阻止脏读，所以保持独立性会以付出性能作为代价：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-01-29-sql-server-acid/sql-server-acid-201201291407215367.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201201/201201291407208681.png)

理解持久性（Durability\)

**** 持久性，意味着在事务完成以后，该事务所对数据库所作的更改便持久的保存在数据库之中，并不会被回滚。

即使出现了任何事故比如断电等，事务一旦提交，则持久化保存在数据库中.

SQL SERVER通过write-ahead transaction log来保证持久性。write-ahead transaction log的意思是，事务中对数据库的改变在写入到数据库之前，首先写入到事务日志中。而事务日志是按照顺序排号的（LSN）。当数据库崩溃或者服务器断点时，重启动SQL SERVER，SQL SERVER首先会检查日志顺序号，将本应对数据库做更改而未做的部分持久化到数据库，从而保证了持久性.

### 总结

本文简单讲述了ACID的概念和ACID在SQL SERVER中的实现.ACID只是一个理念，并不是某项具体的技术.对于健壮数据库来说，保证ACID是可靠数据库的前提.
