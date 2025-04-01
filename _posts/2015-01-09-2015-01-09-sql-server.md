---
layout: post
title: "在SQL Server中添加供应用程序使用的帐号"
date: 2015-01-09
categories: blog
tags: [博客园迁移]
---

在之前客户咨询案例中，很多客户应用程序连接SQL Server直接用的就是SA帐号。如果对数据库管理稍微严格一点的话，就不应该给应用程序这种权限，通常应用程序只需要进行增删改查，而很少有DDL操作，因此配置帐号时应该遵循“最小权限分配”的原则仅仅赋予所需的权限。

对于应用程序来说，最小的权限通常就是就是给予读权限，写权限和执行存储过程权限。由于为了防止SQL注入导致的数据库信息泄漏，则还需要考虑拒绝帐号的查看定义权限，但值得注意的是，如果拒绝了查看定义的权限，则Bulk Insert会失败。完整的权限定义如下：
    
    
    ALTER ROLE [db_datareader] ADD MEMBER 用户名
    ALTER ROLE [db_datawriter] ADD MEMBER 用户名
    grant execute to 用户名
    deny view definition to 用户名

在SQL Server中，实例级别的是登录名，而数据库级别的才是用户名，登录名在创建完成后可映射到具体的库。因此我写了一个完整的脚本，同时创建登录名，用户，以及赋予对应的权限，脚本如下：
    
    
    --创建用户的存储过程， 
    
    --示例EXEC sp_CreateUser 'UserName','rw','DatabaseName' 
    --EXEC sp_CreateUser 'tesefx','r','Test','0xE39CA97EBE03BB4CA5FF78E50374EEBB' 
    
    CREATE PROC sp_CreateUser 
    @loginName VARCHAR(50) , 
    @IsWrite VarCHAR(3) , 
    @DatabaseName VARCHAR(50), 
    @Sid VARCHAR(100) ='1' 
    AS 
    PRINT('示例：EXEC sp_CreateUser ''UserName'',''rw'',''DatabaseName''') 
    PRINT('示例：EXEC sp_CreateUser ''UserName'',''rwv'',''DatabaseName'',''0xE39CA97EBE03BB4CA5FF78E50374EEBB''') 
    PRINT('r为只读权限，rw为读写权限，rwv为读写加View Definition权限') 
    
    
    IF EXISTS ( SELECT name 
    FROM sys.syslogins 
    WHERE name = @loginName ) 
    BEGIN 
    PRINT N'登录名已存在，跳过创建登录名步骤' 
    END 
    ELSE 
    BEGIN 
    
    DECLARE @CreateLogin NVARCHAR(1000) 
    DECLARE @pwd VARCHAR(50) 
    PRINT @Sid 
    SET @pwd=NEWID() 
    IF(@sid='1') 
    BEGIN 
    SET @CreateLogin = 'CREATE LOGIN [' + @loginName + '] WITH PASSWORD=N''' 
    + @Pwd 
    + ''', DEFAULT_DATABASE=[master], CHECK_EXPIRATION=OFF, CHECK_POLICY=OFF;' 
    PRINT N'登录名已创建，密码为:'+@pwd 
    END 
    ELSE 
    BEGIN 
    SET @CreateLogin = 'CREATE LOGIN [' + @loginName + '] WITH PASSWORD=N''' 
    + @Pwd 
    + ''', DEFAULT_DATABASE=[master], CHECK_EXPIRATION=OFF, CHECK_POLICY=OFF,sid='+@Sid+';' 
    PRINT N'已经使用SID创建登录名:'+@loginName 
    
    END 
    EXEC (@CreateLogin) 
    
    --DECLARE @sidtemp NVARCHAR(50) 
    --SELECT @sidtemp=sid FROM sys.server_principals WHERE name=@loginName 
    --PRINT(N'登录名为:'+@loginName+N' SID为: 0x'+CONVERT(VARCHAR(50), @sidtemp, 2) ) 
    END 
    
    
    
    DECLARE @DynamicSQL NVARCHAR(1000) 
    --切换数据库上下文 
    SET @DynamicSQL = N'Use [' + @DatabaseName + ']; ' + 'IF EXISTS(SELECT name FROM sys.database_principals WHERE name='''+@loginName+''') Begin Print(''用户名已存在，跳过创建用户名的步骤'') end else begin CREATE USER [' 
    + @loginName + '] FOR LOGIN ' + @loginName + ' end;IF (''' 
    + @IsWrite 
    + '''=''rw'' or ''' 
    + @IsWrite 
    + '''=''rwv'') BEGIN ALTER ROLE [db_datareader] ADD MEMBER ' + @loginName 
    + ';ALTER ROLE [db_datawriter] ADD MEMBER ' + @loginName 
    + '; END ELSE BEGIN ALTER ROLE [db_datareader] ADD MEMBER ' 
    + @loginName + '; 
    ALTER ROLE db_datawriter DROP MEMBER ' 
    + @loginName + ' 
    ;End;grant execute to ' + @loginName + '; 
    if('''+@IsWrite+'''<>''rwv'') begin deny view definition to ' + @loginName + '; end else begin grant view definition to ' + @loginName + '; end' 
    
    EXEC (@DynamicSQL) 

该存储过程用于创建应用程序连接SQL Server所需的登录名，用户以及对应权限，当用户或登录名存在时还会跳过该步骤，使用该存储过程的示例如：   

    
    
    EXEC sp_CreateUser 'UserName','rw','DatabaseNam'
    EXEC sp_CreateUser 'tesefx','r','Test','0xE39CA97EBE03BB4CA5FF78E50374EEBB' 

上述执行的第一行是创建一个标准的帐号，账户名UserName，赋予对DatabaseNam的库的读写权限，并返回生成的GUID密码。第二个存储过程是使用第四个参数sid创建登录名，由于在AlwaysOn或镜像的环境中，两端登录名需要有相同的SID，因此提供了在该情况下使用SID创建登录名的办法。

如果需要，可以将该存储过程按照自己的需要去修改。
