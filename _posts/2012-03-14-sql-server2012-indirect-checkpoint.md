---
layout: post
title: "SQL Server2012中的Indirect CheckPoint"
date: 2012-03-14
categories: blog
tags: [博客园迁移]
---

### 简介

SQL Server2012新增的Indirect CheckPoint允许CheckPoint的恢复间隔设置到数据库级别，而不是以前那样实例级别。

在数据库级别设置的恢复时间以秒为单位，而不是在实例级别的以分钟为单位。这可以更精确的保证数据库Recovery的最大时间。

### 配置Indirect CheckPoint

Indirect Checkpoint是数据库级别的。在SQL SERVER中，包括Contained Database,SQL Server把一些设置从实例级别转到了数据库级别。

按照MSDN上对Indirect CheckPoint的描述，我对Indirect CheckPoint的理解是独立于实例级别CheckPoint的的额外线程。仅仅负责其所在的数据库。因此带来的好处可以归结如下。

1.更少的数据库恢复时间\(CheckPoint间隔小了，自然恢复时间就少了\)

2.更精确的恢复时间。现在不仅仅CheckPoint的范围缩小了，并且最大恢复时间是以秒为单位。

3.由于这个Indirect CheckPoint线程将其所负责数据库范围内的Dirty Page写入磁盘，所以实例级别的CheckPoint可以减少对磁盘的一次性写入量。从而减少了实例级别CheckPoint的负载

但是，设置Indirect CheckPoint保证数据库Recovery时间尽可能短的同时，由于恢复间隔可能变短，在OLTP环境下造成更多的磁盘写入，有可能给I/O造成额外的负担

下面来看配置Indirect CheckPoint,我们可以通过SSMS或是T-SQL进行配置

使用SSMS配置Indirect CheckPoint如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-14-sql-server2012-indirect-checkpoint/sql-server2012-indirect-checkpoint-201203141633222963.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203141633211982.png)

图1.在SSMS中设置CheckPoint

也可以通过设置数据库的TARGET\_RECOVERY\_TIME选项来设置恢复时间，如代码1所示。   

    
    
    [ALTER](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ALTER&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [DATABASE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DATABASE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) Test 
    
    [SET](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SET&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) TARGET_RECOVERY_TIME = 32 SECONDS;

代码1.设置数据库的TARGET\_RECOVERY\_TIME选项   


参考资料:[Change the Target Recovery Time of a Database](http://msdn.microsoft.com/en-us/library/hh403416\(v=sql.110\).aspx#Restrictions)

[Database Checkpoints](http://msdn.microsoft.com/en-us/library/ms189573\(v=sql.110\).aspx)
