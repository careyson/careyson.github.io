---
layout: post
title: "T-SQL查询进阶--理解SQL SERVER中的分区表"
date: 2011-12-30
categories: blog
tags: [博客园迁移]
---

### **简介**

* * *

分区表是在SQL SERVER2005之后的版本引入的特性。这个特性允许把逻辑上的一个表在物理上分为很多部分。而对于SQL SERVER2005之前版本，所谓的分区表仅仅是[分布式视图](http://www.cnblogs.com/CareySon/archive/2011/12/07/2279522.html),也就是多个表做union操作.

分区表在逻辑上是一个表，而物理上是多个表.这意味着从用户的角度来看，分区表和普通表是一样的。这个概念可以简单如下图所示：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301625171168.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301625141984.png)

而对于SQL SERVER2005之前的版本，是没有分区这个概念的，所谓的分区仅仅是分布式视图:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301626566162.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301626508500.png)

本篇文章所讲述的分区表指的是SQL SERVER2005之后引入的分区表特性.

### **为什么要对表进行分区**

* * *

在回答标题的问题之前，需要说明的是，表分区这个特性只有在企业版或者开发版中才有,还有理解表分区的概念还需要理解SQL SERVER中[文件和文件组](http://www.cnblogs.com/CareySon/archive/2011/12/26/2301597.html)的概念.

对表进行分区在多种场景下都需要被用到.通常来说，使用表分区最主要是用于:

  * 存档，比如将销售记录中1年前的数据分到一个专门存档的服务器中 
  * 便于管理，比如把一个大表分成若干个小表，则备份和恢复的时候不再需要备份整个表，可以单独备份分区 
  * 提高可用性，当一个分区跪了以后，只有一个分区不可用，其它分区不受影响 
  * 提高性能，这个往往是大多数人分区的目的，把一个表分布到不同的硬盘或其他存储介质中，会大大提升查询的速度. 



### **分区表的步骤**

* * *

分区表的定义大体上分为三个步骤：

  1. 定义分区函数 
  2. 定义分区构架 
  3. 定义分区表 



分区函数，分区构架和分区表的关系如下：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301627051546.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301626593918.png)

分区表依赖分区构架，而分区构架又依赖分区函数.值得注意的是，分区函数并不属于具体的分区构架和分区表，他们之间的关系仅仅是使用关系.

下面我们通过一个例子来看如何定义一个分区表:

假设我们需要定义的分区表结构如下:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301629137352.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301627061122.png)

第一列为自增列，orderid为订单id列，SalesDate为订单日期列，也就是我们需要分区的依据.

下面我们按照上面所说的三个步骤来实现分区表.

### **定义分区函数**

* * *

分区函数是用于判定数据行该属于哪个分区,通过分区函数中设置边界值来使得根据行中特定列的值来确定其分区，上面例子中，我们可以通过SalesDate的值来判定其不同的分区.假设我们想定义两个边界值\(boundaryValue\)进行分区,则会生成三个分区,这里我设置边界值分别为2004-01-01和2007-01-01，则前面例子中的表会根据这两个边界值分成三个区:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301630598579.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301630033682.png)

在MSDN中，定义分区函数的原型如下:
    
    
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) PARTITION [FUNCTION](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=FUNCTION&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) partition_function_name ( input_parameter_type )
    [AS](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=AS&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) RANGE [ [LEFT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=LEFT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) | [RIGHT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=RIGHT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ] 
    [FOR](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=FOR&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [VALUES](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=VALUES&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ( [ boundary_value [ ,...n ] ] ) 
    [ ; ]

通过定义分区函数的原型，我们看出其中并没有具体涉及具体的表.因为分区函数并不和具体的表相绑定.上面原型中还可以看到Range left和right.这个参数是决定临界值本身应该归于“left”还是“right”：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301632452106.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301631174954.png)

下面我们根据上面的参数定义分区函数:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301633545815.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301633251316.png)

通过系统视图，可以看见这个分区函数已经创建成功

### **定义分区构架**

* * *

定义完分区函数仅仅是知道了如何将列的值区分到了不同的分区。而每个分区的存储方式，则需要分区构架来定义.使用分区构架需要你对[文件和文件组](http://www.cnblogs.com/CareySon/archive/2011/12/26/2301597.html)有点了解.

我们先来看MSDN的分区构架的原型:
    
    
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) PARTITION SCHEME partition_scheme_name
    [AS](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=AS&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) PARTITION partition_function_name
    [ [ALL](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ALL&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ] [TO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=TO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ( { file_group_name | [ [PRIMARY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=PRIMARY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ] } [ ,...n ] )
    [ ; ]

从原型来看，分区构架仅仅是依赖分区函数.分区构架中负责分配每个区属于哪个文件组，而分区函数是决定如何在逻辑上分区:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301634197834.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301634033675.png)

基于之前创建的分区函数,创建分区构架:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301640338372.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301634242266.png)

### **定义分区表**

* * *

接下来就该创建分区表了.表在创建的时候就已经决定是否是分区表了。虽然在很多情况下都是你在发现已经表已经足够大的时候才想到要把表分区，但是分区表只能够在创建的时候指定为分区表。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301650023276.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301649449998.png)

为刚建立的分区表PartitionedTable加入5万条测试数据，其中SalesDate随机生成，从2001年到2010年随机分布.加入数据后，我们通过如下语句来看结果:
    
    
    [select](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=select&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [convert](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=convert&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)([varchar](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=varchar&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)(50), ps.name) [as](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=as&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) partition_scheme,
    p.partition_number, 
    [convert](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=convert&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)([varchar](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=varchar&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)(10), ds2.name) [as](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=as&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) filegroup, 
    [convert](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=convert&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)([varchar](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=varchar&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)(19), isnull(v.[value](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=value&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99), ''), 120) [as](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=as&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) range_boundary, 
    str(p.[rows](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=rows&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99), 9) [as](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=as&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [rows](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=rows&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    [from](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=from&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) sys.indexes i 
    [join](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=join&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) sys.partition_schemes ps [on](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=on&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) i.data_space_id = ps.data_space_id 
    [join](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=join&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) sys.destination_data_spaces dds
    [on](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=on&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ps.data_space_id = dds.partition_scheme_id 
    [join](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=join&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) sys.data_spaces ds2 [on](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=on&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) dds.data_space_id = ds2.data_space_id 
    [join](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=join&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) sys.partitions p [on](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=on&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) dds.destination_id = p.partition_number
    [and](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=and&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) p.object_id = i.object_id [and](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=and&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) p.index_id = i.index_id 
    [join](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=join&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) sys.partition_functions pf [on](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=on&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ps.function_id = pf.function_id 
    [LEFT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=LEFT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [JOIN](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=JOIN&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) sys.Partition_Range_values v [on](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=on&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) pf.function_id = v.function_id
    [and](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=and&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) v.boundary_id = p.partition_number - pf.boundary_value_on_right 
    [WHERE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=WHERE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) i.object_id = object_id('PartitionedTable')
    [and](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=and&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) i.index_id [in](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=in&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) (0, 1) 
    [order](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=order&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [by](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=by&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) p.partition_number

可以看到我们分区的数据分布:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301657263685.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301650393650.png)

### **分区表的分割**

* * *

分区表的分割。相当于新建一个分区，将原有的分区需要分割的内容插入新的分区，然后删除老的分区的内容,概念如下图:

假设我新加入一个分割点：2009-01-01，则概念如下:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301703256018.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301703203014.png)

通过上图我们可以看出，如果分割时，被分割的分区3内有内容需要分割到分区4，则这些数据需要被复制到分区4，并删除分区3上对应数据。

这种操作非常非常消耗IO，并且在分割的过程中锁定分区三内的内容，造成分区三的内容不可用。不仅仅如此，这个操作生成的日志内容会是被转移数据的4倍！

所以我们如果不想因为这种操作给客户带来麻烦而被老板爆菊的话…最好还是把分割点建立在未来（也就是预先建立分割点\)，比如2012-01-01。则分区3内的内容不受任何影响。在以后2012的数据加入时，自动插入到分区4.

分割现有的分区需要两个步骤:

1.首先告诉SQL SERVER新建立的分区放到哪个文件组

2.建立新的分割点

可以通过如下语句来完成:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301711163859.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301710308383.png)

如果我们的分割构架在定义的时候已经指定了NEXT USED，则直接添加分割点即可。

通过文中前面查看分区的长语句..再来看:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301712337281.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301711183435.png)

新的分区已经加入！

### **分区的合并**

* * *

分区的合并可以看作分区分割的逆操作。分区的合并需要提供分割点，这个分割点必须在现有的分割表中已经存在，否则进行合并就会报错

假设我们需要根据2009-01-01来合并分区,概念如下:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301714062104.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301712358069.png)

只需要使用merge参数：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-201112301714187296.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301714146310.png)

再来看分区信息:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-2011123017183486.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301714237268.png)

这里值得注意的是，假设分区3和分区4不再一个文件组，则合并后应该存在哪个文件组呢？换句话说，是由分区3合并到分区4还是由分区4合并到分区3？这个需要看我们的分区函数定义的是left还是right.如果定义的是left.则由左边的分区3合并到右边的分区4.反之，则由分区4合并到分区3:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-12-30-t-sql-sql-server/t-sql-sql-server-20111230171851789.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201112/201112301718477328.png)

### **总结**

* * *

本文从讲解了SQL SERVER中分区表的使用方式。分区表是一个非常强大的功能。使用分区表相对传统的分区视图来说，对于减少DBA的管理工作来说，会更胜一筹！
