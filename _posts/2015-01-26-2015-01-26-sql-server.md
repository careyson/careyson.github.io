---
layout: post
title: "如果正确读取SQL Server中的扩展事件？"
date: 2015-01-26
categories: blog
tags: [博客园迁移]
---

SQL Server中使用扩展事件捕捉所需的信息后，可以选择存放的位置。比如说内存或文件中，但无论存在哪里，其本质都是一个大XML。因此在SQL Server中读取该XML就是解析扩展事件结果的方式。

微软官方或者一些SQL Server论坛提供了使用SQL XML解析扩展事件的脚本，如代码清单1所示。
    
    
       1: WITH    events_cte
    
    
       2:           AS ( SELECT   DATEADD(mi,
    
    
       3:                                 DATEDIFF(mi, GETUTCDATE(), CURRENT_TIMESTAMP),
    
    
       4:                                 xevents.event_data.value('(event/@timestamp)[1]',
    
    
       5:                                                          'datetime2')) AS [event time] ,
    
    
       6:                                                             xevents.event_data.value('(event/@name)[1]',
    
    
       7:                                                  'nvarchar(128)') AS [Event Name],
    
    
       8:                         xevents.event_data.value('(event/action[@name="client_app_name"]/value)[1]',
    
    
       9:                                                  'nvarchar(128)') AS [client app name] ,
    
    
      10:                         xevents.event_data.value('(event/action[@name="client_hostname"]/value)[1]',
    
    
      11:                                                  'nvarchar(max)') AS [client host name] ,
    
    
      12:                         xevents.event_data.value('(event/action[@name="sql_text"]/value)[1]',
    
    
      13:                                                  'nvarchar(max)') AS [sql_text] ,
    
    
      14:           
    
    
      15:                         xevents.event_data.value('(event/action[@name="database_name"]/value)[1]',
    
    
      16:                                                  'nvarchar(max)') AS [database name] ,
    
    
      17:                         xevents.event_data.value('(event/action[@name="username"]/value)[1]',
    
    
      18:                                                  'nvarchar(max)') AS [username] ,
    
    
      19:                         xevents.event_data.value('(event/action[@name="duration"]/value)[1]',
    
    
      20:                                                  'bigint') AS [duration (ms)] ,
    
    
      21:                         xevents.event_data.value('(event/action[@name="cpu_time"]/value)[1]',
    
    
      22:                                                  'bigint') AS [cpu time (ms)] ,
    
    
      23:                         xevents.event_data.value('(event/data[@name="object_name"]/value)[1]',
    
    
      24:                                                  'nvarchar(max)') AS [OBJECT_NAME]
    
    
      25:                FROM     sys.fn_xe_file_target_read_file('D:\XeventResutl\DDLAudit*.xel',
    
    
      26:                                                         NULL, NULL, NULL)
    
    
      27:                         CROSS APPLY ( SELECT    CAST(event_data AS XML) AS event_data
    
    
      28:                                     ) AS xevents
    
    
      29:              )
    
    
      30:     SELECT  *
    
    
      31:     FROM    events_cte
    
    
      32:     ORDER BY [event time] DESC;

代码清单1.读取扩展事件文件的脚本

但代码清单1的脚本使用的是XQuery，XQuery在使用Xml的节点属性作为删选条件时，数据上千以后就会变得非常慢。因此我对上述脚本进行了改写，将XML读取出来后，变为节点的集合以关系数据格式存放，再用子查询进行筛选，这种方式读取数据基本上是秒出，如代码清单2所示。
    
    
       1: WITH   tt
    
    
       2:          AS ( SELECT   MIN(event_name) AS event_name ,
    
    
       3:               DATEADD(hh,DATEDIFF(hh, GETUTCDATE(), CURRENT_TIMESTAMP),
    
    
       4:                                CONVERT(DATETIME, MIN(CASE WHEN d_name = 'collect_system_time'
    
    
       5:                                                          AND d_package IS NOT NULL THEN d_value
    
    
       6:                                                      END))) AS [event_timestamp] ,
    
    
       7:                        CONVERT 
    
    
       8:        (VARCHAR(MAX), MIN(CASE WHEN  d_name = 'client_hostname'
    
    
       9:                                     AND d_package IS NOT NULL THEN d_value
    
    
      10:                           END)) AS [Client_hostname] ,
    
    
      11:                        CONVERT 
    
    
      12:        (VARCHAR(MAX), MIN(CASE WHEN --event_name = 'sql_batch_completed'
    
    
      13:                                d_name = 'client_app_name'
    
    
      14:                               THEN d_value
    
    
      15:                     END)) AS [Client_app_name] ,
    
    
      16:                        CONVERT 
    
    
      17:        (VARCHAR(MAX), MIN(CASE WHEN  d_name = 'database_name'
    
    
      18:                                     AND d_package IS NOT NULL THEN d_value
    
    
      19:                           END)) AS [database_name] ,
    
    
      20:                           CONVERT
    
    
      21:                                   (VARCHAR(MAX), MIN(CASE WHEN  d_name = 'object_name'
    
    
      22:                                      THEN d_value
    
    
      23:                           END)) AS [object_name] ,
    
    
      24:                        CONVERT 
    
    
      25:        (BIGINT, MIN(CASE WHEN event_name = 'sql_batch_completed'
    
    
      26:                               AND d_name = 'duration'
    
    
      27:                               AND d_package IS NULL THEN d_value
    
    
      28:                     END)) AS [sql_statement_completed.duration] ,
    
    
      29:             
    
    
      30:                        CONVERT 
    
    
      31:        (VARCHAR(MAX), MIN(CASE WHEN d_name = 'sql_text'
    
    
      32:                                      THEN d_value
    
    
      33:                           END)) AS [sql_statement_completed.sql_text] ,
    
    
      34:                        CONVERT 
    
    
      35:        (VARCHAR(MAX), MIN(CASE WHEN d_name = 'username'
    
    
      36:                                     AND d_package IS NOT NULL THEN d_value
    
    
      37:                           END)) AS [username] 
    
    
      38:               FROM     ( SELECT    * ,
    
    
      39:                                    CONVERT(VARCHAR(400), NULL) AS attach_activity_id
    
    
      40:                          FROM      ( SELECT    event.value('(@name)[1]',
    
    
      41:                                                            'VARCHAR(400)') AS event_name ,
    
    
      42:                                                DENSE_RANK() OVER ( ORDER BY event ) AS unique_event_id ,
    
    
      43:                                                n.value('(@name)[1]',
    
    
      44:                                                        'VARCHAR(400)') AS d_name ,
    
    
      45:                                                n.value('(@package)[1]',
    
    
      46:                                                        'VARCHAR(400)') AS d_package ,
    
    
      47:                                                n.value('((value)[1]/text())[1]',
    
    
      48:                                                        'VARCHAR(MAX)') AS d_value ,
    
    
      49:                                                n.value('((text)[1]/text())[1]',
    
    
      50:                                                        'VARCHAR(MAX)') AS d_text
    
    
      51:                                      FROM      ( SELECT    ( SELECT
    
    
      52:                                                              CONVERT(XML, target_data)
    
    
      53:                                                              FROM
    
    
      54:                                                              sys.dm_xe_session_targets st
    
    
      55:                                                              JOIN sys.dm_xe_sessions s ON s.address = st.event_session_address
    
    
      56:                                                              WHERE
    
    
      57:                                                              s.name = 'DDL'
    
    
      58:                                                              AND st.target_name = 'ring_buffer'
    
    
      59:                                                            ) AS [x]
    
    
      60:                                                FOR
    
    
      61:                                                  XML PATH('') ,
    
    
      62:                                                      TYPE
    
    
      63:                                                ) AS the_xml ( x )
    
    
      64:                                                CROSS APPLY x.nodes('//event') e ( event )
    
    
      65:                                                CROSS APPLY event.nodes('*')
    
    
      66:                                                AS q ( n )
    
    
      67:                                    ) AS data_data
    
    
      68:                        ) AS activity_data
    
    
      69:               GROUP BY unique_event_id
    
    
      70:             )
    
    
      71:    SELECT  *
    
    
      72:    FROM    tt
    
    
      73:  

代码清单2.对扩展事件结果的优化读取方式

参考资料：<http://blog.wharton.com.au/2011/06/13/part-5-openxml-and-xquery-optimisation-tips/>
