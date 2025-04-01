---
layout: post
title: "浅谈SQL Server 对于内存的管理"
date: 2012-08-16
categories: blog
tags: [博客园迁移]
---

### 简介

理解SQL Server对于内存的管理是对于SQL Server问题处理和性能调优的基本，本篇文章讲述SQL Server对于内存管理的内存原理。

### 二级存储\(_secondary storage_\)

对于计算机来说，存储体系是分层级的。离CPU越近的地方速度愉快，但容量越小\(如图1所示\)。比如：传统的计算机存储体系结构离CPU由近到远依次是:CPU内的寄存器，一级缓存，二级缓存，内存，硬盘。但同时离CPU越远的存储系统都会比之前的存储系统大一个数量级。比如硬盘通常要比同时代的内存大一个数量级。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-20120816073722310.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/201208/201208160737221456.jpg)

图1.计算机存储体系

因此对于SQL Server来说，正常的生产系统所配置的内存通常不能装载所有数据，因此会涉及到二级存储,也就是磁盘。磁盘作为现代计算机系统中最后的机械存储部件，读取数据需要移动磁头（具体关于磁盘的原理，可以看我之前写的一篇[文章](http://www.cnblogs.com/CareySon/archive/2012/04/06/Imple-BTree-With-CSharp.html)）,并且由于数据库所访问的数据往往是随机分布在磁盘的各个位置,因此如果频繁的读取磁盘需要频繁的移动磁头,这个性能将会十分底下。

由计算机体存储体系结构可以知道，计算机对于所有硬盘内数据的操作都需要首先读取到内存，因此利用好内存的缓冲区而减少对磁盘IO的访问将会是提升SQL Server性能的关键，这也是本篇文章写作的出发点之一。

### SQL Server引擎，一个自我调整的引擎

由于SQL Server过去一直面向是中小型企业市场的原因，SQL Server存储引擎被设计成一个不需要太多配置就能使用的产品，从而减少了部署成本，但这也是很多人一直诟病的微软开放的配置过少。而对于SQL Server如何使用内存,几乎没有直接可以配置的空间，仅仅开放的配置只有是否使用AWE,以及实例占用的最大或最小内存，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-201208160737239655.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/201208/20120816073723801.jpg)

图2.SQL Server可控控制内存的选项

而对于具体的SQL Server如何使用内存，例如分配给执行计划缓存多少，分配给数据buffer多少，这些都无法通过配置进行调控。这也是很多其它技术的开发人员对于使用微软技术的开发人员充满优越感的原因，而在我看来，虽然SQL Server提供可控配置的地方很少，但是很多地方都可以在通晓原理的情况下进行“间接”的配置。这也需要了解一些Windows的原理。

### SQL Server是如何使用内存的

SQL Server存储引擎本身是一个Windows下的进程，所以SQL Server使用内存和其它Windows进程一样，都需要向Windows申请内存。从Windows申请到内存之后，SQL Server使用内存粗略可以分为两部分：缓冲池内存（数据页和空闲页）,非缓冲内存\(线程，DLL,链接服务器等\)。而缓冲池内存占据了SQL Server的大部分内存使用。缓冲池所占内存也就是图2最大最小内存所设置的，因此sqlservr.exe所占的内存有可能会大于图2中所设置的最大内存。

还有一点是，SQL Server使用内存的特点是：有多少用多少，并且用了以后不释放\(除非收到Windows内存压力的通知\)。比如我所在公司的开发服务器，在几乎没有负载的时候来看内存使用，如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-201208160737256666.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/201208/201208160737243733.jpg)

图3.SQL Server 进程的内存使用

可以看到CPU在0负载的时候，内存却占据了13个G。这其实是在之前的使用SQL Server向Windows申请的内存一直没有释放所致。

具体SQL Server能够使用多少内存是由以下几个因素决定的：

1.物理内存的大小

2.所安装Windows版本对于内存的限制\(比如windows server 2008标准版限制最大内存只能使用32GB\)

3.SQL Server是32位或64位

4.如图2所示配置SQL Server对于内存的使用量

5.SQL Server的版本\(比如express版只能用1G内存\)

### SQL Server OS的三层内存分配

SQL Server OS对于内存的分配分为三个层级,依赖关系如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-201208160737266916.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/201208/201208160737258585.jpg)

图4.SQL Server OS内存依赖关系

**Memory Node**

首先最底层的是Memory Node,Memory Node的作用是使得分配内存由Windows移交到SQL Server OS层面执行。每个SQL Server实例通常都只拥有一个Memory Node,Memory Node的多寡只取决于NUMA构架的硬件配置。我们通过 DBCC MEMORYSTATUS 可以看到Memory Node的一些信息,如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-201208160737262946.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201208/201208160737266883.png)

图5.查看Memory Node信息

我们可以看出 ，按照申请内存大小分类，可以分为两部分

1.申请小于等于8KB为一个单位的内存，这些内存被用于缓存。\(图5中的SinglePage Allocator\)

2.申请大于8KB为一个单位的内存，这些内存称为Multi-Page（或MemToLeave）\(图5中的MultiPage Allocator\)

对于为什么叫MemToLeave,被称为MemToLeave的原因是由于SQL Server虽然大部分内存被用于缓冲区，但还需要一些连续的内存用于SQL CLR,linked server,backup buffer等操作，32位SQL Server在启动实例时会保留一部分连续的虚拟地址（VAS）用于进行MultiPage Allocator。具体保留多少可以用如下公式计算：

保留地址=\(\(CPU核数量-4\)+256\)\*0.5MB+256MB,通常在384MB左右。

**Memory Clerk**

**** 让我们再来看Memory Clerk,Memory Clerk用于分配内存，用于将Allocate出去的内存进行分类，可以简单的进行如下语句,如图6所示.

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-201208160737278420.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201208/201208160737267373.png)

图6.按照Memory Clerk的类别进行分类

注意：由图4可以看到，Memory Clerk只是分配内存的一部分，另一部分是数据缓存（Buffer Pool\)

### Buffer Pool

在开始讲述Buffer Pool之前，首先想讲一下虚拟内存。

在Windows中每个进程都有一个虚拟内存\(Virtual Address Space VAS\)，32位系统是2的32次方，也就是4G，这4G被Windows划为两部分，一部分是Windows使用，另一部分才是应用程序使用。虚拟内存并不是实际的物理内存，而是对于物理内存的映射，当物理内存不存在虚拟内存指向的内容时，产生缺页中断，将一部分页面置换出内存，然后将需要的部分从硬盘读到内存，关于这块，可以读我之前写的一篇文章:[浅谈操作系统对内存的管理](http://www.cnblogs.com/CareySon/archive/2012/04/25/2470063.html)。

因此Buffer Pool的作用是缓冲数据页，使得未来读取数据时减少对磁盘的访问。

这个Buffer Pool这部分就是图2中设置最大最小服务器内存所占用的空间。这个最小值并不意味着SQL Server启动时就能占用这么多内存，而是SQL Server Buffer Pool的使用一旦超过这个值，就不会再进行释放了。

在DBCC MEMORYSTATUS 其中有一部分我们可以看到Buffer Pool的信息，如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-201208160737278910.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201208/201208160737279259.png)

图7.Buffer Pool的相关信息

在SQL Server实例启动时，Buffer Pool所保留的VAS地址空间取决于多个因素:包括实际的物理内存和SQL Server是32位或是64位（这个限制32位是4G，还要划一半给Windows和减去MemToLeave空间）,而对于实际上SQL Server所使用的物理内存，可以通过如下语句查看，如图8所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-201208160737282748.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201208/201208160737287241.png)

图8.查看Buffer Pool所使用物理内存

Buffer Pool会按照需要不断的提出内存申请。Buffer Pool如果需要，Buffer Pool会不断消耗内存，直到Windows通知SQL Server内存过低时，Buffer Pool才有可能释放内存，否则Buffer Pool占据了内存不会释放。

另外值得注意的一点是，Buffer Pool所分配的页面和SQL Server OS页面大小是一致的，也就是8192字节，当SQL Server其它部分需要向”Buffer Pool”借内存时,也只能按照8k为单位借，并且这部分内存在物理内存中是不连续的，这听上去像是Buffer Pool内存管理自成体系![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-201208160737285223.png)，可以这么理解，因为Buffer Pool 不使用任何SQL Server的page allocator,而直接使用virtual或AWE SQLOS's的接口。

所以SQL Server所占用的内存可以用这个公式粗略估算出来: buffer pool占用的内存+从buffer pool借的页占得内存+multiPageAllocator分配的非buffer pool内存，如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-201208160737299617.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201208/201208160737281286.png)

图9.可以近似的估算出sql server所占的内存

**Memory Object**

**** menory object本质上是一个堆,由Page Allocator进行分配，可以通过sys.dm\_os\_memory\_objects这个DMV进行查看，这个DMV可以看到有一列Page\_Allocator\_Address列，这列就是Memory Clerk的标识，表明这个Memory Object是由哪个Memory Clerk进行分配的。

### 32位SQL Server的内存瓶颈

由文章前面所述的一些基本原理可以看出，由于32位的SQL Server使用的是VAS进行地址分配，因此寻址空间被限制在4GB，这4GB还要有一半分给Windows,使得Buffer Pool最多只能用到2G的内存，这使得32位SQL Server即使有多余的物理内存，也无法使用。

解决办法之一是通过减少Windows默认占用的2G到1G，使得SQL Server可以使用的内存变为3G。这个可以通过在Windows Server 2008中的命令行键入 BCDEdit /set设置increaseuserva选项，设置值为3072MB，对于Windows Server 2003来说，需要在boot.ini中加上/3gb启动参数。

另一种办法是使用AWE（ _Address_ _Window_ Extension）分配内存。AWE通过计算机物理地址扩展\(Physical Address Extension PAE\)，增加4位，使得32位的CPU寻址范围增加到2的36次方，也就是64GB。基本解决了寻址范围不够的问题。

**VirtualAlloc和AllocateUserPhysicalPages**

**** VirtualAlloc和AllocateUserPhysicalPages是SQL Server向Windows申请内存所使用的方法。在默认情况下，SQL Server所需要的所有内存都会使用VirtualAlloc去Windows申请内存，这种申请是操作系统层面的，也就是直接对应的虚拟内存。这导致一个问题，所有通过VirtualAlloc分配的内存都可以在Windows面临内存压力时被置换到虚拟内存中。这会造成IO占用问题。

而使用AllocateUserPhysicalPages所申请的内存，直接和更底层的页表\(Page Table\)进行匹配，因此使用这个方法申请的内存不会被置换出内存。在32位SQL Server的情况下，通过开启AWE分配内存，buffer pool中的data cache部分将会使用这个函数，而MemToLeave部分和Buffer Pool中的另一部分内存（主要是执行计划缓存）依然通过****VirtualAlloc进行内存分配。

因此在开启通过AWE分配内存之前，SQL Server首先需要对应的权限，否则就会在日志中报错，如图10所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-201208160737298156.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201208/201208160737292092.png)

图10.开启AWE却没有开启对应权限报错

我们可以在组策略里设置启动SQL Server的账户拥有这个权限，如图11所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-08-16-sql-server/sql-server-201208160737308057.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201208/201208160737307566.png)

图11.锁定内存页\(Lock Page In Memory\)

### 64位SQL Server的问题

64位Windows基本已经不存在上述的内存问题，但是依然要注意，在默认情况下，64位的SQL Server使用的依然是VirtualAlloc进行内存分配，这意味着所有分配的内存都会在Windows面临压力时将页置换出去，这很可能造成抖动（Buffer Pool Churn）,这种情况也就是SQL Server Buffer Pool中的页不断的被交换进硬盘，造成大量的IO占用\(可以通过sys.dm\_exec\_query\_memory\_grants这个DMV查看等待内存的查询\),因此64位SQL Server将Buffer Pool中的Date Page通过AllocateUserPhysicalPages来进行内存分配就能避免这个问题。与32位SQL Server不同的是，64位SQL Server并不需要开启AWE,只需开启如图11所示的“Lock Page In Memory”就行了。

但这又暴漏出了另一个问题，因为SQL Server锁定了内存页，当Windows内存告急时，SQL Server就不能对Windows的内存告急做出响应（当然了Buffer Pool中的非data cache和MemToLeave部分依然可以，但往往不够，因为这部分内存相比Data Cache消耗很小），因为SQL Server的特性是内存有多少用多少，因此很有可能在无法做出对Windows低内存的响应时造成Windows的不稳定甚至崩溃。因此开启了”Lock Page In Memory”之后，要限制SQL Server Buffer Pool的内存使用，前面图2中已经说了，这里就不再细说了。

还有一个问题是当Buffer Pool通过AllocateUserPhysicalPages分配内存时，我们在任务管理器中看到的sqlservr.exe占用的内存就仅仅包含Buffer Pool中非Data Cache部分和MemToLeave部分，而不包含Data Cache部分，因此看起来有可能造成sqlservr.exe只占用了几百兆内存而内存的使用是几十G。这时我们就需要在Perfmon.exe中查看SQL Server:Memory Manager\Total Server Memory计数器去找到SQL Server真实占用的内存。

### 总结

本文讲述了SQL Server对内存管理的基本原理和SQL Server对内存使用所分的部分，对于SQL Server性能调优来说，理解内存的使用是非常关键的一部分，很多IO问题都有可能是内存所引起的。

  
  
  
  
[点击这里下载本文的PDF版本](https://files.cnblogs.com/CareySon/SQLServer%E5%AF%B9%E4%BA%8E%E5%86%85%E5%AD%98%E7%9A%84%E7%AE%A1%E7%90%86.pdf)
