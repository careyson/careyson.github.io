---
layout: post
title: "【译】在ASP.Net和IIS中删除不必要的HTTP响应头"
date: 2009-12-14
categories: blog
tags: [博客园迁移]
---

## **引入**

每次当浏览器向Web服务器发起一个请求的时，都会伴随着一些HTTP头的发送.而这些HTTP头是用于给Web服务器提供一些额外信息以便于处理请求。比如说吧。如果浏览器支持压缩功能，则浏览器会发送 _Accept-Encoding_ HTTP头，这样一来服务器便知道浏览器可以使用哪种压缩算法。还有任何在上一次传输中服务端设置的cookies也会通过 _Cookies_ HTTP头来回传到服务器，浏览器还会发送用于让服务端知道客户使用的是何种浏览器（IE,火狐，Safari等），浏览器版本，操作系统以及其他相关信息的 _User-Agent_ HTTP头。

同样，Web服务器也会在发送回客户端时伴随着一些HTTP头,这些HTTP头可以通知浏览器如何生成相应的内容和缓存内容的时间，Web服务器也会发送自身的识别信息，这很像 _User-Agent_ HTTP头,这些头信息包括Web服务器的版本以及当前使用的ASP.Net的版本.

在某些情况下一些HTTP头是必须的，然而Web服务器的自身识别头信息却并不是那么必要，这些信息会让每次的传输多出100字节左右。好吧，我同意100字节单独来说并不是一个很大的数字，但在传输成千上万次时，这些信息也不可小觑。此外，提供服务器信息也会导致安全问题，有些攻击者很了解特定的服务器以及特定的Asp.net版本所包含的漏洞，他们会扫描大量服务器然后选择特定的服务器（译者按:比如IIS和Asp.net 2.0.50727）来作为他们的攻击目标。

而这篇文章就来讲如何删除这些不必要的HTTP响应头.

## **观察Web服务器的HTTP响应头**

为了看到从服务器和浏览器之间通信的HTTP头，你需要在浏览器安装一些插件.比如说[Fiddler](http://www.fiddler2.com/fiddler2/)就是一个微软发布的免费的用于记录HTTP日志的软件。而这些HTTP日志会包含HTTP头,在这篇文章中我会假设读者已经熟悉了这个软件，假如你并不熟悉这个软件的话，我推荐阅读[Troubleshooting Website Problems by Examining the HTTP Traffic](http://www.4guysfromrolla.com/webtech/111208-1.shtml)，这篇文章里详细讲述了如何安装&使用Fiddler.

使用Fiddler，找一个使用IIS和Asp.net的Web服务器,比如微软asp.net官方网站,通常在默认情况下，HTTP响应头会包含3个Web服务器的自身识别头.

  * 服务器-指定是何种服务器以及服务器版本，比如：
    * Server:Microsoft-IIS/6/0
    * Server:Microsoft-IIS/7.0
  * X-Powered-By,用于表示这个站点是“Powered by asp.net”
    * X-Powered-By:ASP.NET
  * X-AspNet-Version，用于指定当前的Asp.net版本，注意就算你使用Asp.net 3.5但在X-AspNet-Version可能会报告使用的是2.0:
    * X-AspNet-Version：2.0.50727
    * X-AspNet-Version：1.1.4322
  * X-AspNetMvc,指定当前版本的Asp.net MVC\(如果使用Asp.net MVC的话\):
    * X-AspNetMvc-Version:1.0



这些服务器自身识别信息在大多数情况下并不会被浏览器使用，因此可以被安全的移除，这篇文章的余下部分将会讲述如何移除这些HTTP头

#### **移除X-AspNet-Version HTTP头**

X-AspNet-Version HTTP头会告诉全世界我们服务器当前使用的Asp.net版本，去除这个HTTP头简直是小菜一碟，只需要在Web.Config的<system.web>节点下添加如下内容:
    
    
    <httpRuntime enableVersionHeader="false" />  

是不是非常轻松愉快？

#### **移除X-AspNetMvc-Version HTTP头**

X-AspNetMvc-Version HTTP头会自动被Asp.net MVC框架加入进去，如果你没有使用Asp.net MVC,这个HTTP头不会存在.移除这个HTTP头的方式是在Global.asax的`Application_Start`事件中将`MvcHandler类的`DisableMvcResponseHeader属性设置为True``
    
    
    // C#
    MvcHandler.DisableMvcResponseHeader = true;
    
    
    ' VB
    MvcHandler.DisableMvcResponseHeader = True 

#### **移除X-Powered-By HTTP头**

X-Powered-By HTTP头并不只是在Asp.net中存在，其他服务端语言，比如PHP,也会包含这个HTTP头,当Asp.net被安装时，这个头会作为一个定制的HTTP头插入IIS中,因此,我们需要将这个HTTP头从IIS的配置中删除,如果你的网站是在共享的环境下并且没有使用IIS7并使用管道模式，你不得不为此联系你的空间提供商来帮你移除。\(如果你的网站是在IIS7环境下，那你可以通过HTTP Module的形式通过编程来移除\)

在IIS6中移除X-Powered-By HTTP头:

  1. 启动IIS Manager
  2. 展开Website目录
  3. 在Website上点击右键并在弹出的菜单中选择属性
  4. 选择HTTP Header标签，所有IIS响应中包含的自定义的HTTP头都会在这里显示，只需要选择响应的HTTP头并点击删除就可以删除响应的HTTP头,如图:



![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-12-14-asp-net-iis-http/asp-net-iis-http-RemoveHeadersIIS6.gif)

而在IIS7中移除X-Powered-By HTTP头的方法是:

  1. 启动IIS Manager
  2. 展开Website目录
  3. 选择你需要修改的站点并双击HTTP响应头部分
  4. 所有的自定义HTTP头全在这里了，删除相应的头仅需要点击右边的”Remove”链接:



![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-12-14-asp-net-iis-http/asp-net-iis-http-RemoveHeadersIIS7.gif)

#### **移除Server HTTP头**

这个HTTP头会自动附加在当前的IIS相应中,删除这个HTTP头可以使用微软免费的[UrlScan](http://technet.microsoft.com/en-us/security/cc242650.aspx)工具.

如果你使用的是IIS7 整合管道模式，你也可以使用HTTP Module来使用编程的方式来去除它。Stefan Grobner's的博客中[IIS 7 - How To Send A Custom "Server" HTTP Header](http://blogs.technet.com/stefan_gossner/archive/2008/03/12/iis-7-how-to-send-a-custom-server-http-header.aspx)这篇文章详细讲述了如何修改Server HTTP标头.简单的说，你需要创建一个HTTP Module并为`PreSendRequestHeaders事件创建事件处理程序,在这个事件处理程序中的代码会类似:`
    
    
    HttpContext.Current.Response.Headers.Remove("Server");  

Howard von Rooijen的文章更深层次的论述了如何在IIS7和整合管道模式中移除Server Http头,更多细节，请查看：[Cloaking your ASP.NET MVC Web Application on IIS 7](http://consultingblogs.emc.com/howardvanrooijen/archive/2009/08/25/cloaking-your-asp-net-mvc-web-application-on-iis-7.aspx)

## **小结**

移除服务器自身识别响应头会有如下好处：

  * 这降低了服务器和浏览器之间所需传输的数据量
  * 使黑客攻击服务器变得更加困难，从而使服务器更加强壮



如上的几个HTTP头并没有带来直接的好处，反而小幅加重了宽带的负担,所幸的是我们可以通过配置的方式进行移除

> Happy Programming\! 
> 
> * By [Scott Mitchell](http://www.4guysfromrolla.com/ScottMitchell.shtml)

\-----------------------------------------------------------------------------------------

原文链接:<http://aspnet.4guysfromrolla.com/articles/120209-1.aspx>
