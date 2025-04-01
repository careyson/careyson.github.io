---
layout: post
title: "SQL Server中In-Flight日志究竟是多少"
date: 2013-07-17
categories: blog
tags: [博客园迁移]
---

在SQL Server中，利用日志的WAL来保证关系数据库的持久性，但由于硬盘的特性，不可能使得每生成一条日志，就直接向磁盘写一次，因此日志会被缓存起来，到一定数据量才会写入磁盘。这部分已经生成的，却没有写入磁盘的日志，就是所谓的In-Flight日志。

在SQL Server中，In-Flight的日志的大小取决于两个因素，根据Paul Randal的说法，In-Flight日志不能超过60K，因此In-Flight的日志最大是60K，此外，如果In-Flight日志没有到60K，如果发生了Commit或Rollback，那么直接会写入磁盘。因此日志最小为512字节，最大为60K，以512字节为单位进行增长。下面我们来看一个例子。

我们首先建立一个简单的表，循环向其中插入10W的数据，该语句会生成大量的日志，如代码清单1所示：
    
    
    [BEGIN](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BEGIN&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [TRAN](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=TRAN&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
     
    [DECLARE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DECLARE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) @i [INTEGER](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=INTEGER&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
     
    [SET](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SET&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) @i = 0
     
    [WHILE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=WHILE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ( @i < 100000 ) 
        [BEGIN](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BEGIN&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
     
            [INSERT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=INSERT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)  [INTO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=INTO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) Number
            [VALUES](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=VALUES&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)  ( @i )
     
            [SET](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SET&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) @i = @i + 1
        [END](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=END&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
     
    [CHECKPOINT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CHECKPOINT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
     
    [COMMIT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=COMMIT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
     

  


代码清单1.生成大量日志的语句

数据库我以5M日志为起点，以5M递增，上面的语句导致日志自动增长，如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-07-17-sql-server-in-flight/sql-server-in-flight-17103757-019010ca30594448841836825cd59cce.jpg)](//images0.cnblogs.com/blog/35368/201307/17103753-cf496f82e45f49e3a44c7446c8b01658.jpg)

图1.对应的6次日志增长

我们再来观察SQL Server进程对于日志文件的操作，如图2所示：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-07-17-sql-server-in-flight/sql-server-in-flight-17103834-4aec9e2337e84175b8c6ec6cbbae833a.jpg)](//images0.cnblogs.com/blog/35368/201307/17103820-5b98cc9db3684117993074a739de2064.jpg)

图2.SQL Server进程对于日志文件的写

图2中的图片我只截取了一小部分，但是可以看到没有超过60K的log block，只有在日志文件填零增长时，才出现5M的块。因此我对于微软亚太数据库支持组的博文：<http://blogs.msdn.com/b/apgcdsd/archive/2013/06/17/sql-server-log-write.aspx>中说到会出现超过60K的log write产生一些疑问，毕竟日志填零增长和logWrite不是一回事。

因此，得知这一点之后，对于日志所在的LUN，分配单元64K应该是对于性能来说最优的。
