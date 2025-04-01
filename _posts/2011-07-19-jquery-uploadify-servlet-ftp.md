---
layout: post
title: "Jquery Uploadify插件+Servlet解决FTP多文件上传"
date: 2011-07-19
categories: blog
tags: [博客园迁移]
---

这个小程序的起因是老大让我做一个Adobe LiveCycle的外围小程序，附件要随着工作流一起流转用于每级用户审批作为参考.我用.Net2个小时搞完了，被老大通知这个必须用JAVA做-.-无奈之下搞了两天终于搞出来了.

Uploadify插件是一个界面友好，有进度条，支持多文件上传的插件，官方地址为:<http://www.uploadify.com/>

前台使用的纯HTML+JQuery+Uploadify插件,通过HTTP POST将文件和参数发到后台进行处理

前台截图如下:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-07-19-jquery-uploadify-servlet-ftp/jquery-uploadify-servlet-ftp-201107191030559721.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201107/201107191030536506.png)

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-07-19-jquery-uploadify-servlet-ftp/jquery-uploadify-servlet-ftp-201107191031028995.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201107/201107191031008811.png)

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-07-19-jquery-uploadify-servlet-ftp/jquery-uploadify-servlet-ftp-201107191031069089.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201107/20110719103105857.png)

前台代码如下:
    
    
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title></title>
        <link href="uploader/uploadify.css" rel="stylesheet" type="text/css" />
        <script src="Scripts/jquery-1.4.1.min.js" type="text/javascript"></script>
        <script src="uploader/swfobject.js" type="text/javascript"></script>
        <script src="uploader/jquery.uploadify.v2.1.4.min.js" type="text/javascript"></script>
        <script type="text/javascript">
            function queryString(query) {
                var search = window.location.search + '';
                if (search.charAt(0) != '?') {
                    return undefined;
                }
                else {
                    search = search.replace('?', '').split('&');
                    for (var i = 0; i < search.length; i++) {
                        if (search[i].split('=')[0] == query) {
                            return decodeURI(search[i].split('=')[1]);
                        }
                    }
                    return undefined;
                }
            }; 
        </script>
        <script type="text/javascript">
            $(document).ready(function () {
                if (queryString("URI") != undefined&&queryString("URI1") != undefined) {
                    var flodCode = queryString("URI");
                    var URLOne=queryString("URI1");
                    $("#uploadify").uploadify({
                        'uploader': 'uploader/uploadify.swf',
                        'script': 'servlet/Upload',//Servlet名称
                        'cancelImg': 'uploader/cancel.png',
                        'folder': 'upload',
                        'queueID': 'fileQueue',
                        'auto': false,
                        'method' : 'GET',
                        'multi': true,
                        'filesSelected': '4',
                        'scriptData': {'URL1':URLOne,'dirName':flodCode,'ftpAddress':$("#ftp").val(),'userName':$("#username").val(),'pwd':$("#pwd").val()},
                        'onAllComplete': function () { alert("您的文件已经上传成功"); },
                        'onError': function () { alert("上传出错，请您重新尝试"); }
                    });
                }
                else {
                    $("#Content").html("您好，页面参数错误，请通过正确的途径访问页面")
                }
            });
              
            
        </script>
    </head>
    <body>
    <div id="Content">
        <div id="fileQueue">
        </div>
        <input type="file" name="uploadify" id="uploadify" />
        <p>
            <a href="javascript:$('#uploadify').uploadifyUpload()">上传</a>| <a href="javascript:$('#uploadify').uploadifyClearQueue()">
                取消上传</a>
    
        </p>
        <input type="hidden" id="ftp" value="127.0.0.1"/>
        <input type="hidden" id="username" value="admin"/>
        <input type="hidden" id="pwd" value="admin"/>
    </div>
    </body>
    </html>

因为ftp地址有可能变化，所以我将ftp的地址用户名密码写在前台，通过HTTP POST方式发到后台\(因为是内网用户使用，所以安全问题可以不用考虑）

并且一个FTP地址我准备了一个workflow的一级目录用于存放工作流附件，工作流ID作为二级目录的名称，所以我准备了两个参数，使用HTTP GET方式发往后台,URI1是一级目录的地址，URI是二级目录的地址，所以这里一个合法的地址比如:Uploader.htm?URI=2011719942857171001&URI1=WORKFLOW.

后台使用了org.apache.commons.net.ftp.FTP这个第三方FTP类库进行上传，这个类库对中文名文件支持有问题，好在已经封装后改好了.在后台代码里有详细注释

项目图：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-07-19-jquery-uploadify-servlet-ftp/jquery-uploadify-servlet-ftp-201107191031087462.png)](http://images.cnblogs.com/cnblogs_com/CareySon/201107/201107191031077561.png)

cnFTP是类是FTP上传的类库，upload是处理上传的servlet,后台代码就不贴了，源码里有详细注释。

下面是项目源码下载:

[猛击这里下载项目源码](https://files.cnblogs.com/CareySon/Uploader.rar)

应园友要求，增加了.Net版本的代码，不过这个版本并没有做FTP上传功能，仅仅是上传到服务器里，因为刚做完这个功能就被告知要用JAVA做-.-

[猛击这里下载DotNet项目源码](https://files.cnblogs.com/CareySon/UploaderDotNet.rar)
