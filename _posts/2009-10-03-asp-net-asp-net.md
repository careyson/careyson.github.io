---
layout: post
title: "Asp.net控件开发学习笔记(四)---Asp.net服务端状态管理"
date: 2009-10-03
categories: blog
tags: [博客园迁移]
---

**Asp.net****请求处理构架**

当一个客户端浏览器对IIS发起访问请求资源时（比如一个.aspx文件），Asp.net会初始化并维护一个包含了多个Response和Request的Http Session 的客户端的连接。一次典型的访问如下图:  


  
![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-10-03-asp-net-asp-net/asp-net-asp-net-IIS处理Http请求的图例.jpg) 上图中，首先，一个请求发到IIS服务器，IIS会检查请求的扩展名，如果是aspx或者ascx文件，IIS会自动匹配到aspnet\_isapi.dll来处理这个请求，如果是其他扩展名的文件，IIS会自动匹配到对应ISAPI文件来处理请求。

请求的过程会执行HttpRuntime对象，而HttpRuntiem会利用HttpApplicationFactory对象来确认当前的AppDomain并创建HttpApplication对象来处理请求。Global.asax处理的事件就是基于HttpApplication对象存在的事件。在当前Application中，当前用户的用户信息会通过HttpApplication对象的Context进行访问.接下来执行过程到了HttpModule,任何执行HttpModule的类在这时都会在程序中注册并引发他们的事件。比如Global.asax中的全局事件Session\_Start和Session\_End事件其实就是SessionStateModule,它实现了HttpModule.所以HttpModule的作用是实行全局的功能.

当HttpModule执行完成后，会到HttpHandler这一块,不同的请求会调用不同的HttpHandler，HttpHandler的执行方法是调用其内部的ProcessRequest\(\)方法，ProcessRequest\(\)方法只有一个参数，参数类型为保存了当前用户状态的HttpContext对象。然后,HttpHandler会负责利用Context.Response.Write\(\)方法来响应当前的请求.

上面的整个处理过程都是利用了Asp.net的对对象，这些对象的关系可以简单用下图表示:

****

**![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-10-03-asp-net-asp-net/asp-net-asp-net-web.ui的主要命名空间.jpg)HttpHandler**

**** HttpHandler是Asp.net的处理.aspx和.asmx的构架和方法.HttpHandler允许用户在应用程序处理单个的Url或者相同的扩展名.Asp.net里面有两个Build-in的HttpHandler,如下:

**Handler** |  **描述**  
---|---  
**Asp.net Web Service** |  默认用于处理.asmx的HttpHandler  
**Asp.net****页面** |  默认用于处理.aspx的HttpHandler  
  
注意，上面的描述中用了默认，这意味这我们也可以写自己的处理.asmx或.aspx的HttpHandler实现

Asp.net的PageHandlerFactory是用来专门为创建用于被Developer操作的Page实例的,在这个实例中会包含我们常用的用户信息，比如Session,Application,ViewState等…….

通常情况下,HttpHandler可以是异步的，也可以使同步的。

同步的过程是指处理完整个Http请求才返回数据，而异步指处理完请求立刻返回数据.

**Asp.net****和服务端状态管理**

****

Asp.net服务端状态管理是由我们最熟悉的Application和Session对象组成的，它们以集合的方式将用户信息储存在服务器.

Application是面向全局的，而Session对象是针对特定用户的.这两个对象都可以通过HttpContext对象来进行访问。

**HttpContext****对象**

HttpContext提供了服务端状态管理并实现了HttpApplicationState和HttpSessionState,下面是一些HttpContext对象的属性:

|  [AllErrors](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/01fa8fb0-5696-866e-50aa-7934ccd003c2.htm) |  Gets an array of errors accumulated while processing an HTTP request.  
---|---|---  
|  [Application](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/9d82a344-207b-e094-0131-4f41deba3994.htm) |  Gets the [HttpApplicationState](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/7b74d1f6-4afb-4a69-661b-146e6f808a3d.htm) object for the current HTTP request.  
|  [ApplicationInstance](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/20b6abbc-f320-199d-54ff-3dbdead8cc7d.htm) |  Gets or sets the [HttpApplication](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/aaf0c446-d27c-fe68-155e-0921c2357f02.htm) object for the current HTTP request.  
|  [Cache](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/15d21688-29ce-bc13-73d6-918d8e5c64bf.htm) |  Gets the [Cache](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/9d1983d0-b5cf-daf0-7d9b-1715c8a4d1da.htm) object for the current application domain.  
|  [Current](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/ce797b91-44c4-cd66-9132-78ab1f26f2fa.htm) |  Gets or sets the [HttpContext](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/728eba6f-5f33-c85c-4ceb-03ba42020feb.htm) object for the current HTTP request.  
|  [Error](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/9896b60b-e20e-6ebe-18f9-bb6dd7ef3c3a.htm) |  Gets the first error \(if any\) accumulated during HTTP request processing.  
|  [Handler](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/89e79262-b741-4e87-7112-312797f4aebc.htm) |  Gets or sets the [IHttpHandler](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/0ee1c462-e6e7-36cd-9e57-1efa29ad8b6c.htm) object responsible for processing the HTTP request.  
|  [Items](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/d685e5d3-d742-7510-6deb-8d3f31374509.htm) |  Gets a key/value collection that can be used to organize and share data between an [IHttpModule](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/4b845223-0603-b231-d7d6-2e6ff2243847.htm) interface and an [IHttpHandler](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/0ee1c462-e6e7-36cd-9e57-1efa29ad8b6c.htm) interface during an HTTP request.  
|  [PreviousHandler](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/d491f89f-d08b-2c99-d2db-7ade8a5ce95c.htm) |  Gets the [IHttpHandler](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/0ee1c462-e6e7-36cd-9e57-1efa29ad8b6c.htm) object for the parent handler.  
|  [Profile](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/79c3a8bb-5d70-181d-e73e-3a69501d043f.htm) |  Gets the [ProfileBase](http://www.cnblogs.com/CareySon/admin/ms-help://MS.MSDNQTR.v90.en/fxref_system.web/html/499ed000-e7cf-ffb3-d89d-bc418ffefa99.htm) object for the current user profile.  
  
**服务端状态管理总结**

**** 通常情况下,在开发服务器控件时，尽量少用服务端的状态管理，尤其是在能够使用客户端状态管理时，就不要用服务端状态管理。但在一些情况下，客户端浏览器被限制，比如cookies被禁止，这时使用服务端状态管理还是比较方便的J
