---
layout: post
title: "TempDB为什么要根据CPU数目来决定文件个数"
date: 2012-10-06
categories: blog
tags: [博客园迁移]
---

在SQL Server的世界中，SQL Server在Windows之上有一套自己的任务调度和资源分配系统，这使得SQL Server作为Windows的一个进程，却可以处理大量的并发，这些任务调度和资源分配非常像一个操作系统，因此SQL Server在Windows之上，有一层被称为SQL OS的系统。

类似Windows进程之间的任务调度，SQL Server OS也有一套自己的调度方案，在早期的SQL Server曾经使用Windows自带的进程调度系统，但由于SQL Server是一个处理高并发的进程，因此Windows调度造成的线程切换\(Context Switch\)会带来很多的资源浪费，并且Windows调度是抢占式调度，这对于SQL Server来说非常不利，因此SQL Server OS通过非抢占式调度算法来调度进程，除非线程自己释放资源，SQL Server不会强制剥夺资源（当然了，一些极端情况比如死锁，或是检查scheduler时发现不利问题，会记录到日志，但依然不会抢占资源），这也使得开发人员对T-SQL语句需要小心，当然了这是题外话了。

在了解了SQL Server基本的调度算法后，再让我们通过一个图来了解一下简单的SQL Server中线程的几种状态（这类线程对Windows来说是线程，对SQL Server来说是进程，这也是为什么查询这些线程的时候用的是Sysprocess![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-10-06-tempdb-cpu/tempdb-cpu-2012100619150176.png)）,如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-10-06-tempdb-cpu/tempdb-cpu-201210061915045390.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201210/201210061915024145.png)

图1.SQL Server OS的简单算法

如果你了解操作系统的调度算法的话，你会发现这里和操作系统的形式一样，当线程得到等待的资源并获得CPU时，就会是运行状态，而当获得资源没有CPU时，就会是Runnable状态，或是当线程所需的资源没有到位时，就会是阻塞状态。

因此，多个CPU可以有多个线程在Running状态。

另外在SQL Server中，每创建一个新表时，都会为表分配存储页面，相应的，SQL Server也需要修改GAM,SGAM和FPS页。对于修改这些页来说，SQL Server需要在修改的时候加上一个轻量级的锁，这也就是所谓的闩锁\(Latch\)。当多个线程同时需要修改GAM,SGAM,FPS页时，闩锁会造成阻塞。对于用户数据库来说，不可能一直存在DDL操作，但对于Tempdb来说，会经常进行建表和删表，因此对于GAM,SGAM以及FPS页都会经常修改，如果Tempdb只有一个文件而CPU存在多核的时候，多个同时运行的任务有可能争抢GAM，SGAM，FPS页的修改权，因此造成阻塞，这对性能是非常不利的，而按照CPU个数将TempDB的文件分为多份，则会存在多个GAM,SGAM,FPS页。多个Running的线程会按照每个文件的大小平均分布到不同的文件中，因此解决了争用问题。

另外，值得注意的是，对于TempDB的最佳做法是一开始就为每一个文件分配足够大的值。并且每个文件大小相等，这就避免了某个文件增长导致的文件大小不一，而SQL Server对于文件的使用比率是按照文件大小，如果文件大小不一样，就会造成热点文件，从而有可能造成闩锁争用。
