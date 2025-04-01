---
layout: post
title: "使用PowerShell收集多台服务器的性能计数器"
date: 2016-09-06
categories: blog
tags: [博客园迁移]
---

## 写在前面

当管理多台Windows Server服务器时（无论是DB、AD、WEB以及其他的应用服务器），当出现性能或其他问题后，参阅性能计数器都是一个非常好的维度从而推测出问题可能出现的原因，再不济也能缩小需要考虑的问题范围，因此定期收集每一台服务器的计数器就会使得问题有据可循。并且收集到的数据也可以作为BaseLine，即使没有出现问题也可以预先判断一些问题。

之前看到网上的大多数收集性能计数器的文章都比较局限，一般是只收集单台服务器，因此我分享一个多服务器的写法。

至于为什么使用PowerShell，因为在微软系产品来说像Python等脚本语言虽然有丰富的开源代码没有太好的对应接口，而PowerShell每一个微软自己的产品都提供了大量的Cmdlet，调用起来甚是方便：-）

## 核心Cmdlet

获取性能计数器的核心cmdlet就是Get-Counter了，该Get-Counter主要使用两个参数，分别为要获取的计算机名称-ComputerName与性能计数器列表-Counter，这里要注意的是，获取性能计数器需要在被获取服务器有对应权限（**Performance Monitor Users组** ），我这里的例子是使用域管理员帐号收集域内服务器，因此不考虑权限问题。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-09-06-powershell/powershell-35368-20160906144229832-735420009.png)](http://images2015.cnblogs.com/blog/35368/201609/35368-20160906144229207-1656504495.png)

图1.获取到的远程服务器性能计数器

然后将获取到的结果保存到变量中，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-09-06-powershell/powershell-35368-20160906144231129-917930275.png)](http://images2015.cnblogs.com/blog/35368/201609/35368-20160906144230410-53866321.png)

图2.将计数器结果保存到变量中

## 收集多台服务器的多个计数器

将所需收集的服务器以及所需收集的计数器保存到记事本内，方便随时添加或减少服务器或者计数器，记事本写法如下：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-09-06-powershell/powershell-35368-20160906144232410-908539781.png)](http://images2015.cnblogs.com/blog/35368/201609/35368-20160906144231707-1650795134.png)

图3.计数器与服务器配置

在PowerShell中使用Get-Content读取配置文件内容，如下：
    
    
    $currentPath=Split-Path ((Get-Variable MyInvocation -Scope 0).Value).MyCommand.Path
    
    
    #读取需要收集的性能计数器列表
    
    
    $ServerNeedScan=get-content $currentPath\ServerNeedScan.txt
    
    
    $ServerNeedScanArray=$ServerNeedScan.Split(",")
    
    
     
    
    
     
    
    
    #读取需要收集的性能计数器
    
    
    $PerfCounter=get-content $currentPath\PerfmonCounter.txt
    
    
    $PerfCounterArray=$PerfCounter.Split(",")

代码1.读取服务器列表和计数器列表

现在由于收集的计数器中部分计数器是关于SQL Server的，而部分服务器可能带有实例名称，而对于带有SQL Server实例名称的计数器需要把实例和及其名分开，然后把计数器名称中实例名部分进行替换，代码如下：
    
    
    foreach ($fcomputer in $ServerNeedScanArray)
    
    
    {
    
    
       
    
    
        if($fcomputer.Trim() -eq "")
    
    
        {
    
    
            continue
    
    
        }
    
    
        #检查是否为默认实例
    
    
        $computer=""
    
    
        if($fcomputer -like "*\*")
    
    
        {
    
    
            $instanceName=$fcomputer.Substring($fcomputer.IndexOf("\")+1,$fcomputer.Length-$fcomputer.IndexOf("\")-1)  
    
    
            $computer=$fcomputer.Substring(0,$fcomputer.IndexOf('\'))
    
    
        }
    
    
        else
    
    
        {
    
    
            $computer=$fcomputer
    
    
            $instanceName=""
    
    
        }
    
    
     
    
    
    #遍历所有计数器
    
    
        $fullCounter=@()
    
    
        foreach($counter in $PerfCounterArray)
    
    
        {
    
    
            $c=""
    
    
            $c+="\"
    
    
            $c+=$counter
    
    
            $fullCounter+=$c
    
    
         }
    
    
     
    
    
    $NoDeaultInstanceName="MSSQL`$"
    
    
    $NoDeaultInstanceName+=$instanceName
    
    
    #如果是默认实例
    
    
    if($instanceName -eq "")
    
    
    {
    
    
       $fullCounter | % { 
    
    
       if($_ -like "*network*")
    
    
       {
    
    
            $finalCounter+= $_.ToLower()
    
    
           
    
    
       }
    
    
       else
    
    
       {
    
    
           $finalCounter+= $_.ToLower().Replace("*","_total")
    
    
       }
    
    
       }
    
    
    }
    
    
    #如果是非默认实例
    
    
    else
    
    
    {
    
    
       $a=$fullCounter | % { 
    
    
       if($_ -like "*network*")
    
    
       {
    
    
            $finalCounter+= $_.ToLower().Replace("sqlserver", $NoDeaultInstanceName)
    
    
           
    
    
       }
    
    
       else
    
    
       {
    
    
            $finalCounter+= $_.ToLower().Replace("*","_total").Replace("sqlserver", $NoDeaultInstanceName)
    
    
       }
    
    
     
    
    
       } 
    
    
    }

代码2.替换SQL Server计数器中的非默认实例

## 将结果插入一台SQL Server

上述情况就已经准备好了计数器和服务器名称，现在就可以将这些数据插入到一台集中的SQL Server服务器，代码如下：
    
    
    $a=(Get-Counter -ComputerName $computer -Counter $finalCounter).CounterSamples |Select-Object Path,CookedValue
    
    
     
    
    
     
    
    
          $InsertSQL=""
    
    
          $curentTime=Get-Date
    
    
          foreach($PerformanceCounter in $a)
    
    
          {
    
    
                
    
    
              $realvalue=$PerformanceCounter.CookedValue
    
    
              $InsertSQL+="INSERT INTO PerfCounter(instancename,event_timestamp,Counter,CounterValue)
    
    
                  VALUES(''"+$fcomputer+"'',''"+$curentTime+"'',''"+$PerformanceCounter.Path+"'',''"+$realvalue.ToString()+"'');"
    
    
              
    
    
           
    
    
                 
    
    
           }
    
    
          $connectionString3="data source=服务器IP;database=test;uid=perf_writer;pwd=123123;"
    
    
          $conn2=new-object system.Data.SqlClient.SqlConnection($connectionString3)
    
    
          $conn2.open()
    
    
     
    
    
          $cmd2=$conn2.CreateCommand()
    
    
     
    
    
           $cmd2.CommandText=$InsertSQL
    
    
           $cmd2.ExecuteNonQuery()
    
    
           $conn2.Close()

代码3.读取计数器后插入SQL Server

现在，读取一台服务器并将计数器记录到数据库中的代码就写好了，并且已经可以灵活配置需要读取的计数器和机器名。

## 多线程读取

如果需要记录计数器的服务器比较多时，那么循环遍历每一台服务器就会花费比较长的时间，因此需要多线程来加快这一个速度，在PowerShell中，启用多线程的cmdlet是start-job，我们首先需要将代码2和代码3的脚本封装到一个script block中，并设置可传入的参数，如代码4。
    
    
    $sb = [scriptblock]::Create('
    
    
      param($instanceName,$NoDeaultInstanceName,$fullCounter,$fcomputer,$computer)
    
    
    #这里写其他代码
    
    
     
    
    
    ')
    
    
     
    
    
    #开始异步线程，并传入参数
    
    
    start-job -scriptblock $sb -Argument $instanceName,$NoDeaultInstanceName,$fullCounter,$fcomputer,$computer 
    
    
     

代码4.利用异步线程读取计数器数据并插入SQL Server

经过测试，PowerShell对同时可以并发的线程做了限制，这个限制很奇怪，我在每台服务器上测试的结果并不相同，因此如果同时全部并发执行这些线程，某些线程会因为限制而不起作用，因此如果需要记录性能计数器的服务器比较多的话，会丢失一部分服务器信息，我的解决办法是限制同时并发的进程数量，如果进程数量超过规定数值，则等待1秒再次检测，如果检测通过再启动新进程，代码如代码5所示。
    
    
    While (@(Get-Job | Where { $_.State -eq "Running" }).Count -gt 5) {
    
    
            Write-host "Waiting for background jobs..."
    
    
            Start-Sleep -Seconds 1
    
    
          }

代码5.检测处于“运行中”进程的数量是否大于5

## 定期执行脚本

现在，上面脚本就可以收集多台服务器的性能计数器，并将结果保存到SQL Server了，现在只需要定期（比如2分钟一次）执行该脚本即可。使用Windows计划任务是定期执行PowerShell脚本推荐的方式，如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-09-06-powershell/powershell-35368-20160906144233348-492464356.png)](http://images2015.cnblogs.com/blog/35368/201609/35368-20160906144232926-1437676057.png)

图4.使用计划任务2分钟收集一次性能计数器信息

在图4中，我们注意到使用了-NonInteractive参数，该参数用于在执行时，不弹出PowerShell窗口。

## 结果

现在，我们可以看到收集后的性能计数器信息，如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-09-06-powershell/powershell-35368-20160906144235582-234282399.png)](http://images2015.cnblogs.com/blog/35368/201609/35368-20160906144234082-1758184253.png)

图5.收集到的性能计数器信息

有了上述性能计数器信息，我们可以使用一些可视化工具分析这些信息，比如我将数据导入到ElasticSearch中，出几张简单的报表，如图6所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2016-09-06-powershell/powershell-35368-20160906144238691-968924603.png)](http://images2015.cnblogs.com/blog/35368/201609/35368-20160906144237441-572325938.png)

图6.使用这些性能计数器出简单的报表

这些报表可以帮助我们直观的看出一些问题，比如图6中的forward record可以看到，某些实例大量缺少聚集索引，或者下面的Top Lock Wait可以看到某些实例定期会产生大量的锁阻塞，从而我们可以更容易提前发现问题，进行解决。

## 小结

定期收集一些服务器的信息可以帮助在运维工作中掌握主动，在业务中现在流行所谓的“大数据促进决策”，其实在IT运维本身中，收集大量的数据同样重要，通过数据我们甚至可以在问题出现之前发现问题。

在WIndows下PowerShell无疑是最适合做这一工作的语言。
