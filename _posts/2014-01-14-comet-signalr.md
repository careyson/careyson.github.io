---
layout: post
title: "Comet服务器推送与SignalR"
date: 2014-01-14
categories: blog
tags: [博客园迁移]
---

HTTP协议是一个典型的Request/Response协议，是基于TCP/IP之上的一个应用层协议，该协议最典型的特点就是无状态且需要客户端发起Request服务端才能进行Response，这意味着服务端无法主动“推送”信息。但现代很多应用需求这种“服务端推送”，比如说监控系统、报价系统、游戏、协同文档、进度条等应用。因此本文会谈论服务器推送技术的不同手段，以及在Asp.Net中的SignalR是如何封装这些细节来达到推送的目的。

### 实现服务器推送的一些手段

由于HTTP协议并不支持全双工，因此目前对于服务器“推送”的手段也是根据HTTP协议的特性玩了很多小花招。但大体上可以分为高端大气的全双工类和略微tricky的长轮询类。Streaming类通常会有比较多的限制，比如说对浏览器的版本要求、需要使用sliverlight或flash等查件来实现全双工等。长轮询类主要是包括长轮询或不间断Ajax请求等。

**Ajax定期请求方式**

这种方式严格来说并不算是服务器推送，而是客户端在一个比较短的间隔内定期去服务器用Ajax请求信息，如果服务器端有了新的事件，则客户端在下一次请求就会获取到，并在客户端调用对应的回调函数来处理这些信息。简单的示意图如图1所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-01-14-comet-signalr/comet-signalr-141440199398.png)](//images0.cnblogs.com/blog/35368/201401/141440194709.png)

图1.Ajax定期请求

当然，这种方式的一些缺点也是显而易见的，首先定期发起请求会白白消耗服务器资源，其次，这种方式也并不是真正的“实时”。

**长连接的方式**

长连接是另一种方式，是对于页面挂起一个额外的Ajax请求，当服务器有事件发生时，将请求返回给客户端，并在此挂起一个长连接。从而避免了定期请求的损耗，如图2所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-01-14-comet-signalr/comet-signalr-141440208147.png)](//images0.cnblogs.com/blog/35368/201401/141440202983.png)

图2.长连接方式

这种方式的缺点同样显而易见，就是需要客户端和服务器对于这部分功能写自定义实现代码。

**使用插件方式**

使用诸如silverlight和flash等插件可以基于socket做全双工的通信，但这种方式需要特定的客户端，跨平台性并不好（比如手机客户端等不支持一些插件，PC端没有预装Silverlight等）。对条件限制比较严格。

**Forever iFrame**

这种方式本质上和长连接的方法非常类似，就是在页面中嵌入一个iframe元素，该元素的Src属性指向被请求的对象，服务端有事件发生就，就回传一个调用客户端JS方法的JS。Iframe中HTTP头的`Transfer-Encoding属性为``chunked，这意味着服务端并不知道要发送给客户端多少数据，也就隐式意味着该连接的长度为无限。`

**HTML5 Web Socket**

[WebSocket](http://zh.wikipedia.org/wiki/WebSocket)是HTML5开始提供的一种浏览器与服务器间进行全双工通讯的网络技术。 WebSocket通信协议于2011年被IETF定为标准 RFC 6455，WebSocketAPI被W3C定为标准。

在WebSocket API中，浏览器和服务器只需要做一个握手的动作，然后，浏览器和服务器之间就形成了一条快速通道。两者之间就直接可以数据互相传送。

WebSocket协议的出现可以避免上述几种方式带来的服务器资源占用和宽带占用。但缺点也是很明显的，对客户端和服务端都有一定要求，包括浏览器的版本和服务器的版本（比如IIS7.5+）

### SignalR？

上面说到了这么多中实现实时应用程序的办法，作为Asp.net框架中，提供了一个叫SignalR的框架来封装这些网络细节，SignalR会自动选择合适的实现技术来实现该种实时程序。我们只要关注更高层面的业务实现，而无需关注技术上的实现细节。

SignalR最低需要基于Jquery 1.6.4，在服务端至少需要是.Net FrameWork 4.0+。

使用SignalR会自动根据环境选择合适的网络实现细节，该过程根据微软的官网定义如下：

  1. 如果浏览器是IE8或低于IE8，使用长连接方式。
  2. 如果配置了JSONP参数，则使用长连接方式。
  3. 如果请求跨域，且客户端和服务器端都支持Web Socket，且客户端支持CORS，则使用Web Socket
  4. 如果没跨域，客户端和浏览器都支持的话，使用Web Socket方式
  5. 如果客户端或服务器端不支持Web Socket的话，会使用HTML5的[Server-sent events](http://en.wikipedia.org/wiki/Server-sent_events "http://en.wikipedia.org/wiki/Server-sent_events")
  6. 如果Server-Sent Event不被支持的话，会使用Forever iFrame
  7. 最后会使用长连接方式



SignalR的实现可以通过在Visual Studio的nuget来获取。SignalR从使用的角度来说模型非常简单，服务端是客户端回调用的HUB方法，而客户端只要引入了对应的JS之后，形成Hub-Proxy，使得服务端被调用后里的方法也可以回调不同的客户端。模型概念如图3所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-01-14-comet-signalr/comet-signalr-141440219708.png)](//images0.cnblogs.com/blog/35368/201401/141440215649.png)

图3.SignalR的Hub模型

在服务端的Hub被调用后，我们可以处理该部分代码，并针对不同的客户端返回信息，一个典型的代码如图4所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-01-14-comet-signalr/comet-signalr-141440228149.png)](//images0.cnblogs.com/blog/35368/201401/141440223459.png)

图4.一些返回给不同客户端的方法

而在客户端，我们仅仅需要引用SignalR的Js文件后，声明了Hub-Proxy，就可以直接调用服务器方法，如图5所示。

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2014-01-14-comet-signalr/comet-signalr-141440235807.png)](//images0.cnblogs.com/blog/35368/201401/141440231733.png)

图5.客户端直接调用服务端的方法

我们注意到，在使用SignalR的过程中，并没有任何关于网络交互技术细节的实现，仅仅是简单的调用。SignalR已经按照本文之前所提到的那样，根据Context选择的具体的实现细节。
