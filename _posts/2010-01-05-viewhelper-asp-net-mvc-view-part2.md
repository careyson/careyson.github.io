---
layout: post
title: "【译】使用自定义ViewHelper来简化Asp.net MVC view的开发------part2"
date: 2010-01-05
categories: blog
tags: [博客园迁移]
---

接上篇…首先让我们来看如何创建一个我们先前讨论的textbox

我们已经知道需要创建的textbox有一个文本值与之对应：

  1. 文本值在label标签中 
  2. 可选的值放在Textbox中 
  3. 可选的验证信息（validation message） 



如果上面3个条件都能满足，肯定也能满足我们在part1里的那5个条件.还有一些锦上添花的是可以通过属性来指定textbox是否包裹在li标签内以及textbox是否是readonly模式.这样我们便能更好的在view page中代码复用。下面的代码包含所有HtmlText\(译者按:继承AbstractHtmlViewObject对象，在part1的类图中\)对象所有的属性:
    
    
    private readonly string mLabelText; 
    private readonly bool mCreateLabel; 
    private readonly object mValue; 
    private readonly string mValidationMessage; 
    private readonly bool mCreateValidationMessage; 
    private readonly bool mCreateLi; 
    private readonly bool mReadonly; 
     
    public HtmlText( 
        ViewRequestContext requestContext, string name, string labelText, objec
        string validationMessage, bool @readonly, bool createLi, object attribu
        : base(requestContext, name) 
    { 
        mLabelText = labelText; 
        mCreateLabel = !string.IsNullOrEmpty(mLabelText); 
        mValidationMessage = validationMessage; 
        mCreateValidationMessage = !string.IsNullOrEmpty(validationMessage); 
        mCreateLi = createLi; 
        mReadonly = @readonly; 
        Attributes = attributes; 
     
        object valueToAssign = value; 
        if (valueToAssign == null) 
        { 
            // see if the ModelState has a value for this 
            valueToAssign = GetModelStateValue(name, typeof(string)); 
        } 
     
        mValue = valueToAssign; 
    } 

在构造函数中，我们我们存入一系列私有变量中并初始化了会在StartView方法内使用的一个bool类型,除此之外你可以发现这里开始使用GetModelStateValue方法.目前为止我们先不过多讨论这个方法,这个方法会在后面提到。在参数传入构造器之前我们注意到:

  1. value参数的类型是object 
  2. object类型的attributes参数被传入 



之所以把Value参数定义为object类型是因为这样可以使用户更容易使用并且和ASP.Net MVC Helpers的执行方式保持一致。attributes参数可以被调用者来扩展生成的HTML。比如说，你想将textbox的maxlength属性设置为5，你只需要传入匿名类型”new \{maxlength=5\}“.input标签会将这个匿名类型转换为HTML属性maxlength=5.这同时也符合Asp.net MVC中HTML Helper现有扩展方法的使用方式.每一个View helper对象都应该支持这种行为以便具有更大的灵活性.在这个类中剩下的两个方法就是从父类继承来的StartView和EndView方法了.

StartView和EndView的定义如下:
    
    
    public override void StartView() 
    { 
        HttpResponseBase httpResponse = RequestContext.HttpResponse; 
     
        TagBuilder htmlLiTagBuilder = new TagBuilder("li"); 
        if (mCreateLi) 
        { 
            httpResponse.Write(htmlLiTagBuilder.ToString(TagRenderMode.StartTag)); 
        } 
     
        // write out label if provided 
        if (mCreateLabel) 
        { 
            TagBuilder labelTag = new TagBuilder("label"); 
            labelTag.Attributes.Add("for", Name); 
            labelTag.SetInnerText(mLabelText); 
            httpResponse.Write(labelTag.ToString(TagRenderMode.Normal)); 
        } 
     
        string stringValue = string.Empty; 
        if (this.mValue != null) 
        { 
            stringValue = Convert.ToString(this.mValue, CultureInfo.CurrentCulture); 
        } 
     
        if (this.mReadonly) 
        { 
            TagBuilder textTag = new TagBuilder("span");         
            textTag.AddCssClass("readonly-text"); 
            textTag.SetInnerText( 
                Convert.ToString(this.mValue, CultureInfo.CurrentCulture)); 
            httpResponse.Write(textTag.ToString(TagRenderMode.Normal)); 
        } 
        else 
        { 
            // Use MVC helpers to create the actual text box 
            httpResponse.Write(RequestContext.HtmlHelper.TextBox( 
                Name, this.mValue, Attributes)); 
        } 
     
        if (this.mCreateLi) 
        { 
            httpResponse.Write(htmlLiTagBuilder.ToString(TagRenderMode.EndTag)); 
        } 
    } 
    public override void EndView() 
    { 
        // Not needed for this element 
    } 

在StartView方法中有很多值得注意的地方，让我们逐个讨论。首先是我们使用System.Web.Mvc.TagBuilder来生成HTML,而不是直接写HTML标签。TagBuilder只能在Asp.net MVC中使用并且我推荐在生成HTML中必须使用TagBuilder而不是直接写HTML标签,下面是TagBuilder的类图:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-01-05-viewhelper-asp-net-mvc-view-part2/viewhelper-asp-net-mvc-view-part2-1_thumb.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/ViewHelperAsp.netMVCviewpart2_10B8A/1_2.jpg)

下表是TagBuilder中一些方法的说明:

名称 | 描述  
---|---  
AddCssClass | 加入css的class名称，如果class已经存在，则后来加入的会和原来的class一起生效  
MergeAttribute | 这个方法用于添加或者更新tag的属性，这个方法有一个接受replaceExisting参数的重载，默认情况下已经定义的属性不会被重载。  
MergeAttributes | 同上，只是可以在一个方法内添加或更新所有属性.  
SetInnerText | 设置标签内的文本  
ToString | 被重载。用于生成相应的html代码，TagRenderMode枚举类型会控制如何生成HTML标签.  
  
在上面表格的ToString那行，TagRenderMode枚举用于控制TagBuilder生成HTML标签的方式，TagRenderModel如下所示：

TagRenderModel | 结果示例  
---|---  
Normal | <div name=”Sample01”>Some content here</div>  
StartTag | <div name=”Sample01”>  
EndTag | </div>  
SelfClosing | <div name=”Sample01” />  
|   
  
根据你想创建的HTML标签和你如何使用它，你会发现使用TagRenderModel可以创建出任何你想创建出的HTML.在前面提到的StartView方法内你会发现TagRenderModel被依据不同的条件设置成StartTag,Normal和EndTag等不同的的类型.如果你给InnerHTML属性赋值并用StartTag和EndTag生成它你必须要记住InnerHtml不会被自动生成，你还必须显式的使用InnerHtml属性本身。下面我们来讨论如何创建HtmlHelper扩展方法。

\-------------------------------------------

待续…

原文链接：<http://mvcviewhelpers.codeplex.com/>

translated by [CareySon](http://www.cnblogs.com/careyson)
