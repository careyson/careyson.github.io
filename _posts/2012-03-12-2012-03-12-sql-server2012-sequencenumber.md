---
layout: post
title: "SQL Server2012中的SequenceNumber尝试"
date: 2012-03-12
categories: blog
tags: [博客园迁移]
---

### 简介

SequenceNumber是SQL Server2012推出的一个新特性。这个特性允许数据库级别的序列号在多表或多列之间共享。对于某些场景会非常有用，比如，你需要在多个表之间公用一个流水号。以往的做法是额外建立一个表，然后存储流水号。而新插入的流水号需要两个步骤：

1.查询表中流水号的最大值

2.插入新值（最大值+1）

现在，利用SQL Server2012中的Sequence.这类操作将会变得非常容易。

### SequenceNumber的基本概念

SequenceNumber的概念并不是一个新概念，Oracle早就已经实现了（<http://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_6015.htm>）。与以往的Identity列不同的是。SequenceNumber是一个与构架绑定的数据库级别的对象，而不是与具体的表的具体列所绑定。这意味着SequenceNumber带来多表之间共享序列号的遍历之外，还会带来如下不利影响:

  * 与Identity列不同的是，Sequence插入表中的序列号可以被Update,除非通过触发器来进行保护
  * 与Identity列不同，Sequence有可能插入重复值（对于循环SequenceNumber来说）
  * Sequence仅仅负责产生序列号，并不负责控制如何使用序列号，因此当生成一个序列号被Rollback之后，Sequence会继续生成下一个号，从而在序列号之间产生间隙。



### SequenceNumber的用法

SequenceNumber在MSDN中定义的原型如代码1所示。
    
    
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SEQUENCE [schema_name . ] sequence_name
        [ [AS](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=AS&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [ built_in_integer_type | [user](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=user&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)-defined_integer_type ] ]
        [ START [WITH](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=WITH&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) <constant> ]
        [ INCREMENT [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) <constant> ]
        [ { MINVALUE [ <constant> ] } | { [NO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=NO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) MINVALUE } ]
        [ { MAXVALUE [ <constant> ] } | { [NO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=NO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) MAXVALUE } ]
        [ CYCLE | { [NO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=NO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) CYCLE } ]
        [ { CACHE [ <constant> ] } | { [NO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=NO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) CACHE } ]
        [ ; ]

  


代码1.Sequence的创建原型

由代码1看以看到,参数相对比较简单。从指定数据类型（INT兼容）到开始计数点，步长，最大值和最小值，是否循环和是否缓存几个参数来设置Sequence。

下面图1创建了一个简单的Sequence。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-12-sql-server2012-sequencenumber/sql-server2012-sequencenumber-201203121223376057.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203121223367792.png)

图1.创建一个简单的Sequence并进行使用

此时，我们可以通过SQL Server 2012新增的视图sys.sequences来看到刚才创建成功的Sequence,如图2所示.

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-12-sql-server2012-sequencenumber/sql-server2012-sequencenumber-20120312122536129.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203121225122049.png)

图2.sys.sequences视图

当然我们可以这个序列按照顺序插入表,如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-12-sql-server2012-sequencenumber/sql-server2012-sequencenumber-201203121225418728.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203121225389582.png)

图3.在单表中插入序列

而SequenceNumber最重要的功能是在多表间共享序列号，如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-12-sql-server2012-sequencenumber/sql-server2012-sequencenumber-20120312122622782.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203121225555225.png)

图4.多表之间利用Sequence共享序列号

前面图2可以看到，如果我们不指定Sequence的上限和下限，则默认使用所指定数据类型的最大值和最小值作为上限和下限（如图2INT类型的的上下限）.当达到上线后，可以指定循环来让Sequence达到上限后从指定的开始值重新开始循环。如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-12-sql-server2012-sequencenumber/sql-server2012-sequencenumber-201203121226295529.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203121226234205.png)

图5.Sequence设置上限下限和循环

还可以通过修改Sequence将其初始值指定为一个特定值，如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-12-sql-server2012-sequencenumber/sql-server2012-sequencenumber-201203121226326312.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203121226319509.png)

图6.重置Sequence的值

Sequence一个需要注意的情况是Sequence只负责生成序列号，而不管序列号如何使用，如果事务不成功或回滚，SequenceNumber仍然会继续向后生成序列号,如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-12-sql-server2012-sequencenumber/sql-server2012-sequencenumber-201203121226415354.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203121226367344.png)

图7.Sequence仅仅负责生成序列号

我们还可以为Sequence指定缓存选项，使得减少IO，比如，我们指定Cache选项为4，则当前的Sequence由1增长过4后，SQL Server会再分配4个空间变为从5到8，当分配到9时，SQL Server继续这以循环，如果不指定Cache值，则值由SQL Server进行分配。一个简单的例子如图8所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-12-sql-server2012-sequencenumber/sql-server2012-sequencenumber-201203121227006994.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/20120312122645531.png)

图8.为Sequence设置Cache选项

### 总结

本文讲述了SequenceNumber的简单用法。Sequence是一个比较方便的功能，如果使用妥当，将会大大减少开发工作和提升性能。

参考资料:[Sequence Numbers](http://msdn.microsoft.com/en-us/library/ff878058\(v=SQL.110\).aspx)

[CREATE SEQUENCE \(Transact-SQL\)](http://msdn.microsoft.com/en-us/library/ff878091\(v=sql.110\).aspx)
