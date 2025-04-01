---
layout: post
title: "【译】使用自定义ViewHelper来简化Asp.net MVC view的开发------part1"
date: 2010-01-05
categories: blog
tags: [博客园迁移]
---

从开发者的角度来看，创建Asp.net MVC的View是一件很爽的事，因为你可以精确控制最终生成的HTML。具有讽刺意味的是不得不写出每一行HTML代码同时也是Asp.net MVC的View中让人不爽的地方。让我用我的一个经历来告诉我创建ASP.Net MVC view Helpers背后灵感的由来。由一小部分开发人员（包括我）和一个CSS设计人员（我们叫他Ricky）组成的小组，开始了一个新的Asp.net MVC的项目,在项目开发过程中；我给页面添加了一些TextBox和一些其他元素，我check-in了我的代码，直到回家我也没再想起过这事。隔夜早晨，刚上班时我就从CSS设计那里收到一封邮件来通知我我必须按照他的CSS指导方针来写HTML，比如说对于textbox,必须遵循以下规则:

  * 每个textbox必须内嵌在li标签中
  * 每一个textbox都必须有一个label标签的for属性与之对应 
  * textbox必须使用input标签并设置type属性为text



对于这些要求我一一照做并修改我的代码符合了后两条规则，但我忘了关于li的指导方针,我很快更新了页面并提交了我的代码。几天后，项目又推进了很多，Ricky来到我的办公桌前并让我看看我所做的改变。打开页面，他开始一一列举那些我不遵循它的UI规定的地方，有很多地方我都忽视了因为我甚至不知道这些指导方针的存在.在他指出这些后，我想：一定会有方法可以让我们两个人都如愿以偿.对于我来说只是需要html标签的id，对于Ricky来说他需要我的HTML符合规范来让他的CSS文件能够选择到合适的html。所以我们引入了view helper.

在我用Asp.net MVC时我注意到我自己写了很多纯Html,比如div和span,同时伴随使用了很多System.Web.Mvc.HtmlHelper来生成html,比如说一个输入名字的textbox:
    
    
    <li> 
        <label for="FirstName">First name</label>
        <%= Html.TextBox("FirstName") %>     
        <%= Html.ValidationMessage("FirstName", "*") %> 
    </li> 

我就想，是不是能有一种方法来将上面的所有代码融合在一起呢。这样不仅让我编程更加轻松，而且再也不用担心Ricky给我设置的条条框框了。理想的情况下会满足以下标准：

  1. 容易执行 
  2. 重用性好 
  3. 强制执行某些标准（比如Ricky的） 
  4. 和标准的HtmlHelper扩展方法用起来没太大区别 
  5. 容易使用 



在我们进入执行这个的细节之前如果你感觉这听起来像又回到了Web Form时代，那就错了。view helper仅仅是在创建HTML的时候起辅助作用，而不是将HTML进行抽象。我关心的只是HTML在页面中的显示效果以及使用javascript的行为更轻松.而不是textbox是否放入li中,当我需要创建一个textbox时，我只需在view中放入如下代码：
    
    
    <% Html.NewText("FirstName", "First name"); %> 

我想声明我仅仅是想将创建HTML延迟到另一个类中。使用View helper我可以轻松做到这一点。首先我们先来看标准的HtmlHelper扩展方法如何做到这一点.

Html helper有两种实现用法，大多数的使用方法都会如下：
    
    
    <%= Html.TextBox("FirstName") %> 

而还有一种用法和声明一个form元素很相似：
    
    
    <% using (Html.BeginForm()) { %> 
        <!--  Other elements here--> 
    <% } %> 

上面两种方法的主要区别是Html.TextBox仅仅返回一个string来注入到view中。这也是为什么使用<%=而不是标准的的代码块。而另一种以对象作为返回类型的方法更老练许多，比如，System.Web.Mvc.Html.MvcForm，这个对象放入using语句.对象被创建时一些HTML就会被注入到view中\(严格说：并不是对象创建时，但很接近\)还有一些事在对象被回收时将html注入view\(也就是碰到”\}”符号时\).使用这种方法的好处是可以在using语句之间插入代码。这使它的能力无疑比那些仅仅返回一个字符串注入页面的方式要强大许多。

所以，我选择第二种方法来实现我的View Helpers.所以HtmlHelper扩展方法会实现我创建的IViewObject接口对象。类图如下：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-01-05-viewhelper-asp-net-mvc-view-part1/viewhelper-asp-net-mvc-view-part1-1_thumb.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/ViewHelperAsp.netMVCviewpart1_E45A/1_2.jpg)

可以看到，IViewObject实现了System.IDisposable接口。这使实现如前面所提到和Html.BeginForm的使用方法类似所必须的。IViewObject有两个方法，StartView和EndView.这两个方法分别在对象创建时和对象回收时被调用.为了让这些对象的创建更加容易我创建了一个抽象类来处理:执行方法，回收对象和在合适的时候调用EndView方法。类图如下：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-01-05-viewhelper-asp-net-mvc-view-part1/viewhelper-asp-net-mvc-view-part1-2_thumb.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/ViewHelperAsp.netMVCviewpart1_E45A/2_2.jpg)

上图中的抽象类完整代码如下：
    
    
    public abstract class AbstractHtmlViewObject : IViewObject 
    { 
        private bool mDisposed; 
     
        public AbstractHtmlViewObject(ViewRequestContext requestContext, string name) 
        { 
            if (requestContext == null)  
            { throw new ArgumentNullException("requestContext"); } 
     
            ViewRequestContext = requestContext; 
            Name = name; 
        } 
     
        public IViewRequestContext RequestContext 
        { 
            get; 
            protected set; 
        } 
       #region IViewObject Members 
       public object Attributes { get; set; } 
       public string Name { get; set; } 
       public abstract void StartView(); 
       public abstract void EndView(); 
       #endregion 
       // based on System.Web.Mvc.HtmlHelper.GetModelStateValue 
       public object GetModelStateValue(string key, Type destinationType) 
       { 
           object result = null; 
           ModelState modelState; 
           if (ViewRequestContext.HtmlHelper.ViewData.ModelState.TryGetValue( 
               key, out modelState)) 
           { 
               result = modelState.Value.ConvertTo(destinationType, null); 
           } 
           return result; 
       } 
        #region IDisposable Members 
        public void Dispose() 
        { 
            Dispose(true); 
            GC.SuppressFinalize(this); 
        } 
     
        protected virtual void Dispose(bool disposing) 
        { 
            if (!mDisposed) 
            { 
                mDisposed = true; 
     
                EndView(); 
            } 
        } 
        #endregion 
    } 

如你所见上面AbstractHtmlViewObject对象不仅满足了最上面提到的列表（Ricky那段里），还包含了一些辅助类更容易扩展的东西。也就是它包含的一个属性：RequestContext，这个属性可以帮助我们很容易创建HTML和扩展方法GetModelStateValue,我们会在后面详细讲述GetModelStateValue的使用方法。我们会在后面讲述RequestContext的细节，这里我们先看看如何创建我们先前讨论的那个textbox。

\-------------------------------------------

待续…

原文链接：<http://mvcviewhelpers.codeplex.com/>

translated by [CareySon](http://www.cnblogs.com/careyson)
