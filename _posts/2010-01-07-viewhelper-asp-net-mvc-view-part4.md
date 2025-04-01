---
layout: post
title: "【译】使用自定义ViewHelper来简化Asp.net MVC view的开发------part4"
date: 2010-01-07
categories: blog
tags: [博客园迁移]
---

接上篇，我们下面通过HtmlFiledSet helper来展示何时使用EndView\(\): 

如果你用Asp.net已经有一段时间了，那使用Html.BeginForm helper来创建HTML form标签的方式会让你觉得有点怪.当你创建一个新的Asp.net mvc项目后，在View里的ChangePassword.aspx会默认被创建，这个页面使用了Html.BeginForm helper,下面是使用这个helper的代码段: 
    
    
    <% using (Html.BeginForm()) { %> 
        <div> 
            <fieldset> 
                <legend>Account Information</legend> 
                <p> 
                    <label for="currentPassword">Current password:</label> 
                    <%= Html.Password("currentPassword") %> 
                    <%= Html.ValidationMessage("currentPassword") %> 
                </p> 
                <p> 
                    <label for="newPassword">New password:</label> 
                    <%= Html.Password("newPassword") %> 
                    <%= Html.ValidationMessage("newPassword") %> 
                </p> 
                <p>                 <label for="confirmPassword">Confirm new password:</label> 
                    <%= Html.Password("confirmPassword") %> 
                    <%= Html.ValidationMessage("confirmPassword") %> 
                </p> 
                <p> 
                    <input type="submit" value="Change Password" /> 
                </p> 
            </fieldset> 
        </div> 
    <% } %> 

上面代码中你会发现Html.BeginForm的使用和<%=Html.Password\(“currentPassword”\) %>的使用不尽相同，也就是Html.BeginForm在using语句中被调用,这点很有意思，让我先来看看上面代码段生成后的Html,如下： 
    
    
    <form  
      action="/Account/LogOn?ReturnUrl=%2fAccount%2fChangePassword"  
      method="post"> 
      <div> 
        <fieldset> 
          <legend>Account Information</legend> 
          <p> 
            <label for="username">Username:</label> 
            <input id="username" name="username" type="text" value="" />   
          </p> 
          <p> 
            <label for="password">Password:</label> 
            <input id="password" name="password" type="password" />   
          </p> 
          <p> 
            <input id="rememberMe" name="rememberMe" type="checkbox" value="true" /> 
            <input name="rememberMe" type="hidden" value="false" /> 
            <label class="inline" for="rememberMe">Remember me?</label> 
          </p> 
          <p> 
            <input type="submit" value="Log On" /> 
          </p> 
        </fieldset> 
      </div> 
    </form> 

比较<%= Html.Password\("currentPassword"\) %> 语句和Html.BeginForm所生成的HTML代码你会发现password那段仅仅仅仅将调用password扩展方法变成对应的Html，而BeginForm调用HTML扩展方法来注入form的开始标签，<form…>，和using语句结束时\(“\}”\)注入标签<./form>.这种方式十分方便，因为我们可以一方面使用view helper创建合适的form标签，另一方面在form标签内插入任何我们想插入的html.这种方法的工作原理是当你调用Html.BeginForm方法并返回MvcForm类型的对象,这个对象在using语句中所以当对象被回收\(译者按：也就是Dispose\)的时候，也就是执行到结尾的”<% \} %>”时，关闭标签</form>将会被写入到View中.下面是Dispose方法的实现: 
    
    
    public void Dispose() { 
        Dispose(true /* disposing */); 
        GC.SuppressFinalize(this); 
    } 
     
    protected virtual void Dispose(bool disposing) { 
        if (!_disposed) { 
            _disposed = true; 
            _httpResponse.Write("</form>"); 
        } 
    } 

我们用相似的方法来实现HtmlFieldSet: 

从这篇文章附带的代码中有一个”DetailsClassic.aspx”页面中，一些字段包含于fieldset元素中，具体代码如下： 
    
    
    <fieldset class="details-field-group" name="Details"> 
      <legend>Details</legend> 
      <ol> 
        <li> 
          <label for="FirstName">FirstName</label> 
          <span id="FirstName"> 
            <%= Html.Encode(Model.FirstName) %></span>  
        </li> 
        <li> 
          <label for="LastName">LastName</label> 
          <span id="LastName"><%= Html.Encode(Model.LastName) %></span> 
        </li> 
        <li> 
          <label for="Email">Email</label> 
          <span id="Email"><%= Html.Encode(Model.Email) %></span> 
        </li> 
        <li> 
          <label for="Phone">Phone</label> 
          <span id="Phone"><%= Html.Encode(Model.Phone) %></span> 
        </li> 
        <li> 
          <label for="Gender">Gender</label> 
          <span id="Gender"><%= Html.Encode(Model.Gender) %></span> 
        </li> 
      </ol> 
    </fieldset> 

如果能用一个view helper来创建下面所有的html标签，那会惬意很多： 

  * fieldset的开始标记 
  * legend标签 
  * ol的开始标签 
  * ol的结束标签 
  * fieldset的结束标签 



如果能用view helper来处理这些，那上面那段代码无疑会简单很多,尤其再加上使用Html.Text标签来代替上面的text域。让我们开始做到这一点，首先创建一个实现IViewObject接口的类，命名为HtmlFieldSet类并继承与AbstractHtmlViewObject，整个类的代码附下： 
    
    
    public class HtmlFieldset : AbstractHtmlViewObject 
    { 
        private readonly string mTitle; 
     
        public HtmlFieldset( 
            ViewRequestContext requestContext, string name,  
            string title, object attributes) 
            : base(requestContext, name) 
        { 
            mTitle = title; 
            Attributes = attributes; 
        } 
     
        private TagBuilder FieldsetTag { get; set; } 
     
        private TagBuilder OlTag { get; set; } 
     
        public override void StartView() 
        { 
            HttpResponseBase httpResponse = RequestContext.HttpResponse; 
     
            FieldsetTag = new TagBuilder("fieldset"); 
     
            // apply any Attributes passed in 
            if (Attributes != null) 
            { 
                FieldsetTag.MergeAttributes(new RouteValueDictionary(Attributes)); 
            }  
            // The Name property should override any passed into the Attributes 
            FieldsetTag.MergeAttribute("name", Name, true); 
     
            httpResponse.Write(FieldsetTag.ToString(TagRenderMode.StartTag)); 
     
            if (!string.IsNullOrEmpty(mTitle)) 
            { 
                TagBuilder legendTag = new TagBuilder("legend"); 
                legendTag.SetInnerText(mTitle); 
                httpResponse.Write(legendTag.ToString(TagRenderMode.Normal)); 
            } 
     
            OlTag = new TagBuilder("ol"); 
            httpResponse.Write(OlTag.ToString(TagRenderMode.StartTag)); 
        } 
     
        public override void EndView() 
        { 
            HttpResponseBase httpResponse = RequestContext.HttpResponse; 
     
            httpResponse.Write(OlTag.ToString(TagRenderMode.EndTag)); 
            httpResponse.Write(FieldsetTag.ToString(TagRenderMode.EndTag)); 
        } 
    } 

这个类的实现和其它的view对象没什么不同，除了EndView方法，在这里我们需要EndView方法来生成必须的结束标记。当然我们也可以使用EndView来生成任何需要的HTML,在这里我们仅是用它生成结束标记。 

\------------------------------------------- 

待续… 

原文链接：<http://mvcviewhelpers.codeplex.com/>

translated by [CareySon](http://www.cnblogs.com/careyson)
