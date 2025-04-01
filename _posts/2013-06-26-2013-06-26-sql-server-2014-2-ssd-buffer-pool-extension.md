---
layout: post
title: "SQL Server 2014新特性探秘(2)-SSD Buffer Pool Extension"
date: 2013-06-26
categories: blog
tags: [博客园迁移]
---

### 简介

SQL Server 2014中另一个非常好的功能是，可以将SSD虚拟成内存的一部分，来供SQL Server数据页缓冲区使用。通过使用SSD来扩展Buffer-Pool，可以使得大量随机的IOPS由SSD来承载，从而大量减少对于数据页的随机IOPS和PAGE-OUT。

### SSD AS Buffer Pool

SSD是固态硬盘，不像传统的磁盘有磁头移动的部分，因此随机读写的IOPS远远大于传统的磁盘。将SSD作为Buffer Pool的延伸，就可以以非常低的成本巨量的扩充内存。而传统的模式是内存只能容纳下热点数据的一小部分，从而造成比较大的Page-Out，如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-06-26-sql-server-2014-2-ssd-buffer-pool-extension/sql-server-2014-2-ssd-buffer-pool-extension-26194730-e700fa0de9284547a9706c0cb29c30a1.png)](//images0.cnblogs.com/blog/35368/201306/26194730-31a114fd6cfb4dab8852844f67e6b7b0.png)

图1.大量随机的IOPS需要由磁盘阵列所承担

但如果考虑到将SSD加入计算机的存储体系，那么内存可以以非常低的成本扩展到约等于热点数据，不仅仅是提升了性能，还可以减少IO成本，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-06-26-sql-server-2014-2-ssd-buffer-pool-extension/sql-server-2014-2-ssd-buffer-pool-extension-26194731-adf0d902d8d2446a8916a955a72b2645.png)](//images0.cnblogs.com/blog/35368/201306/26194731-0e5154fb56e34a80a851775061b265f2.png)

图2.扩展后内存几乎能HOLD所有热点数据

由图1和图2的对比可以看出，扩展后可以使用更便宜的SATA存储。此外，该特性是透明的，无需应用程序端做任何的改变。

此外，该特性为了避免数据的丢失，仅仅在作为缓冲区的SSD中存储Buffer Pool的Clean Page，即使SSD出现问题，也只需要从辅助存储中Page In页即可。

最后，该特性对于NUMA进行了特别优化，即使拥有超过8个Socket的系统，CPU也能无障碍的访问内存。

### 启用BUFFER Pool Extension

在SQL Server 2014总，启用Buffer Pool Extension非常简单，仅仅需要拥有SysAdmin权限后，输入一个T-SQL语句即可，如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-06-26-sql-server-2014-2-ssd-buffer-pool-extension/sql-server-2014-2-ssd-buffer-pool-extension-26194732-d80ee216a48f4043b528b4b696489251.png)](//images0.cnblogs.com/blog/35368/201306/26194732-4ad094ae47b94e24acb8690c7c37b18e.png)

图3.启用Buffer Pool Extension

对应的，我们可以在物理磁盘中看到这个扩展文件，该文件的性能和Windows的虚拟内存文件非常类似，如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-06-26-sql-server-2014-2-ssd-buffer-pool-extension/sql-server-2014-2-ssd-buffer-pool-extension-26194736-f43fea27d30747f68176021fe2cb8b92.png)](//images0.cnblogs.com/blog/35368/201306/26194735-e5e65e251c7c4c5aa22bdf0bf6ddda0b.png)

图4.对应的Buffer Pool扩展文件

但这里值得注意的是，我们启用的内存扩展无法小于物理内存或阈值，否则会报错，如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-06-26-sql-server-2014-2-ssd-buffer-pool-extension/sql-server-2014-2-ssd-buffer-pool-extension-26194736-b326bbef96b04b30a13345b8ad3625c9.png)](//images0.cnblogs.com/blog/35368/201306/26194736-f9f35ec9335c468ca5ebacdffcd9a1c3.png)

图5.报错信息

对于该功能，SQL Server引入了一个全新的DMV和在原有的DMV上加了一列，来描述Buffer Pool Extention，如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-06-26-sql-server-2014-2-ssd-buffer-pool-extension/sql-server-2014-2-ssd-buffer-pool-extension-26194737-21ff79103a4b4ec2a852e275bf9d7cba.png)](//images0.cnblogs.com/blog/35368/201306/26194737-022a065760544c699e3adee7137c684a.png)

图6.引入的新的DMV和对于原有DMV的更新

此外，对于该特性的监控，SQL Server还引入了大量与之相关的计数器，如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2013-06-26-sql-server-2014-2-ssd-buffer-pool-extension/sql-server-2014-2-ssd-buffer-pool-extension-26194738-f3a5aa4df193499da772119bbd13ec0f.png)](//images0.cnblogs.com/blog/35368/201306/26194737-d1cc2beffadf4392bb85787f1ffb6aaf.png)

图7.相关计数器

### 小结

SQL Server Buffer Pool Extension给我们提供了以更低成本来满足更高企业级需求的可能，结合内存数据库，未来的可能性将无限延伸。
