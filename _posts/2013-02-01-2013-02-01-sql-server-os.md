---
layout: post
title: "SQL Server OS的任务调度机制"
date: 2013-02-01
categories: blog
tags: [博客园迁移]
---

### 简介

SQL Server OS是在Windows之上，用于服务SQL Server的一个用户级别的操作系统层次。它将操作系统部分的功能从整个SQL Server引擎中抽象出来，单独形成一层，以便为存储引擎提供服务。SQL Server OS主要提供了任务调度、内存分配、死锁检测、资源检测、锁管理、Buffer Pool管理等多种功能。本篇文章主要是谈一谈SQL OS中所提供的任务调度机制。

### 抢占式\(Preemptive\)调度与非抢占式\(non-Preemptive\)调度

数据库层面的任务调度的起源是ACM上的一篇名为“Operating System Support for Database Management”。但是对于Windows来说，在操作系统层面专门加入支持数据库的任务调度，还不如在SQL Server中专门抽象出来一层进行调度，既然可以抽象出来一层进行数据库层面的任务调度，那么何不在这个抽象层进行内存和IO等的管理呢？这个想法，就是SQL Server OS的起源。

在Windows NT4之后，Windows任务调度是抢占式的，也就是说Windows任务是根据任务的优先级和时间片来决定。如果一个任务的时间片用完，或是有更高优先级的任务正在等待，那么操作系统可以强制剥夺正在运行的线程（线程是任务调度的基本单位）所占用的CPU，将CPU资源让给其它线程。

但是对于SQL Server来说，这种非合作式的、基于时间片的任务调度机制就不那么合适了。如果SQL Server使用Windows内的任务调度机制来进行任务调度的话，Windows不会根据SQL Server的调度机制进行优化，只是根据时间片和优先级来中断线程，这会导致如下两个缺陷:

  * Windows不会知道SQL Server中任务\(也就是SQL OS中的Task,会在文章后面讲到\)的最佳中断点，这势必会造成更多的Context Switch（Context Switch代价非常非常高昂,需要线程字用户态和核心态之间转换），因为Windows调度不是线程本身决定是否该出让CPU，而是由Windows决定。Windows并不会知道当前数据库中对应的线程是否正在做关键任务，只会不分青红皂白的夺取线程的CPU。 
  * 连入SQL Server的连接不可能一直在执行，每一个Batch之间会有大量空闲时间。如果每个连接都需要单独占用一个线程，那么SQL Server维护这些线程就需要消耗额外的资源，这是很不明智的。 



而对于SQL Server OS来说，线程调度采用的合作模式而不是抢占模式。这是因为这些数据库内的任务都在SQL Server这个SandBox之内，SQL Server充分相信其内线程，所以除非线程主动放弃CPU，SQL Server OS不会强制剥夺线程的CPU。这样一来，虽然Worker之间的切换依然是通过Windows的Context Switch进行，但这种合作模式会大大减少所需Context Switch的次数。

SQL Server决定哪一个时间点哪一个线程运行，是通过一个叫Scheduler的东西进行的，下面让我们来看Scheduler。

### Scheduler

SQL Server中每一个逻辑CPU都有一个与之对应的Scheduler，只有拿到Scheduler所有权的任务才允许被执行，Scheduler可以看做一个队SQLOS来说的逻辑CPU。您可以通过sys.dm\_os\_schedulers这个DMV来看系统中所有的Scheduler，如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-02-01-sql-server-os/sql-server-os-01101424-f2aed074137c43a6a2d68601a6f51bc9.png)](//images0.cnblogs.com/blog/35368/201302/01101423-ab9705fcd41c4cfaac694451a8e4c4b4.png)

图1.查看sys.dm\_os\_schedulers

我的笔记本是一个i7四核8线程的CPU，对应的，可以看到除了DAC和运行系统任务的HIDDEN Scheduler，剩下的Scheduler一共8个，每个对应一个逻辑CPU，用于处理内部Task。当然，您也可以通过设置Affinity来将某些Scheduler Offline，如图2所示。注意，这个过程是在线的，无需重启SQL Server就能实现。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-02-01-sql-server-os/sql-server-os-01101426-074571da750e425587a775c4ba650f91.png)](//images0.cnblogs.com/blog/35368/201302/01101425-aaa5a87e988a492ba85075620e99fdb5.png)

图2.设置Affinity

此时，无需重启实例就能看到4个Scheduler被Offline,如图3所示:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-02-01-sql-server-os/sql-server-os-01101427-b8599ad1ee0446de8bbb8435f920b116.png)](//images0.cnblogs.com/blog/35368/201302/01101427-41666af6ab8a4898960c3c1200b4f558.png)

图3.在线Offline 4个Scheduler

一般来说，除非您的服务器上运行其他实例或程序，否则不需要控制Affinity。

在图1中，我们还注意到，除了Visible的Scheduler之外，还有一些特殊的Scheduler，这些Scheduler的ID都大于255，这类Scheduler都用于系统内部使用，比如说资源管理、DAC、备份还原操作等。另外，虽然Scheduler和逻辑CPU的个数一致，但这并不意味着Scheduler和固定的逻辑CPU相绑定，而是Scheduler可以在任何CPU上运行，只有您设置了Affinity Mask之后，Scheduler才会被固定在某个CPU上。这样的一个好处是，当一个Scheduler非常繁忙时，可能不会导致只有一个物理CPU繁忙，因为Scheduler会在多个CPU之间移动，从而使得CPU的使用倾向于平均。

这意味着对于一个比较长的查询，可以前半部分在CPU0上执行，而后半部分在CPU1上执行。

另外，在每一个Scheduler上，同一时间只能有一个Worker运行，所有的资源都就绪但没有拿到Scheduler，那么这个Worker就处于Runnable状态。下面让我们来看一看Worker。

### Worker

每一个Worker可以看做是对应一个线程（或纤程），Scheduler不会直接调度线程，而是调度Worker。Worker会随着负载的增加而增加，换句话说，Worker是按需增加，直到增加到最大数字。在SQL Server中，默认的Worker最大数是由SQL Server进行管理的。根据32位还是64位，以及CPU的数量来设置最大Worker,具体的计算公式，您可以参阅BOL：<http://msdn.microsoft.com/zh-cn/library/ms187024(v=sql.105).aspx>。当然您也可以设置最大Worker数量，如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-02-01-sql-server-os/sql-server-os-01101429-863b2518ef544d9eb1a4eebce3df01ac.png)](//images0.cnblogs.com/blog/35368/201302/01101428-67e52100dca04e6ba33a2404da0ef09e.png)

图4.设置最大Worker数量

如果是自动配置，那么SQL Server的最大工作线程数量可以在sys.dm\_os\_sys\_info中看到，如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-02-01-sql-server-os/sql-server-os-01101430-7e9c95348d594e3d8a2c7ab713338aa2.png)](//images0.cnblogs.com/blog/35368/201302/01101429-9b787a916ee64da88445d6d5b95e4e82.png)

图5.查看自动配置的最大Worker数量

一般来说，这个值您都无需进行设置，但也有一些情况，需要设置这个值。那就是Worker线程用尽，此时除了DAC之外，您甚至无法连入SQL Server。

Worker实际上会对应Windows上的一个线程，并与某个特定Scheduler绑定，每一个Worker只要开始执行Task,除非Task完成，否则Worker永远不会放弃这个Task,如果一个Task在运行过程由于锁、IO等陷入等待，那么实际上Worker就会陷入等待。

此外，同一个连接内的多个Batch之间倾向于使用同一个Worker,比如第一个Batch使用了Worker 100,那么第二个Batch也同样倾向于是用Worker 100，但这并不绝对。

正在运行的任务所是用的Worker，我们可以通过DMV sys.dm\_exec\_requests查看正在运行的任务，其中的Task\_Address列可以看到正在运行的Task,再通过sys.dm\_os\_tasks的Worker\_Address来查看对应的Worker。

SQL Server会为每一个Worker保留大约2M左右的内存，对于每一个Scheduler上所能有的Worker数量是服务器的最大Worker数量/在线的Scheduler,每一个Scheduler所绑定的Worker会形成Worker池，这意味着每一个Scheduler需要Worker时，首先在Worker池中中查找空闲的Worker，如果没有空闲的Worker时，才会创建新的Worker。这个行为会和连接池类似。

那么当一个Scheduler空闲超过15分钟，或是Windows面临内存压力时。SQL Server就会尝试Trim这个Worker池来释放被Worker所占用的内存。

### Task

Task是Worker上运行的最小任务单元。只能拿到Worker的Task才能够运行。我们可以看下面一个简单的例子，如代码1所示。
    
    
    [SELECT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SELECT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) @@VERSION 
    [go](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=go&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    
    [SELECT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SELECT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) @@SPID 
    [go](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=go&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)

  


代码1.一个连接上的两个Batch

代码1中的两个Batch属于一个连接，每一个Batch中都是一个简单的Task,如我们前面所说，这两个Task更倾向于复用同一个Worker，因为他们属于同一个连接。但也有可能，这两个Task使用了不同的Worker,甚至是不同的Scheduler。

除了用户所用的Task之外，还有一些永久的系统Task，这类Task会永远占据Worker,这些Task包括死锁检测、Lazy Writer等。

**Task在Scheduler上的平均分配**

新的Task还会尝试在Scheduler之间平均分配，可以通过sys.dm\_os\_schedulers来看到一个load\_factor列，这列的值就是用于供Task向Scheduler进行分配时，用来参考。

每次一个新的Task进入Node时，会选择负载最少的的Scheduler。但是，如果每次都来做一次选择，那么就会在Task入队时造成瓶颈\(这个瓶颈类似于TempDB SGAM页争抢\)。因此SQL OS对于每一个连接，都会记住上次运行的Scheduler ID，在新的Task进入时作为提示\(Hint\)。但如果一个Scheduler的负载大于所有Scheduler平均值的20%，则会忽略这个提示。负载可以通过上面提到的load\_factor列来看，对于某个Task运行的时间比较长，则很有可能造成Scheduler上Task分配的不均匀。

### Worker的Yield

由于SQL Server是非抢占式调度，那么就不能为了完成某个Task，让Worker占据Scheduler一直运行。如果是这样，那么处于Runnable的Worker将会饥饿，这不利于大量并发，也违背了SQL OS调度的初衷。

因此，在合适的时间点让出Scheduler就是关键。Worker让出CPU使得其它Worker可以运行的过程称之为yield。yield大体可分为两种，一种是所谓的“natural yield”,这种方式是Worker在运行过程中被锁或是某些资源阻塞，此时，该Worker就会让出Scheduler来让其它Worker运行。另外一种情况是Worker没有遇到阻塞，但在时间片到了之后，主动让出Scheduler,这就是所谓的“voluntarily yield”，这也就是SOS\_SCHEDULER\_YIELD等待类型的由来，一个Worker由RUNNING状态转到WAITING状态的过程被称之为switching。SQL OS的一个基本思想就是，要多进行switching，来保证高并发。下面我们来看几种常见的yield场景:

  * 基于时间片的voluntarily yield大概使得Worker每4秒yield一次。这个值可以通过sys.dm\_os\_schedulers的quantum\_length\_us列看到。

  * 每64K结果集排序，就做一次yield。

  * 语句complie,会做yield。

  * 读取数据页时

  * batch中每一句话做完，就会做一次yield。

  * 如果客户端不能及时取走数据，worker也会做yield。




### SQL Server OS中的抢占式任务调度

对于一些代码来说，SQL Server会存在一些抢占式代码。如果您在等待类型中看到“PREEMPTIVE\_\*”类型的等待，说明这里面的代码正在运行在抢占式任务调度模式。这类任务包括扩展存储过程、调用Windows API、日志增长（日志填0）。我们知道，合作式的任务调度需要任务本身Yield，但这类代码在SQL Server 之外，如果让他们运行在合作式任务调度这个SandBox之内，这类代码如果不yield，则会永远占用Scheduler。这是非常危险的。

因此，在进入抢占式模式之前，首先需要将Scheduler的控制权交给在Runable队列中的下一个Worker。此时，抢占式模式运行的代码不再由SQL OS控制，转而由Windows任务调度系统控制。因此一个Task的生命周期如果再加上转到抢占式任务调度模式，则会如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-02-01-sql-server-os/sql-server-os-01101431-8ccd7b568c7649779bfa36fe8006357a.png)](//images0.cnblogs.com/blog/35368/201302/01101430-dd3abd1618d84623ada1073640208c6b.png)

图6.一个Task完整的生命周期

### 每一个Scheduler的任务调度

对于每一个Scheduler的调度，一个简单的模型如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-02-01-sql-server-os/sql-server-os-01101432-20860e550ae14e1c9cf9c641d1957160.png)](//images0.cnblogs.com/blog/35368/201302/01101432-80e0491abdad495e8b6ebc37fd155878.png)

图7.一个Scheduler的调度周期模型

### 小结

SQL Server OS在Windows之上抽象出一套非抢占式的任务调度机制，从而减少了Context Switch。同时，又有一套线程自己的yield机制，相比Windows随机抢占数据库之内的线程而言，让线程自己来yield则会大量减少Context Switch,从而提升了并发性。
