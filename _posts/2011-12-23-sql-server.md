---
layout: post
title: "理解SQL SERVER中的逻辑读，预读和物理读"
date: 2011-12-23
categories: blog
tags: [博客园迁移]
---

在我的上一篇关于SQL SERVER索引的[博文](http://www.cnblogs.com/CareySon/archive/2011/12/22/2297568.html),有圆友问道关于逻辑读，预读和物理读的概念.我觉的还是写一篇博文能把这个问题解释清楚。

### **SQL SERVER数据存储的形式**

* * *

在谈到几种不同的读取方式之前，首先要理解SQL SERVER数据存储的方式.SQL SERVER存储的最小单位为页\(Page\).每一页大小为8k，SQL SERVER对于页的读取是原子性，要么读完一页，要么完全不读，不会有中间状态。而页之间的数据组织结构为B树（请参考我之前的[博文](http://www.cnblogs.com/CareySon/archive/2011/12/22/2297568.html)\).所以SQL SERVER对于逻辑读，预读，和物理读的单位是页.

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-23-sql-server/sql-server-201112231058509353.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112231058486712.png)

SQL SERVER一页的总大小为:8K

但是这一页存储的数据会是:8K=8192字节-96字节\(页头\)-36字节\(行偏移）=8060字节

所以每一页用于存储的实际大小为8060字节.

比如上面AdventureWorks中的Person.Address表，通过SSMS看到这个表的数据空间为:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-23-sql-server/sql-server-201112231108353465.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112231058546717.png)

我们可以通过公式大概推算出占用了多少页:2.250\*1024\*1024/8060\(每页的数据容量）≈293 - 表中非数据占用的空间≈290（上图中的逻辑读取数）

### **SQL SERVER查询语句执行的顺序**

* * *

SQL SERVER查询执行的步骤如果从微观来看，那将会非常多。这里为了讲述逻辑读等概念，我从比较高的抽象层次来看:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-23-sql-server/sql-server-201112231109137461.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112231108401976.png)

图有些粗糙。

下面我解释一下图。当遇到一个查询语句时，SQL SERVER会走第一步，分别为生成执行计划\(占用CPU和内存资源\),同步的用估计的数据去磁盘中取得需要取的数据\(占用IO资源，这就是预读\),注意，两个第一步是并行的，SQL SERVER通过这种方式来提高查询性能.

然后查询计划生成好了以后去缓存读取数据.当发现缓存缺少所需要的数据后让缓存再次去读硬盘（物理读）

最后从缓存中取出所有数据（逻辑读）。

下面我再通过一个简单的例子说明一下:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-23-sql-server/sql-server-201112231109232944.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112231109156546.png)

这个估计的页数数据可以通过这个DMV看到:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-23-sql-server/sql-server-20111223110949702.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112231109325330.png)

当我们第一次查询完成后，再次进行查询时，所有请求的数据这时已经在缓存中,SQL SERVER这时只要对缓存进行读取就行了，也就是只用进行逻辑读:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-23-sql-server/sql-server-201112231109585596.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112231109557774.png)
