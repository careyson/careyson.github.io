---
layout: post
title: "SQL Server中的GAM页和SGAM页"
date: 2012-09-12
categories: blog
tags: [博客园迁移]
---

###  简介

我们已经知道SQL Server IO最小的单位是页,连续的8个页是一个区。SQL Server需要一种方式来知道其所管辖的数据库中的空间使用情况，这就是GAM页和SGAM页。

### Global Allocation Map Page

GAM\(全局分配位图\)是用于标识SQL Server空间使用的位图的页。位于数据库的第3个页，也就是页号是2的页。下面我们通过新建一个数据库来看其GAM的结构。创建测试数据库的代码如代码所示。
    
    
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [DATABASE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DATABASE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [test] [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)  [PRIMARY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=PRIMARY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 
    ( NAME = N'test', FILENAME = N'C:\Test\test.mdf' , [SIZE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SIZE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) = 3072KB , MAXSIZE = UNLIMITED, FILEGROWTH = 1024KB )
     LOG [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 
    ( NAME = N'test_log', FILENAME = N'C:\Test\test_log.ldf' , [SIZE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SIZE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) = 2048KB , MAXSIZE = 2048GB , FILEGROWTH = 10%)
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)

代码1.创建测试数据库

数据库创建成功后，通过查看数据库页号为2的页。我们看到如图1所示的结果。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-09-12-sql-server-gam-sgam/sql-server-gam-sgam-201209121445244995.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201209/201209121445242454.png)

图1.GAM页示例

我们看到页内的数据通过16进制表示。也就是一个数字是4比特，两个是一字节。其中前4个字节0000381f是系统信息，slot1的后10个字节也是系统信息。其余的每位表示SQL Server的一个区的状态，0表示已分配，1表示未分配。下面我们就通过图1所示的GAM页来计算一下这个数据库所占的空间。

我们可以看到，由于数据库刚刚创建，分配的空间在第4-8个字节就能表示，也就是0001c0ff。下面将0001c0ff由16进制化为2进制。结果是

0000 0000 0000 0001 1100 0000 1111 1111

通过计算，可以看出，上面的bit中有21个0，也就是目前数据库已经分配了21个区，我们知道每个区是8\*8k=64K。因此算出这个数据库占用空间\(21\*64\)/1024=1.3125MB≈1.31MB

下面我们通过SSMS来看数据库实际占用的空间，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-09-12-sql-server-gam-sgam/sql-server-gam-sgam-201209121445257570.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201209/201209121445259489.png)

图2.通过SSMS来看数据库所占的空间

通过上面的计算3-1.69=1.31MB和通过GAM页进行计算的结果完全吻合。

那可能大家会有疑问了，那如果数据库增长超过一个GAM所能表示的区的范围那该怎么办？答案很简单，就是再创建一个GAM页，第二个GAM页的位置也可以通过图1中的信息进行计算。图1中slot1有7992个字节，其中前四个字节用于存储系统信息，后面7988字节用于表示区的情况，因此所能表示的区是7988\*8=63904,横跨的页的范围是511232,所以第511232+1页应该是下一个GAM页，而页号就会是511232页。这个区间也就是所谓的GAM Interval,接近4GB。

### Shared Global Allocation Map Page

通过GAM页可知，分配空间的最小单位是区。但假如一个非常小的索引或是表只占1KB，但要分给其64K的空间就显得过于奢侈了。所以当几个表或索引都很小时，可以让几个表或索引公用一个区，这类区就是混合区。而只能让一个表或索引使用的区就是统一区。SGAM位于数据库的第四页，也就是GAM的下一个页。页号为3。通过和GAM相同位置的bit组合，就能知道空间的状态。所能表示的几种状态如表1所示。

| GAM | SGAM位  
---|---|---  
未分配 | 1 | 0  
统一区或空间使用完的混合区 | 0 | 0  
含有可分配空间的混合区 | 0 | 1  
  
表1.SGAM和GAM

通过SGAM和GAM的组合,SQL Server就能知道该从哪里分配空间。

第二个SGAM页位于第二个GAM页之后，也就是页号为511233的页。依此类推。
