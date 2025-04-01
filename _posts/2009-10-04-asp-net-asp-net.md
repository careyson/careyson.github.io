---
layout: post
title: "Asp.net控件开发学习笔记(五)---Asp.net客户端状态管理"
date: 2009-10-04
categories: blog
tags: [博客园迁移]
---

****

Asp.net提供了很多种与客户端状态交互的方式，控件开发人员可以给控件添加额外的值\(比如控件的ViewState\)来使控件貌似能记住前一个值.Asp.net提供了四种客户端状态管理的方式。他们是:

l ViewState

l URL strings

l Hidden Html Variables

l Cookies

**URL String**

**** 利用URL传值请求服务器是简单并且应用最广泛的。比如在电子商务中，一个像这样的地址：

[http://xxx.com/product.aspx?categoryid=1&productid=1](http://xxx.com/product.aspx?categoryid=1&productid=1)

表示传入两个键值对。

在服务器接收对应值时可以用Request对象的QueryString属性和Params属性来进行访问，也可以利用Request本身的索引器来访问，比如Request\[“category”\]。

注意：QueryString属性只能访问以GET方式传的值.

**Cookies**

**** Cookies是一个通过在Http协议中添加额外的信息让服务器和客户端共同实现在用户的机器上存储一定量的信息.Cookies里存放的信息针对特定站点，并且有时间限制。这意味着Cookies在一个站点存放的信息只能这个站点读取，而不能在其他站点被读取。

Cookies的信息是通过Http头里发送Set-Cookies然后加上服务器想在客户端存储的信息.

在Asp.net中对Cookies的操作是通过HttpResponse类的Cookies属性.

给客户端的Cookies赋值的代码如下:

Response.Cookies\["LastVisit"\].Value = DateTime.Now.ToShortDateString\(\);

Response.Cookies\["LastVisit"\].Expires = DateTime.Now.AddDays\(1\);

这两行代码会在Http头中传送到客户端服务器,HTTP会如下:

Set-Cookie: LastVisit=mm/dd/yy; path=/

当在对此代码进行读取时，只需要利用Request对象中的Cookies属性,代码如下

string firstname = Request.Cookies\["LastVisit"\].Value;

在Cookies中，不要存储大量信息.在控件开发的过程中，尽量不要使用Cookies,因为Cookies可能被客户端浏览器禁用.

**HTML Hidden variables**

**** Html hidden variable也是被经常使用的客户端状态存储方式,在这种方式相对于前两种方式的优势在于，这种方式没有传送字节的大小限制，并且不用怕客户端浏览器不支持（啥？难道有不支持HTML的浏览器？？？）

利用Http Post方法，可以将客户端的Hidden variable回传到服务器.Asp.net通过System.Web.UI.HtmlControls.HtmlInputForm服务器控件,这个控件会在页面中产生如下代码：

<form id="first" method="post" runat="server">

而当render到客户端时，会产生如下代码

<form id="first" method="post" action=”first.aspx”>

注意，first.aspx就是指向页面本身

再来看一个完全点的例子:

<form id="first" method="post" runat="server">

<input type="text" value="CareySon" id="name" />

<input type="text" value="Write Code" id="Task" />

</form>

当上面的form被提交时，或者利用javascript来提交时，asp.net会将当前所有的input格式化成字符串以便服务端进行提取.上面的代码格式化成字符串时会变成:

Name=CareySon&Task==Write Code

而在服务器端进行读取时，可以使用Request对象的Form属性索引器或者Params属性索引器:

string name = Request.Form\["name"\];

string task = Request.Params\["task"\];

Asp.net的回传机制也可以用下图表示:  


![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-10-04-asp-net-asp-net/asp-net-asp-net-asp.net回传机制.jpg)

剑是双刃的，当然Hidden Form也并不是只有好处。比如Hidden Form的值虽然不显示在网页中，但是依然可以被用户查看，所以不要在Hidden Form里存放敏感信息，否则必须的进行字符串加密.还有当Hidden Form中存放的值过大时，会有一些潜在的性能问题.因为每次进行Post提交的时都会将所有的Hidden Form提交的服务器L

当然，虽然有一些缺点，但Hidden Form还是在控件开发中储存状态信息的比较好的方式.

**ViewState**

**** ViewState的本质其实就是在Hidden Form上抽象出一层，换句话说，ViewState的存储原理其实就是利用了Hidden Form.ViewState。克服了Hidden Form一些硬性弱点，比如ViewState会对Hidden Form里的值进行压缩，编码使减少传输的大小并使客户端无法查看Hidden Form里的值。在本质上ViewState就是如下一个Hidden Form:

<input type="hidden" name="\_\_VIEWSTATE" id="\_\_VIEWSTATE" value=" " />

ViewState还有一个比较有用的作用是用于存储控件状态.即存储与控件有关的数据.ViewState是System.Web.UI.StateBag类的实例,而StateBag实现了很多的接口，如下:

**接口** |  **描述**  
---|---  
**ICollection******|  Defines enumerators, synchronization methods, and size for collections  
**IDictionary******|  Specialized collection interface that implements a collection of name/value pairs  
**IEnumerable******|  Provides the enumerator for iteration over a collection  
**IStateManager******|  Defines the properties and methods required to support ViewState management in server controls  
  
其中最有趣的是IStateManager接口.StateManager实现了这个接口用于存储和载入控件的ViewState. .net Framework利用ISateManager对控件的ViewState在被序列化并存入名称为\_viewstate的Hidden Form中之前进行精简.

在ViewState的状态信息中存储着以键/值对方式存储的控件信息，（包括当前页面，因为System.Web.UI.Page也是继承于System.Web.UI.Control的）。在页面执行过程中.ViewState会被Hash运算和压缩.最终存入名称为\_ViewState的Hidden Form中。此外，ViewState能够防止修改，任何在Asp.net页面处理周期之外对ViewState的修改都会被Asp.net发现并且做出处理。

**简单的使用**

**** ViewState听起来很复杂，但是使用起来却非常简单.对ViewState赋值的时候只需要：

ViewState\["Task"\] = "Write Code";

上面的代码在客户端生成的时候会生成如下代码:

<input type="hidden" name="\_\_VIEWSTATE" id="\_\_VIEWSTATE" value="/wEPDwULLTE2MTY2ODcyhc2spkL8ufmlbb5xWbI/" />

对ViewState的读取也是类似的方法.代码如下:

string task = ViewState\["Task"\].ToString\(\);

页面中的ViewState在很多时候会很庞大，这大大加重了服务器负担。所以开发人员需要将不需要ViewState的控件的EnableViewState设置成false,这个属性时System.Web.UI.Control的，这意味着所有的控件都具有这个属性.
