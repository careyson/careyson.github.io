---
layout: post
title: "SQL Server中的Merge关键字"
date: 2012-03-07
categories: blog
tags: [博客园迁移]
---

### 简介

Merge关键字是一个神奇的DML关键字。它在SQL Server 2008被引入，它能将Insert,Update,Delete简单的并为一句。MSDN对于Merge的解释非常的短小精悍:”根据与源表联接的结果，对目标表执行插入、更新或删除操作。例如，根据在另一个表中找到的差异在一个表中插入、更新或删除行，可以对两个表进行同步。”,通过这个描述，我们可以看出Merge是关于对于两个表之间的数据进行操作的。

可以想象出，需要使用Merge的场景比如:

  * 数据同步 
  * 数据转换 
  * 基于源表对目标表做Insert,Update,Delete操作 



### 使用Merge关键字的好处

首先是更加短小精悍的语句，在SQL Server 2008之前没有Merge的时代，基于源表对目标表进行操作需要分别写好几条Insert,Update,Delete。而使用Merge,仅仅需要使用一条语句就好。下面我们来看一个例子。

首先建立源表和目标表，并插入相关的数据,如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-07-sql-server-merge/sql-server-merge-20120307155940719.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203071559273252.png)

图1.创建测试表并插入测试数据

下面我们来写一个简单的Merge语句,如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-07-sql-server-merge/sql-server-merge-201203071600053094.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203071600034438.png)

图2.一个简单的Merge语句

所造成的结果如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-07-sql-server-merge/sql-server-merge-201203071600211094.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203071600191259.png)

图3.Merge语句对于目标表的更新

最终目标表的结果如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-07-sql-server-merge/sql-server-merge-201203071601088583.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203071600226851.png)

图4.最后目标表的结果

Merge语句还有一个强大的功能是通过OUTPUT子句，可以将刚刚做过变动的数据进行输出。我们在上面的Merge语句后加入OUTPUT子句,如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-07-sql-server-merge/sql-server-merge-201203071601403787.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203071601252307.png)

图5.Merge语句后加上OUTPUT子句

此时Merge操作完成后，将所变动的语句进行输出,如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-07-sql-server-merge/sql-server-merge-201203071601456913.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203071601421637.png)

图6.输出Merge操作产生的数据变更

当然了，上面的Merge关键字后面使用了多个WHEN…THEN语句，而这个语句是可选的.也可以仅仅新增或是仅仅删除,如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-07-sql-server-merge/sql-server-merge-201203071601488534.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203071601468143.png)

图7.仅仅插入的Merge语句

我们还可以使用TOP关键字限制目标表被操作的行，如图8所示。在图2的语句基础上加上了TOP关键字，我们看到只有两行被更新。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-07-sql-server-merge/sql-server-merge-201203071602199169.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203071602037789.png)

图8.使用TOP关键字的Merge语句

但仅仅是MATCHED这种限制条件往往不能满足实际需求，我们可以在图7那个语句的基础上加上AND附加上额外的限制条件，如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-03-07-sql-server-merge/sql-server-merge-201203071602271932.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201203/201203071602226364.png)

图9.加上了AND限制条件的Merge语句

### Merge关键字的一些限制

  * 使用Merge关键字只能更新一个表
  * 源表中不能有重复的记录



### 小结

本文简单说明了Merge关键的字的使用。如果你使用的是SQL Server 2008之后的版本，在面对一些比如库存结账之类的业务时，放弃IF…ELSE和手写UPDATE，Insert吧，使用Merge关键字可以使这类操作更加轻松愉悦。
