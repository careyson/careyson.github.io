---
layout: post
title: "【译】Asp.net MVC 利用自定义RouteHandler来防止图片盗链"
date: 2009-12-30
categories: blog
tags: [博客园迁移]
---

你曾经注意过在你服务器请求日志中多了很多对图片资源的请求吗？这可能是有人在他们的网站中盗链了你的图片所致，这会占用你的服务器带宽。下面这种方法可以告诉你如何在ASP.NET MVC中实现一个自定义RouteHandler来防止其他人盗链你的图片. 

首先，我们来回顾一下当一个请求发往ASP.net MVC站点时的情景，IIS收到请求并将请求转到ASP.net,然后根据URL,或者更确切来说：被请求文件的扩展名.在IIS7 integrated模式下（默认模式）,所有的请求都会匹配到ASP.net中，而在IIS6中，你可以通过通配符来达到和IIS7相同的效果. 

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-12-30-asp-net-mvc-routehandler/asp-net-mvc-routehandler-o_MvcRouting.gif)

在ASP.NET MVC程序中首先涉及的部件是UrlRoutingModule,它是 _System.Web.Routing_ 的一部分.UrlRoutingModule用于第一次检查请求的url和本地磁盘中的文件是否相匹配。如果匹配，UrlRoutingModule会将请求直接回发给IIS，IIS根据地址来进行相应。如果UrlRoutingModule没有在磁盘中找到匹配的文件。它会检查RouteCollection结构来决定是否继续传递请求.UrlRoutingModule会引入RouteHandler和匹配的路径入口（默认情况下是MvcRouteHandler）。而后会引入合适的HttpHandler来处理和请求有关的逻辑。默认情况下，这个HttpHandler会是MvcHandler.而对于图片文件，一般会存在于程序中的某个子目录中，核心的routeModule并没有这种能力因为直接索取图片的url回优先回发给iis，而流程在这时无法执行到RouteHandler被引入.

通常情况下，通过Asp.net取出磁盘上的静态文件都是可以的。然而，如果你想执行一些业务逻辑而不是直接让这类文件响应请求。你需要在某些关键点以编程的方式实现。你可以通过设置 _RouteTable.Routes.RouteExistingFiles = true_ 来避免对现有文件的默认相应行为。Phil Haack\( ASP.NET MVC的高级程序经理\)称之为”核武器级别的选项”，无论是css,js,doc,pdf等文件，在这种模式下所有文件都需要利用Routing来处理。所以确保这一点的关键是对于静态文件的请求不能和磁盘上对应的文件匹配。这会强制RouteModule来对Route表（当然会引入RouteHandler等过程）进行查找。这很容易做，只需要让<img>元素指向一个虚构的目录即可。比如说，你的图片是存放在网站根目录下的images文件夹下，而<img>元素指向一个”graphics”文件夹将不会和存在的文件相匹配。

想做到这些，需要做如下：

  1. 为对于图片的请求注册Route 
  2. 创建RouteHandler来处理这类请求 
  3. 创建HttpHandler来处理实际的请求 



我们首先从步骤2开始，因为如果没有创建RouteHandler却要在路由表中进行注册的话，这不会编译成功的.

RouteHandler很简单，它是IRouteHandler的实现，它只有一个方法--_IHttpHandler IRouteHandler.GetHttpHandler\(RequestContext requestContext\):_
    
    
    public class ImageRouteHandler : IRouteHandler
    {
      public IHttpHandler GetHttpHandler(RequestContext requestContext)
      {
        return new ImageHandler(requestContext);
      }
    }

对于实际的HttpHandler：
    
    
    public class ImageHandler : IHttpHandler
    {
      public ImageHandler(RequestContext context)
      {
        ProcessRequest(context);
      }
    
      private static void ProcessRequest(RequestContext requestContext)
      {
        var response = requestContext.HttpContext.Response;
        var request = requestContext.HttpContext.Request;
        var server = requestContext.HttpContext.Server;
        var validRequestFile = requestContext.RouteData.Values["filename"].ToString();
        const string invalidRequestFile = "thief.gif";
        var path = server.MapPath("~/graphics/");
    
        response.Clear();
        response.ContentType = GetContentType(request.Url.ToString());
    
        if (request.ServerVariables["HTTP_REFERER"] != null &&
            request.ServerVariables["HTTP_REFERER"].Contains("mikesdotnetting.com"))
        {
          response.TransmitFile(path + validRequestFile);
        }
        else
        {
          response.TransmitFile(path + invalidRequestFile);
        }
        response.End();
      }
    
      private static string GetContentType(string url)
      {
        switch (Path.GetExtension(url))
        {
          case ".gif":
            return "Image/gif";
          case ".jpg":
            return "Image/jpeg";
          case ".png":
            return "Image/png";
          default:
            break;
        }
        return null;
      }
    
      public void ProcessRequest(HttpContext context)
      {
      }
    
      public bool IsReusable
      {
        get { return false; }
      }
    }

在上面代码中，IHttpHandler中的 _ProcessRequest,_ 有两个重载，第一个是 _public void ProcessRequest\(HttpContext context\)，_ 在这里我们忽略这个重载,在MVC程序中，我们传入RequestContext对象作为参数，而不是HttpContext对象。ProcessRequest方法会在ImageHandler的构造器中进行调用，在上面代码中，ProcessRequest会首先检查请求图片的地址是否输入我的域（也就是引用图片的网页是我的网站而不是其它人的），如果不是的话，则返回一张其它图片。返回什么样的图片取决于你自己，我看到过很多种这样的图片，有些包含不和谐内容.甚至你可以返回一个1px的透明gif,或者可以使404 not found….

当然，在这点上你还可以采取一些其它步骤，比如说，你当然会希望google索引你的图片，所以如果引用的链接包含”images.google”你可以返回真实图片。你也可以在其它网站盗链你图片不成功的情况下来用日志进行记录.

最后一步要做的是为对图片的请求注册到RouteTable,用于表示ImageRouteHandler来对这部分请求进行处理，在global.axax文件中，加入:
    
    
    routes.Add("ImagesRoute",
                     new Route("images/{filename}", new ImageRouteHandler()));

希望这篇文章不仅可以帮助你阻止那些盗链的吸血鬼，还能让你对Asp.net MVC的底层有更深入的了解以便于你以后再有其他需求时可以进行扩展。

\-----------------------------------------------------------------------------

原文链接:<http://www.mikesdotnetting.com/Article/126/ASP.NET-MVC-Prevent-Image-Leeching-with-a-Custom-RouteHandler>

translated by:[Careyson](www.cnblogs.com/careyson)
