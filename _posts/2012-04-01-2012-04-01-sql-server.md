---
layout: post
title: "细说SQL Server中的加密"
date: 2012-04-01
categories: blog
tags: [博客园迁移]
---

### 简介

加密是指通过使用密钥或密码对数据进行模糊处理的过程。在SQL Server中，加密并不能替代其他的安全设置，比如防止未被授权的人访问数据库或是数据库实例所在的Windows系统，甚至是数据库所在的机房，而是作为当数据库被破解或是备份被窃取后的最后一道防线。通过加密，使得未被授权的人在没有密钥或密码的情况下所窃取的数据变得毫无意义。这种做法不仅仅是为了你的数据安全，有时甚至是法律所要求的（像国内某知名IT网站泄漏密码这种事在中国可以道歉后不负任何责任了事，在米国妥妥的要破产清算）。

### SQL Server中的加密简介

在SQL Server2000和以前的版本，是不支持加密的。所有的加密操作都需要在程序中完成。这导致一个问题，数据库中加密的数据仅仅是对某一特定程序有意义，而另外的程序如果没有对应的解密算法，则数据变得毫无意义。

到了SQL Server2005，引入了列级加密。使得加密可以对特定列执行，这个过程涉及4对加密和解密的内置函数

SQL Server 2008时代，则引入的了透明数据加密（TDE），所谓的透明数据加密，就是加密在数据库中进行，但从程序的角度来看就好像没有加密一样，和列级加密不同的是，TDE加密的级别是整个数据库。使用TDE加密的数据库文件或备份在另一个没有证书的实例上是不能附加或恢复的。

### 加密的一些基础知识

加密是指通过使用密钥或密码对数据进行模糊处理的过程。加密解密最简单的过程如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-01-sql-server/sql-server-201204011448541271.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204011448453832.png)

图1.一个简单的加密解密过程

通常来说，加密可以分为两大类，对称\(Symmetric\)加密和非对称\(Asymmetric\)加密。

对称加密是那些加密和解密使用同一个密钥的加密算法，在图1中就是加密密钥=解密密钥。对称加密通常来说会比较羸弱，因为使用数据时不仅仅需要传输数据本身，还是要通过某种方式传输密钥，这很有可能使得密钥在传输的过程中被窃取。

非对称加密是那些加密和解密使用不同密钥的加密算法，在图1中就是加密密钥！=解密密钥。用于加密的密钥称之为公钥，用于解密的密钥称之为私钥。因此安全性相比对称加密来说会大大提高。当然有一长必有一短，非对称加密的方式通常算法会相比对称密钥来说复杂许多，因此会带来性能上的损失。

因此，一种折中的办法是使用对称密钥来加密数据，而使用非对称密钥来加密对称密钥。这样既可以利用对称密钥的高性能，还可以利用非对称密钥的可靠性。

### 加密算法的选择

现在流行的很多加密算法都是工业级的，比如对称加密的算法有:DES、3DES、IDEA、FEAL、BLOWFISH.而非对称加密的算法比如经典的RSA。因为这些算法已经公布了比较长的时间，并且经受了很多人的考验，所以通常来说都是比较安全的。

SQL Server提供了比如:DES、Triple DES、TRIPLE\_DES\_3KEY、RC2、RC4、128 位 RC4、DESX、128 位 AES、192 位 AES 和 256 位 AES这些加密算法，没有某种算法能适应所有要求，每种算法都有长处和短处，关于每种加密算法的细节，请Bing…

但选择算法有一些共通之处:

  * 强加密通常会比较弱的加密占用更多的 CPU 资源。

  * 长密钥通常会比短密钥生成更强的加密。

  * 非对称加密比使用相同密钥长度的对称加密更强，但速度相对较慢。

  * 使用长密钥的块密码比流密码更强。

  * 复杂的长密码比短密码更强。

  * 如果您正在加密大量数据，应使用对称密钥来加密数据，并使用非对称密钥来加密该对称密钥。

  * 不能压缩已加密的数据，但可以加密已压缩的数据。如果使用压缩，应在加密前压缩数据。




### SQL Server中的加密层次结构

在SQL Server中，加密是分层级的.根层级的加密保护其子层级的加密。概念如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-01-sql-server/sql-server-20120401144912436.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204011449001723.gif)

图2.SQL Server加密的层级

由图2可以看出，加密是分层级的。每一个数据库实例都拥有一个服务主密钥\(Service Master Key\),对应图2中的橙色部分。这个密钥是整个实例的根密钥，在实例安装的时候自动生成,其本身由Windows提供的数据保护API进行保护\(Data Pertection API\)，服务主密钥除了为其子节点提供加密服务之外，还用于加密一些实例级别的信息，比如实例的登录名密码或者链接服务器的信息。

在服务主密钥之下的是数据库主密钥（Database Master Key），也就是图2中土黄色的部分，这个密钥由服务主密钥进行加密。这是一个数据库级别的密钥。可以用于为创建数据库级别的证书或非对称密钥提供加密。每一个数据库只能有一个数据库主密钥，通过T-SQL语句创建，如代码1所示。
    
    
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) MASTER [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ENCRYPTION [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) PASSWORD ='Pa$$word'

  


代码1.创建数据库主密钥

数据库主密钥由代码1所示的密码和服务主密钥共同保护。当数据库主密钥创建成功后，我们就可以使用这个密钥创建对称密钥，非对称密钥和证书了。如代码2所示。
    
    
    --创建证书
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) CERTIFICATE CertTest 
    [with](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=with&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SUBJECT = 'Test Certificate'
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    --创建非对称密钥
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ASYMMETRIC [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) TestAsymmetric
        [WITH](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=WITH&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ALGORITHM = RSA_2048 
        ENCRYPTION [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) PASSWORD = 'pa$$word'; 
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    --创建对称密钥
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SYMMETRIC [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) TestSymmetric
        [WITH](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=WITH&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ALGORITHM = AES_256
        ENCRYPTION [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) PASSWORD = 'pa$$word';
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)

  


代码2.创建证书，非对称密钥和对称密钥

在代码2中我们看出，并没有显式指定使用数据库主密钥加密证书，对称密钥和非对称密钥。这是因为每个数据库只能有一个数据库主密钥，所以无需指定。创建成功后我们可以在SSMS中查看到刚刚创建的证书，非对称密钥和对称密钥,如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-01-sql-server/sql-server-201204011449183712.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204011449146334.png)

图3.查看刚刚创建成功的证书，非对称密钥和对称密钥

由这个加密层级不难推断，如果数据库主密钥被破解，则由其所创建的证书，对称密钥，非对称密钥都有可能被破解。

由图2的层级我们还可以看出，对称密钥不仅仅可以通过密码创建，还可以通过其它对称密钥，非对称密钥和证书创建。如代码3所示。
    
    
    --由证书加密对称密钥
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SYMMETRIC [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SymmetricByCert
        [WITH](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=WITH&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ALGORITHM = AES_256
        ENCRYPTION [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) CERTIFICATE CertTest;
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    --由对称密钥加密对称密钥
    [OPEN](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=OPEN&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SYMMETRIC [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) TestSymmetric
        DECRYPTION [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) PASSWORD='pa$$word'
    
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SYMMETRIC [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SymmetricBySy
        [WITH](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=WITH&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ALGORITHM = AES_256
        ENCRYPTION [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SYMMETRIC [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) TestSymmetric;
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    --由非对称密钥加密对称密钥
    
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SYMMETRIC [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SymmetricByAsy
        [WITH](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=WITH&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ALGORITHM = AES_256
        ENCRYPTION [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ASYMMETRIC [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) TestASymmetric;
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)

  


代码3.由几种不同的加密方式创建对称密钥

### SQL Server中的数据列加密\(Column-level Encryption\)

SQL Server在2005引入了列加密的功能。使得可以利用证书，对称密钥和非对称密钥对特定的列进行加密。在具体的实现上，根据加密解密的方式不同，内置了4对函数用于加密解密:

  * EncryptByCert\(\) 和DecryptByCert\(\)—利用证书对数据进行加密和解密
  * EncryptByAsymKey\(\) and DecryptByAsymKey\(\)—利用非对称密钥对数据进行加密和解密   
EncryptByKey\(\) and DecryptByKey\(\)—利用对称密钥对数据进行加密和解密
  * EncryptByPassphrase\(\) and DecryptByPassphrase\(\)—利用密码字段产生对称密钥对数据进行加密和解密



因此，加密数据列使用起来相对比较繁琐，需要程序在代码中显式的调用SQL Server内置的加密和解密函数，这需要额外的工作量，并且，加密或解密的列首先需要转换成Varbinary类型。

下面我们来看一个例子:

在AdventureWorks示例数据库中，我们找到Sales.CreditCard表，发现信用卡号是明文显示的（怎么AdventureWorks也像泄漏密码的某IT网站这么没节操）。因此希望对这一列进行加密。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-01-sql-server/sql-server-201204011449254589.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204011449224919.png)

图5.和国内某知名IT网站一样没节操的明文保存重要信息

首先我们需要将CardNumber列转为Varbinary类型。这里通过Select Into新建个表，如代码4所示。
    
    
    [SELECT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SELECT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) CreditCardID, 
    CardType,
    CardNumber_encrypt = [CONVERT](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CONVERT&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)([varbinary](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=varbinary&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)(500), CardNumber), 
    ExpMonth, 
    ExpYear, 
    ModifiedDate
    [INTO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=INTO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) Sales.CreditCard_Encrypt 
    [FROM](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=FROM&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) Sales.CreditCard 
    [WHERE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=WHERE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 1<>1

  


代码4.通过Select Into创建新表

此时我们利用之前创建的由证书加密的对称密钥来进行列加密，如代码5所示。
    
    
    --打开之前创建的由证书加密的对称密钥
    [OPEN](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=OPEN&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SYMMETRIC [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SymmetricByCert
    DECRYPTION [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) CERTIFICATE CertTest
    --利用这个密钥加密数据并插入新建的表
    [insert](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=insert&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) Sales.CreditCard_encrypt (
    CardType,
    CardNumber_encrypt, 
    ExpMonth, 
    ExpYear, 
    ModifiedDate
    ) 
    [select](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=select&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [top](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=top&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 10
    CardType,
    CardNumber_encrypt = EncryptByKey(KEY_GUID('SymmetricByCert'), CardNumber),
    ExpMonth,
    ExpYear, 
    ModifiedDate
    [from](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=from&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) Sales.CreditCard

  


代码5.利用证书加密过的对称密钥加密数据

此时加密列无法直接进行查看,如图6所示:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-01-sql-server/sql-server-201204011449295065.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204011449277738.png)

图6.无法直接查看加密的列

此时可以通过对应的解密函数查看数据，如代码6所示。
    
    
    [OPEN](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=OPEN&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SYMMETRIC [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SymmetricByCert
    DECRYPTION [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) CERTIFICATE CertTest
    
    [select](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=select&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) CardType,
    CardNumber = [convert](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=convert&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)([nvarchar](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=nvarchar&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)(25), DecryptByKey(CardNumber_encrypt)), 
    ExpMonth, 
    ExpYear, 
    ModifiedDate
    [from](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=from&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) Sales.CreditCard_encrypt

  


图6.由对应的解密函数查看加密的数据

所得到的结果如图7所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-01-sql-server/sql-server-2012040114502736.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204011449319011.png)

图7.解密后结果可以正确显示

利用非对称密钥和证书进行加密解密只是函数不同，这里就不测试了。

### 透明数据加密\(Transparent Data Encryption\)

在SQL Server 2008中引入了透明数据加密\(以下简称TDE\)，之所以叫透明数据加密，是因为这种加密在使用数据库的程序或用户看来，就好像没有加密一样。TDE加密是数据库级别的。数据的加密和解密是以页为单位，由数据引擎执行的。在写入时进行加密，在读出时进行解密。客户端程序完全不用做任何操作。

TDE的主要作用是防止数据库备份或数据文件被偷了以后，偷数据库备份或文件的人在没有数据加密密钥的情况下是无法恢复或附加数据库的。

TDE使用数据加密密钥（DEK）进行加密。DEK是存在Master数据库中由服务主密钥保护，由的保护层级如图8所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-01-sql-server/sql-server-201204011450369078.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204011450319573.gif)

图8.TDE的加密层次

开启TDE的数据库的日志和备份都会被自动加密。

因为TDE使得数据库在写入时加密，在读出时解密，因此需要额外的CPU资源，根据微软的说法，需要额外3%-5%的CPU资源。

下面我们来看如何开启TDE

开启TDE非常简单，只需创建数据加密密钥（DEK）后，将加密选项开启就行，如代码7所示。
    
    
    --基于我们之前创建的证书CertTest,创建DEK
    --CertTest需要在Master数据库中
    [USE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=USE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) AdventureWorks
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 
    [CREATE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=CREATE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [DATABASE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DATABASE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ENCRYPTION [KEY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=KEY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) 
    [WITH](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=WITH&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ALGORITHM = AES_256 
    ENCRYPTION [BY](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=BY&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) SERVER CERTIFICATE CertTest
    [GO](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=GO&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)
    --开启TDE
    [ALTER](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ALTER&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) [DATABASE](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=DATABASE&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) AdventureWorks
    [SET](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=SET&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99) ENCRYPTION [ON](http://search.microsoft.com/default.asp?so=RECCNT&siteid=us%2Fdev&p=1&nq=NEW&qu=ON&IntlSearch=&boolean=PHRASE&ig=01&i=09&i=99)

  


代码7.创建DEK后，开启TDE

这里值得注意的是，DEK是存在所开启TDE的数据库中的。当然，这个操作我们也可以通过在SSMS中右键点击需要开始TDE的数据库，选择任务--管理数据库加密来进行。如图9所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-01-sql-server/sql-server-201204011450515508.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204011450433019.png)

图9.在SSMS中开启TDE

开启TDE后，我们可以通过图10的语句查看TDE的状态。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2012-04-01-sql-server/sql-server-201204011450549879.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201204/201204011450535343.png)

图10.查看数据库加密状态

### 总结 

本文介绍了加密的基本概念，SQL Server中加密的层级，以及SQL Server中提供的两种不同的加密方式。SQL Server的TDE是一个非常强大的功能，在用户程序中不做任何改变就能达到数据库层面的安全。在使用SQL Server提供的加密技术之前，一定要先对加密的各个功能概念有一个系统的了解，否则很有可能造成的后果是打不开数据库。准备在后续文章中再写关于证书，密钥的备份和恢复….
