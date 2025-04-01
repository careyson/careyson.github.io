---
layout: post
title: "【译】使用自定义ViewHelper来简化Asp.net MVC view的开发------part5(完)"
date: 2010-01-06
categories: blog
tags: [博客园迁移]
---

接上文..前面我们已经创建好了HtmlFieldSet，现在，为了让HtmlHelper的扩展方法可以使用这个类，还需要创建一个方法：NewHtmlFieldSet
    
    
    public static IViewObject NewHtmlFieldSet( 
        this HtmlHelper htmlhelper, string name, string title, object attributes) 
    { 
        IViewObject viewObject = new HtmlFieldSet( 
            new ViewRequestContext(htmlhelper), name, title, attributes); 
        viewObject.StartView(); 
        return viewObject; 
    } 

这个方法的实现和前面所提到的那些没有上面不同，都是传入相应参数并返回view object,在View被初始化时返回这个对象，View首先在初始化时使用返回的View object,更确切点说，返回的IViewObject会在using语句中被view使用，例子如下：
    
    
    <% using (Html.NewHtmlFieldset("FieldsetName", "My Fieldset", null)) 
       { %> 
        <li> 
          <label for="FirstName">FirstName</label> 
          <span id="FirstName"><%= Html.Encode(Model.FirstName) %></span>  
        </li> 
    <% } %> 

对应生成的HTML代码如下：
    
    
    <fieldset name="FieldsetName"> 
      <legend>My Fieldset</legend> 
      <ol> 
          <li> 
            <label for="FirstName">FirstName</label> 
            <span id="FirstName">Sayed</span>  
          </li> 
      </ol> 
    </fieldset> 

EndView方法输出了最后的三个结尾标签\(</li>，</ol>，</fieldset>\)，达到了我们的预期，现在就可以使用view helper来创建fieldset以及包含在内的legend,以便达到更好的可理解和可维护性。下面来看view helper是如何简化view的开发的。

这篇文章中附带的示例代码时全功能版本，每一个页面都有两个版本-使用view helper和不使用view helper.不适用view helper的版本全部手动创建HTML,而使用view helper的版本包括了我们先前创建的3个view helper，让我们来进行简单的比较，从源码中找到AddContactClassic.aspx
    
    
    <%@ Page Title="" Language="C#" MasterPageFile="~/Views/Shared/Site.Master"  
      Inherits="System.Web.Mvc.ViewPage<Sedodream.Web.ViewHelper.Models.AddContactModel>" 
    %> 
     
    <%@ Import Namespace="Sedodream.Web.Common.Contact" %> 
     
    <asp:Content ID="Content1" ContentPlaceHolderID="TitleContent" runat="server"> 
      Add Contact Classic 
    </asp:Content> 
     
    <asp:Content ID="Content2" ContentPlaceHolderID="MainContent" runat="server"> 
      <h2>Add Contact Classic</h2> 
      <%= Html.ValidationSummary("Errors exist") %> 
       
      <ol>     <li> 
          <span class="success-message"><%= ViewData["SuccessMessage"]%></span> 
          </li> 
      </ol> 
      <% using (Html.BeginForm()) 
         { %> 
          <fieldset> 
            <legend>Account Information</legend> 
            <ol> 
              <li> 
                <label for="FirstName">First name</label> 
                <%= Html.TextBox("FirstName") %> 
                <%= Html.ValidationMessage("FirstName", "*") %> 
              </li> 
              <li> 
                <label for="LastName">Last name</label> 
                <%= Html.TextBox("LastName") %> 
                <%= Html.ValidationMessage("LastName", "*") %> 
              </li> 
              <li> 
                <label for="Email">Email</label> 
                <%= Html.TextBox("Email")%> 
                <%= Html.ValidationMessage("Email", "*")%> 
              </li> 
              <li> 
                <label for="Phone">Phone</label> 
                <%= Html.TextBox("Phone")%> 
                <%= Html.ValidationMessage("Phone", "*")%> 
              </li> 
              <li> 
                <div class="option-group" id="GenderContainer"> 
                  <label for="Gender">Gender</label> 
                  <% foreach (SelectListItem item in Model.GenderList) 
                     { %> 
                       <%= Html.RadioButton(item.Text, item.Value)%> 
                       <span><%= item.Text%></span> 
                  <% } %> 
                </div> 
              </li> 
               
              <li> 
                <input type="submit" value="Add contact" /> 
              </li> 
            </ol> 
          </fieldset> 
      <% } %> 
    </asp:Content> 

上面代码尽管简单，但仍然包含多达59行代码，而且看起来十分丑陋，下面的版本是使用我们自定义的view helper,让我们来看看包含在AddContactNew.aspx内的新版本：
    
    
    <%@ Page 
    Inherits="System.Web.Mvc.ViewPage<Sedodream.Web.ViewHelper.Models.AddContactModel>" 
        Language="C#" MasterPageFile="~/Views/Shared/Site.Master" Title="" %> 
     
    <%@ Import Namespace="Sedodream.Web.Common.View" %> 
     
    <asp:Content ID="Content1" ContentPlaceHolderID="TitleContent" runat="server"> 
      Add Contact New 
    </asp:Content> 
     
    <asp:Content ID="Content2" ContentPlaceHolderID="MainContent" runat="server"> 
     
        <h2>Add Contact New</h2> 
         
        <%= Html.ValidationSummary("Errors exist") %> 
         
        <ol> 
          <li> 
            <span class="success-message"><%= Model.SuccessMessage %></span> 
          </li> 
        </ol> 
        <% using (Html.BeginForm()) 
           { %> 
        <fieldset> 
            <legend>Account Information</legend> 
            <ol> 
                <% Html.NewText("FirstName", "First name"); %> 
                <% Html.NewText("LastName", "Last name"); %> 
                <% Html.NewText("Email", "Email"); %> 
                <% Html.NewText("Phone", "Phone"); %> 
                <% Html.NewRadioButtonGroup("Gender", Model.GenderList); %> 
                 
                <li> 
                    <input type="submit" value="Add contact" /> 
                </li> 
            </ol> 
         
        </fieldset> 
        <% } %> 
    </asp:Content> 

使用view helper的版本html大大减少\(只有39行\)而且更容易理解，这里需要注意view引入了Sedodream.Web.Common.View命名空间，这使view helper扩展方法所必须的.Sedodream.Web.Common.View命名空间包含在另一个程序集中，这样更方便你在整个小组内进行分发，使用View helper所带来的可理解性只是使用它所带来好处的其中之一，它还会带来以下好处:

  1. View更清爽，更容易理解
  2. 小组内遵循某些标准更容易
  3. 在修改时需要改变的地方更少
  4. 可利用回传的model state辅助生成代码



在前面我们提到了GetModelStateValue方法的使用。这个方法用于给HTML元素赋上它自己从View里回传的值,而在view helper内可以给生成的html元素赋值.下面代码片段是System.Web.Mvc.Html.InputExtensions源文件中的一部分，这里用来展示GetModelStateValue的用法：
    
    
    case InputType.Radio: 
        if (!usedModelState) { 
            string modelStateValue = htmlHelper.GetModelStateValue( 
                name, typeof(string)) as string; 
            if (modelStateValue != null) { 
                isChecked = String.Equals( 
                    modelStateValue, valueParameter, StringComparison.Ordinal); 
                usedModelState = true; 
            } 
        } 

上面代码先检查model state来看radio button是否被创建,如果radio button已经存在就可以查看radio button是否已经被选中，当你创建自定义view helper时，你最好也在合适的地方支持类似\(可以获取当前html的元素\)的功能。前面的HtmlText view helper已经说明了这一点。

文章到此已经将创建自定义view helper的方方面面都讲到了。

\-------------------------------------------

shit live writer把part4给覆盖了没有保存，找时间我重新翻译下

全文完

原文链接：<http://mvcviewhelpers.codeplex.com/>

translated by [CareySon](http://www.cnblogs.com/careyson)
