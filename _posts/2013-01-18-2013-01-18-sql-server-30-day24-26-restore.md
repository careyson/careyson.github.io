---
layout: post
title: "SQL Server误区30日谈-Day24-26个有关还原(Restore)的误区"
date: 2013-01-18
categories: blog
tags: [博客园迁移]
---

本系列文章是我在sqlskill.com的PAUL的博客看到的，很多误区都比较具有典型性和代表性，原文来自[T-SQL Tuesday \#11: Misconceptions about.... EVERYTHING\!\!](http://www.sqlskills.com/blogs/paul/post/T-SQL-Tuesday-11-Misconceptions-about-EVERYTHING!!.aspx),经过我们团队的翻译和整理发布在[AgileSharp](http://www.agilesharp.com/)上。希望对大家有所帮助。

本系列文章一直所没有触及的就是有关”还原\(Restore\)”的话题，因为一旦牵扯到这个话题就会涉及大量的误区，多到我无法通过一篇文章说完的地步。

事实上，我希望用字母表的顺序为每一个误区进行编号，希望你看了不要昏昏欲睡。下面开始揭穿这26个误区。

**Myth \#24:** **26个有关还原\(Restore\)的误区**

都是错误的

24 a\)可以通过WITH STOPAT参数在完整备份和差异备份的基础上还原到特定时间点

当然不能。虽然这个语法看上去貌似能的样子，但这个语法的最佳实践是你在进行日志还原到特定时间点时带上，这样你的还原就不会超过这个时间点（译者注：比如说还原的第一个日志备份中不包含这个时间点，但你带上这个参数则这个日志备份会被全部还原，直到你还原到包含时间点的日志备份而不用担心还原过头）,对此我之前的一篇文章会更有帮助:[Debunking a couple of myths around full database backups](http://www.sqlskills.com/BLOGS/PAUL/post/Debunking-a-couple-of-myths-around-full-database-backups.aspx)。

24 b\)使用了WITH CONTINUE\_AFTER\_ERROR选项之后还可以按照既定的还原顺序进行还原

错误。如果你的备份集有损坏而不得不使用这个选项，那么你的还原顺序将会不复存在。当进行日志还原时日志损坏，那么使用这个选项之前就需要三思而后行，因为这很有可能造成数据不一致的问题。在最坏的情况下会造成数据库中结构被破坏，我不推荐使用这个选项。

24 c\)可以将数据库的一部分还原到特定时间点

不能，数据库的每个部分都需要和主文件组时间点一致，否则就无法上线。当然只读文件组除外。

24 d\)可以将不同数据库的不同文件组还原到一个新的数据库中

不能，每个数据库的文件头页（译者注：也就是页号为0的页）都有一个GUID，除非这个GUID和另外数据库的GUID一致才能还原（这当然不可能）。

24 e\)还原可以去除索引碎片（或是更新统计信息等等）

不能，你备份的是什么还原的就是什么，我之前的一篇文章对此有更详细的解释:[blog post over on our SQL Server Magazine Q&A blog](http://www.sqlmag.com/blogs/SQLServerQuestionsAnswered/SQLServerQuestionsAnswered/tabid/1977/entryid/12612/Default.aspx)。

24 f\)在还原的过程中可以进行数据库收缩

不能，虽然大家都需要这个功能，在开发环境下恢复一个大部分是空的备份集时这就十分有用。但就是不能。

24 g\)可以将数据库还原到任何更低版本的实例

不能，这是一个普遍存在的误区。低版本的实例对于高版本的数据库的部分内容有可能无法理解（比如sql server 2005的数据库就无法理解SQL Server 2008数据库的一些内容）。

24 h\)可以将数据库还原到任意版本的SQL Server中

错误，比如说SQL Server 2005,一个含有表分区的数据库只能还原到企业版中。在SQL Server 2008只能还原到企业版的数据库包含了如下特性:分区，透明数据加密，CDC,数据压缩。有关这里我已经写过一篇文章，请看:[SQL Server 2008: Does my database contain Enterprise-only features?](http://www.sqlskills.com/BLOGS/PAUL/post/SQL-Server-2008-Does-my-database-contain-Enterprise-only-features.aspx)。

24 i\)WITH STANDBY参数会破坏还原链

不会，这个参数的作用是使得在还原的过程中，保证数据库事务级别的一致性。从还原顺序的角度来说，With Standby参数WITH NORECOVERY并无区别。你可以在还原的过程中停止N次。这也是事务日志传送的机制。经常有人会问在事务传送的辅助服务器进行日志恢复的过程是否能访问，至此你应该知道是可以只读访问的。同时，这个选项也可能造成一些诡异的问题，请看:[Why could restoring a log-shipping log backup be slow?](http://www.sqlskills.com/BLOGS/PAUL/post/Why-could-restoring-a-log-shipping-log-backup-be-slow.aspx)。

24 j\)如果备份数据库的服务器没有开启即时文件初始化选项，那么恢复的服务器就不能利用这个特性

是否能进行即时文件初始化完全取决于被还原的服务器受否开启这个特性。备份集中不会含有任何有关这点的信息。更详细的内容请看:[SQL Server误区30日谈-Day3-即时文件初始化特性可以在SQL Server中开启和关闭](http://www.cnblogs.com/CareySon/archive/2012/10/22/2733487.html)。

24 k\)还原是从损坏中恢复的最佳办法

不是,并不完全是。这要取决于你有的备份类型。如果损坏的数据比较多，那么利用还原是一个不错的主意，但如果损失的数据比较少并允许一些数据损失的情况下，亦或是由事务日志传送的辅助服务器回传一些日志的情况下，那么downtime就会少很多。最佳办法就是在可接受的数据损失范围内，在尽量少的downtime修复损坏。

24 l\)在开始还原之后还可以备份尾端日志

不允许，一旦你开始还原之后，就不再允许备份尾端日志。所以当灾难发生之后，第一件事永远都是查看是否需要备份尾端日志。

24 m\)你可以还原到在备份的日志范围之内的任何时间点

这是不对的。如果日志中包含了那些那些仅仅少量日志的操作\(比如批量数据导入操作\)，这类操作具有原子性，要么全部还原，要么不还原。这是由于这类操作对于区的进行了修改，但备份集中并没记录何时修改了这些区。你可以通过如下脚本查看日志备份包含的信息量：[New script: how much data will the next log backup include?](http://www.sqlskills.com/BLOGS/PAUL/post/New-script-how-much-data-will-the-next-log-backup-include.aspx)。

24 n\)只要备份成功，就可以利用这个备份集进行还原

No,no,no。备份集只是存储在IO子系统的文件，就和数据库的文件一样。它也有损坏的可能。你需要定期检查备份是否被损坏，否则当灾难发生后的惊喜怕你是承受不了。请看:[Importance of validating backups](http://www.sqlskills.com/BLOGS/PAUL/post/Importance-of-validating-backups.aspx)。另外一点需要注意的是避免额外的完整备份破坏恢复顺序，这个例子或许会给你一点警示：[BACKUP WITH COPY\_ONLY - how to avoid breaking the backup chain](http://www.sqlskills.com/BLOGS/PAUL/post/BACKUP-WITH-COPY_ONLY-how-to-avoid-breaking-the-backup-chain.aspx)。

24 o\)所有的SQL Server页类型都可以通过单页恢复进行还原

不，一些分配位图的页（译者注：比如GAM,SGMA,FPS页等）不能通过进行单页还原\(这类页可以通过SQL Server 2008 的镜像进行自动页修复\)。详情你可以看我这篇文章:[Search Engine Q&A \#22: Can all page types be single-page restored?](http://www.sqlskills.com/BLOGS/PAUL/post/Search-Engine-QA-22-Can-all-page-types-be-single-page-restored.aspx)。

24 p\)RESTORE ... WITH VERIFYONLY选项会验证整个备份集

不，这个选项仅仅检查备份的头是否正确。只有使用WITH CHECKSUM才可以完整备份集的校验和检查。

24 q\)可以在不还原证书的情况下，还原被透明数据加密的数据库

不能，对于透明数据加密最重要的一点要记住，证书丢了意味着整个数据库就没了。

24 r\)当还原过程完成后，还原会进行Redo和Undo

每次还原操作后其实执行的都是Redo操作，只有在整个还原过程完成后，才会进行Undo。

24 s\)压缩备份集只能被还原到SQL Server 2008企业版中

不，所有的版本都能还原压缩后的备份。从SQL Server 2008 R2开始，标准版也可以进行压缩备份。

24 t\)将低版本的数据库还原到高版本的实例可以跳过升级过程

不允许，在数据还原和附加的过程中是不允许跳过必须的升级和恢复过程。

24 u\)在32位实例下备份的数据库无法恢复到64位实例。反之亦然

错误，数据库的内部格式和CPU构架无关。

24 v\)只要进行数据还原，就可以保证程序正常执行

不对，就像高可用性中的镜像故障转移和事务日志传送转移到辅助服务器一样，还有很多额外的步骤需要做才能保证程序正常执行。包括辅助数据库和正确的登录名等。

24 w\)还原受损的文件需要从多个文件组进行还原，则必须还原相关的所有文件组

不，在SQL Server 2000中的确是这样，但在SQL Server 2005以后的版本就完全不用了。

24 x\)你可以将数据库还原到任何最新版本的实例

不对，数据库只能还原到比其新的一个或两个版本.\(比如SQL Server 7.0下的数据库就不能还原到SQL Server 2008\)。

24 y\)恢复时间和还原时间是一样的

不，很多因素会影响还原的时间，比如说是否有长事务需要回滚，或是即时文件初始化特性是否开启。

24 z\)在还原数据库之前需要先Drop被还原的数据库

不是的，如果你在还原数据库之前Drop被还原的数据库，那么还原过程首先需要即时文件初始化，还有，你最好保留被还原数据库的副本以便还原失败的情况下把损失减到最小。
