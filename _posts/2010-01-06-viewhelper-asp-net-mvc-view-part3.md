---
layout: post
title: "【译】使用自定义ViewHelper来简化Asp.net MVC view的开发------part3"
date: 2010-01-06
categories: blog
tags: [博客园迁移]
---

接上篇…现在让我们开始讨论如何创建HtmlHelper扩展方法.

在前面我们说到了创建HtmlText类的方方面面。包括为HtmlText创建的扩展方法.这些扩展方法包括直接被View调用的那些扩展方法。下面代码展示了HtmlText的几种不同的构造函数:
    
    
    public static class HtmlHelperExtensions 
    { 
        #region Textbox 
        public static IViewObject NewText( 
            this HtmlHelper htmlHelper, string name) 
        { 
            return NewText(htmlHelper, name, null); 
        } 
         
        public static IViewObject NewText( 
            this HtmlHelper htmlHelper, string name, string labelText) 
        { 
            return NewText(htmlHelper, name, labelText, null); 
        } 
         
        public static IViewObject NewText( 
            this HtmlHelper htmlHelper, string name, string labelText, object value) 
        { 
            return NewText(htmlHelper, name, labelText, value, null, false, true, null); 
        } 
     
        public static IViewObject NewText( 
            this HtmlHelper htmlHelper, string name, string labelText, object value,  
            string validationMessage, bool @readonly, bool createLi, object attributes) 
        { 
            IViewObject viewObject = new HtmlText( 
                new ViewRequestContext(htmlHelper), name, labelText, value,  
                validationMessage, @readonly, createLi, attributes); 
            viewObject.StartView(); 
            return viewObject; 
        } 
        #endregion 
     
        //NOTE: SOME CONTENT OMITTED FROM THIS SNIPPET 
    } 

NewText方法有四个不同版本的重载,这些重载都属于System.Web.Mvc.HtmlHelper的扩展方法，只有最后一个方法用于真正的起作用，而其他的方法都是这个方法的封装以便让用户使用起来更简单.上面的代码中HtmlText对象通过传入适当的参数来初始化，而view是通过StartView方法来初始化，在StartView中被调用的HtmlText会返回合适的对象动态的将Html注入View.现在让我们来看看如何在view中使用这些方法。

前面我们已经创建了在View中可使用的HtmlText对象，现在就可以使用了。在前面我们提到，如果想要创建一个textbox来满足Ricky的标准，我必须写如下代码:
    
    
    <li> 
        <label for="FirstName">First name</label> 
        <%= Html.TextBox("FirstName") %> 
        <%= Html.ValidationMessage("FirstName", "*") %> 
    </li> 

现在通过使用HtmlHelper,我们可以把代码简化如下：
    
    
    <% Html.NewText("FirstName", "First name"); %> 

上面两种方法所生成的Html是完全相同的，我们实现了前面设定的目标。从今往后就可以使用这个Helper来简化Asp.net MVC view的开发了。上面代码中并没有用到EndView方法.下面我们来研究一个更复杂一些的HTML的构造—radio button,看是如何实现的

使用Asp.net MVC来创建一组radio button，代码一般如下：
    
    
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

上面代码是从AddContactClass.aspx view中节选的，所有代码可以从这篇文章的网站下载,上面代码中ContactController通过Model.GenderList属性来集中返回代码:
    
    
    public ActionResult AddContactClassic() 
    { 
        AddContactModel addModel = InternalGetInitialAddModel(); 
     
        return View(addModel); 
    } 
     
    private AddContactModel InternalGetInitialAddModel() 
    { 
        string maleString = Gender.Male.ToString(); 
        string femaleString = Gender.Female.ToString(); 
         IList<SelectListItem> genderRadioButtons = new List<SelectListItem>() 
        { 
            new SelectListItem { Text = maleString, Value = maleString }, 
            new SelectListItem { Text = femaleString, Value = femaleString } 
        }; 
     
        AddContactModel model = new AddContactModel { GenderList = genderRadioButtons }; 
     
        return model; 
    } 

生成的HTML效果图如下：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-01-06-viewhelper-asp-net-mvc-view-part3/viewhelper-asp-net-mvc-view-part3-1_thumb.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/ViewHelperAsp.netMVCviewpart3_61DD/1_2.jpg)

在上面创建radio button的代码中有很多掩盖了元素真实意图\(译者按：比如说为什么我们这么写HTML,是为了满足Ricky的标准吗？\)的部分，比如说：外层的div和内层的span是为了label而包裹文本.而如果我们需要一组radio button时只需要声明一下并指定相关的值那不是更爽吗？下面我们创建HtmlRadioButtonGroup view helper，它可以满足我们只声明并指定相关值就能创建出相应的html,使用HtmlRadioButtonGroup，我们可以将前面的radio button精简如下：
    
    
    <% Html.NewRadioButtonGroup("Gender", Model.GenderList); %> 

上面代码中，我们可以从更高的视角来创建Html,清楚的这段代码的作用而不是关注Html的细节。下面来创建一个替我们生成HTML的helper，也就是为:HtmlRadioButtonGroup类,下面代码展示了这个类唯一的构造函数和它的字段：
    
    
    private readonly List<SelectListItem> mSelectList; 
    private readonly bool mCreateLi; 
     
    public HtmlRadioButtonGroup( 
        ViewRequestContext requestContext, string name,  
        IEnumerable<SelectListItem> selectList, bool createLi, object attributes) 
        : base(requestContext, name) 
    { 
        mSelectList = new List<SelectListItem>(); 
        if (selectList != null) 
        { 
            mSelectList.AddRange(selectList); 
        } 
     
        mCreateLi = createLi; 
        Attributes = attributes; 
    }

看上去是不是和我们先前的HtmlText对象的构造器很像？它的构造函数为通过传参的方式将RequestContext变得可用。并且通过构造函数为所有的字段进行初始化，这也意味着这个类是在StartView方法中\(译者按：因为RequestContext方法在StartView中可以传入\)的,下面代码是StartView的完全版本:
    
    
    public override void StartView() 
    { 
        HttpResponseBase httpResponse = RequestContext.HttpResponse; 
     
        TagBuilder liTagBuilder = new TagBuilder("li"); 
        if (mCreateLi) 
        { 
            httpResponse.Write(liTagBuilder.ToString(TagRenderMode.StartTag)); 
        } 
     
        TagBuilder divTag = new TagBuilder("div"); 
        divTag.AddCssClass("option-group"); 
        divTag.MergeAttribute("name", Name); 
        if (Attributes != null) 
        { 
            divTag.MergeAttributes(new RouteValueDictionary(Attributes)); 
        } 
     
        TagBuilder labelTag = new TagBuilder("label"); 
        labelTag.MergeAttribute("for", Name); 
        labelTag.SetInnerText(Name); 
        httpResponse.Write(labelTag.ToString(TagRenderMode.Normal)); 
     
        httpResponse.Write(divTag.ToString(TagRenderMode.StartTag)); 
     
        // Write out the radio buttons, let the MVC Helper do the hard work here 
        foreach (SelectListItem item in this.mSelectList) 
        { 
            string text = !string.IsNullOrEmpty(item.Text) 
                            ? item.Text 
                            : item.Value; 
     
            httpResponse.Write(RequestContext.HtmlHelper.RadioButton( 
                Name, item.Value, item.Selected)); 
     
            // Note: Because we are using HtmlHelper.RadioButton the <input>  
            //       elements will have duplicate ids 
            //       See: http://forums.asp.net/t/1363177.aspx 
            //       In order to avoid this we could do this ourselves here 
            TagBuilder spanTag = new TagBuilder("span"); 
            spanTag.SetInnerText(text);        
             httpResponse.Write(spanTag.ToString(TagRenderMode.Normal)); 
        } 
     
        httpResponse.Write(divTag.ToString(TagRenderMode.EndTag)); 
     
        if (this.mCreateLi) 
        { 
            httpResponse.Write(liTagBuilder.ToString(TagRenderMode.EndTag)); 
        } 
    } 

这里的想法和HtmlText类如初一撤，那就是：所有的HTML代码都在StartView方法中生成。因此这里StartView方法创建了一些HTML tag,并遍历mSelectList中的元素并通过Asp.net MVC自带的RadioButton扩展方法为每一个元素生成一个RadioButton。在重用这些方法时最好先重写这些方法（译者按：看上面代码注释）。

从上面代码中的注释可以看出，使用HtmlHelper.RadioButton扩展方法有一个明显的bug,就是id和name用的是同一个值，这里因为name属性本来就应该为RadioButton设置成相同的这样他们便可以逻辑上连成一组，但是id属性是每个元素唯一拥有，这里解决这个bug的方法是不用这个方法，但在这里为了简单起见我们先使用这个方法.上面创建的两个Html helper对象都没有用到EndView方法，你可以已经开怀疑这个方法为什么存在，在接下来的HtmlFieldSet的Helper我会给你展示EndView的用途

\-------------------------------------------

待续…

原文链接：<http://mvcviewhelpers.codeplex.com/>

translated by [CareySon](http://www.cnblogs.com/careyson)
