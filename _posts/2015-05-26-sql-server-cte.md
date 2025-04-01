---
layout: post
title: "SQL Server中CTE的另一种递归方式-从底层向上递归"
date: 2015-05-26
categories: blog
tags: [博客园迁移]
---

SQL Server中的公共表表达式（Common Table Expression，CTE）提供了一种便利的方式使得我们进行递归查询。所谓递归查询方便对某个表进行不断的递归从而更加容易的获得带有层级结构的数据。典型的例子如MSDN（<https://technet.microsoft.com/en-us/library/ms186243(v=sql.105).aspx>）中提到的获取员工关系层级的结构，如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-05-26-sql-server-cte/sql-server-cte-261717022595449.png)](http://images0.cnblogs.com/blog/35368/201505/261717013846548.png)

图1.获取员工层级结构

图1所示的例子是一个简单的通过递归获取员工层级的例子，主要理念是通过一个自连接的表（员工表，连接列为员工ID与其上司ID，没有上司的人为公司最大的CEO），不断递归，从而在每次递归时将员工层级+1，最终递归完成后最低级别的员工可以排出其在公司的层级，也就是如图1中所示的3。

图1的例子应用场景比较广泛，网上也有很多文章提到过这种方式，但当我们需要另一种递归方式时，上面的例子就无能为力了。假设我们有这样一个需求，比如现在流程的微商传销的提成方式，假设员工分为3级，分别为一级代理、二级代理、最终销售。那么算业绩的时候可能是重复提成，比如一级代理提二级代理销售额的3%，一级代理提最终销售的1%。二级代理提最终销售的2%等等。那么我们需要从数据库中提取出所有代理的所有利润就不是一件容易的事。一个简单的示意图如图2所示：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-05-26-sql-server-cte/sql-server-cte-261717038219492.png)](http://images0.cnblogs.com/blog/35368/201505/261717030552092.png)

图2.多层提成的模型

而此时每一级代理自身又可以直接进行销售，所以代理的销售额并不简单等于其下级代理销售额的和，因此我们最简单的办法就是列出每个代理所有下属的代理，并将其销售额按照业务规则相乘即可。

因此我们需要一个查询将每个代理以及其下属层级全部列出来。由于实际需求可能都是按照省份划分代理，比如广州省是一级，广州市是二级，下属天河区是三级。下面是我们测试数据用的表：
    
    
    create table #tb(id varchar(3) , pid varchar(3) , name varchar(10))
    
    
    insert into #tb values('1' , null  , '广东省')
    
    
    insert into #tb values('2' , '1' , '广州市')
    
    
    insert into #tb values('3' , '1' , '深圳市')
    
    
    insert into #tb values('4' , '2' , '天河区')
    
    
    insert into #tb values('5' , '3' , '罗湖区')
    
    
    insert into #tb values('6' , '3' , '福田区')
    
    
    insert into #tb values('7' , '3' , '宝安区')
    
    
    insert into #tb values('8' , '7' , '西乡镇')
    
    
    insert into #tb values('9' , '7' , '龙华镇')

代码清单1.测试数据

而我们希望获得的数据类似：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2015-05-26-sql-server-cte/sql-server-cte-261717053521994.png)](http://images0.cnblogs.com/blog/35368/201505/261717045555350.png)

图3.希望获得的数据

在此，我们采用的策略不是与MSDN中的例子不同，而是自下而上递归。代码如代码清单2所示：
    
    
    WITH    cte ( id, pid, NAME )
    
    
              AS ( SELECT   id ,
    
    
                            pid ,
    
    
                            name 
    
    
                   FROM     #tb a
    
    
                   WHERE    a.pid IS NOT NULL
    
    
                   UNION ALL
    
    
                   SELECT   b.id ,
    
    
                            a.pid ,
    
    
                            b.NAME
    
    
                        
    
    
                   FROM     #tb a
    
    
                            INNER JOIN cte b ON a.id = b.pid
    
    
                WHERE a.pid IS NOT NULL
    
    
                            
    
    
                 )
    
    
        SELECT  pid AS id,id AS SID,NAME
    
    
        FROM    cte a 
    
    
        UNION 
    
    
        SELECT id,id,name FROM #tb
    
    
        ORDER BY id,sid

代码清单2.从下而上的递归

代码清单2展示了方案，与MSDN自顶向下的例子不同，我们这里采用了自下而上的递归，递归的终止条件是WHERE a.pid IS NOT NULL，而不是a.pid IS NULL，该条件使得先从底层开始递归，然后通过a.id = b.pid而不是a.pid=b.id使得查找的过程变为由子节点找父节点，从而实现了上述需求。
