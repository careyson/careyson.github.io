---
layout: post
title: "T-SQL查询进阶--理解SQL Server中索引的概念，原理以及其他"
date: 2011-12-22
categories: blog
tags: [博客园迁移]
---

### **简介**

* * *

在SQL Server中，索引是一种增强式的存在，这意味着，即使没有索引，SQL Server仍然可以实现应有的功能。但索引可以在大多数情况下大大提升查询性能，在OLAP中尤其明显.要完全理解索引的概念，需要了解大量原理性的知识，包括B树，堆，数据库页，区，填充因子，碎片,文件组等等一系列相关知识，这些知识写一本小书也不为过。所以本文并不会深入讨论这些主题。

### **索引是什么**

* * *

索引是对数据库表中一列或多列的值进行排序的一种结构，使用索引可快速访问数据库表中的特定信息。

精简来说，索引是一种结构.在SQL Server中，索引和表（这里指的是加了聚集索引的表）的存储结构是一样的,都是B树，B树是一种用于查找的平衡多叉树.理解B树的概念如下图:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-22-t-sql-sql-server/t-sql-sql-server-201112221217494923.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112221217483886.jpg)

理解为什么使用B树作为索引和表（有聚集索引）的结构，首先需要理解SQL Server存储数据的原理.

在SQL SERVER中，存储的单位最小是页\(PAGE\),页是不可再分的。就像细胞是生物学中不可再分的，或是原子是化学中不可再分的最小单位一样.这意味着,SQL SERVER对于页的读取，要么整个读取，要么完全不读取，没有折中.

在数据库检索来说，对于磁盘IO扫描是最消耗时间的.因为磁盘扫描涉及很多物理特性，这些是相当消耗时间的。所以B树设计的初衷是为了减少对于磁盘的扫描次数。如果一个表或索引没有使用B树（对于没有聚集索引的表是使用堆heap存储\),那么查找一个数据，需要在整个表包含的数据库页中全盘扫描。这无疑会大大加重IO负担.而在SQL SERVER中使用B树进行存储，则仅仅需要将B树的根节点存入内存，经过几次查找后就可以找到存放所需数据的被叶子节点包含的页！进而避免的全盘扫描从而提高了性能.

下面，通过一个例子来证明：

在SQL SERVER中，表上如果没有建立聚集索引，则是按照堆（HEAP）存放的，假设我有这样一张表:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-22-t-sql-sql-server/t-sql-sql-server-201112221217524697.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112221217514216.png)

现在这张表上没有任何索引，也就是以堆存放，我通过在其上加上聚集索引（以B树存放）来展现对IO的减少:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-22-t-sql-sql-server/t-sql-sql-server-201112221217569204.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112221217543466.png)

### **理解聚集和聚集索引**

* * *

在SQL SERVER中，最主要的两类索引是聚集索引和非聚集索引。可以看到，这两个分类是围绕聚集这个关键字进行的.那么首先要理解什么是聚集.

聚集在索引中的定义:

为了提高某个属性\(或属性组\)的查询速度，把这个或这些属性\(称为聚集码\)上具有相同值的元组集中存放在连续的物理块称为聚集。

简单来说，聚集索引就是:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-22-t-sql-sql-server/t-sql-sql-server-201112221217585291.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/20111222121757732.png)

在SQL SERVER中，聚集的作用就是将某一列（或是多列）的物理顺序改变为和逻辑顺序相一致,比如，我从adventureworks数据库的employee中抽取5条数据:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-22-t-sql-sql-server/t-sql-sql-server-201112221218115217.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112221218103689.png)

当我在ContactID上建立聚集索引时，再次查询:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-22-t-sql-sql-server/t-sql-sql-server-201112221218148578.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112221218121478.png)

在SQL SERVER中，聚集索引的存储是以B树存储，B树的叶子直接存储聚集索引的数据:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-22-t-sql-sql-server/t-sql-sql-server-201112221218166858.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112221218159234.gif)

因为聚集索引改变的是其所在表的物理存储顺序，所以每个表只能有一个聚集索引.

### **非聚集索引**

因为每个表只能有一个聚集索引，如果我们对一个表的查询不仅仅限于在聚集索引上的字段。我们又对聚集索引列之外还有索引的要求，那么就需要非聚集索引了.

非聚集索引，本质上来说也是聚集索引的一种.非聚集索引并不改变其所在表的物理结构，而是额外生成一个聚集索引的B树结构，但叶子节点是对于其所在表的引用,这个引用分为两种，如果其所在表上没有聚集索引，则引用行号。如果其所在表上已经有了聚集索引，则引用聚集索引的页.

一个简单的非聚集索引概念如下:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-22-t-sql-sql-server/t-sql-sql-server-201112221218193567.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112221218172006.png)

可以看到，非聚集索引需要额外的空间进行存储，按照被索引列进行聚集索引，并在B树的叶子节点包含指向非聚集索引所在表的指针.

MSDN中，对于非聚集索引描述图是:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-22-t-sql-sql-server/t-sql-sql-server-201112221218216306.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112221218205094.gif)

可以看到，非聚集索引也是一个B树结构，与聚集索引不同的是，B树的叶子节点存的是指向堆或聚集索引的指针.

通过非聚集索引的原理可以看出，如果其所在表的物理结构改变后，比如加上或是删除聚集索引，那么所有非聚集索引都需要被重建，这个对于性能的损耗是相当大的。所以最好要先建立聚集索引，再建立对应的非聚集索引.

### **聚集索引 VS 非聚集索引**

* * *

前面通过对于聚集索引和非聚集索引的原理解释.我们不难发现，大多数情况下，聚集索引的速度比非聚集索引要略快一些.因为聚集索引的B树叶子节点直接存储数据，而非聚集索引还需要额外通过叶子节点的指针找到数据.

还有，对于大量连续数据查找，非聚集索引十分乏力，因为非聚集索引需要在非聚集索引的B树中找到每一行的指针，再去其所在表上找数据，性能因此会大打折扣.有时甚至不如不加非聚集索引.

因此，大多数情况下聚集索引都要快于非聚集索引。但聚集索引只能有一个，因此选对聚集索引所施加的列对于查询性能提升至关紧要.

### **索引的使用**

* * *

索引的使用并不需要显式使用，建立索引后查询分析器会自动找出最短路径使用索引.

但是有这种情况.当随着数据量的增长，产生了索引碎片后，很多存储的数据进行了不适当的跨页，会造成碎片\(关于跨页和碎片以及填充因子的介绍，我会在后续文章中说到\)我们需要重新建立索引以加快性能:

比如前面的test\_tb2上建立的一个聚集索引和非聚集索引，可以通过DMV语句查询其索引的情况:
    
    
    [SELECT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SELECT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) index_type_desc,alloc_unit_type_desc,avg_fragmentation_in_percent,fragment_count,avg_fragment_size_in_pages,page_count,record_count,avg_page_space_used_in_percent
    [FROM](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=FROM&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) sys.dm_db_index_physical_stats(DB_ID('AdventureWorks'),OBJECT_ID('test_tb2'),[NULL](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=NULL&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99),[NULL](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=NULL&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99),'Sampled')

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-22-t-sql-sql-server/t-sql-sql-server-201112221218236570.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112221218221455.png)

我们可以通过重建索引来提高速度:
    
    
    [ALTER](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ALTER&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [INDEX](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=INDEX&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) idx_text_tb2_EmployeeID [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) test_tb2 REBUILD

还有一种情况是，当随着表数据量的增大，有时候需要更新表上的统计信息，让查询分析器根据这些信息选择路径，使用:
    
    
    [UPDATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=UPDATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [STATISTICS](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=STATISTICS&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 表名

那么什么时候知道需要更新这些统计信息呢，就是当执行计划中估计行数和实际表的行数有出入时:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-22-t-sql-sql-server/t-sql-sql-server-201112221218263803.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112221218257574.png)

### **使用索引的代价**

* * *

我最喜欢的一句话是”everything has price”。我们通过索引获得的任何性能提升并不是不需要付出代价。这个代价来自几方面.

1.通过聚集索引的原理我们知道，当表建立索引后，就以B树来存储数据.所以当对其进行更新插入删除时，就需要页在物理上的移动以调整B树.因此当更新插入删除数据时，会带来性能的下降。而对于聚集索引，当更新表后，非聚集索引也需要进行更新，相当于多更新了N（N=非聚集索引数量）个表。因此也下降了性能.

2.通过上面对非聚集索引原理的介绍，可以看到，非聚集索引需要额外的磁盘空间。

3.前文提过，不恰当的非聚集索引反而会降低性能.

所以使用索引需要根据实际情况进行权衡.通常我都会将非聚集索引全部放到另外一个独立硬盘上，这样可以分散IO，从而使查询并行.

### ****

### **总结**

* * *

本文从索引的原理和概念对SQL SERVER中索引进行介绍，索引是一个很强大的工具，也是一把双刃剑.对于恰当使用索引需要对索引的原理以及数据库存储的相关原理进行系统的学习.
