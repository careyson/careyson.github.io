---
layout: post
title: "【译】Asp.net MVC并不仅仅只是Linq to SQL"
date: 2010-03-03
categories: blog
tags: [博客园迁移]
---

很多Asp.net的教程中的示例代码使用的数据访问方法是Linq to Sql或是Entity Framework。我在[www.asp.net](http://www.asp.net)的论坛上看到很多关于讨论是否有其他替代的数据库访问方式，回答是：当然有。这篇文章就讲述了使用Ado.Net作为数据访问层来实现一个典型的增删查改程序。

由于是以练习作为目的，那我就不妨借用Spaanjaar’s 的N层构架文章（[Building Layered Web Applications with Microsoft ASP.NET 2.0](http://imar.spaanjaars.com/QuickDocId.aspx?quickdoc=416).）的构架方式。我强烈推荐你阅读他的系列文章，如果嫌太长起码也得看完前两部分，这样就能对N-Layer构架有个基本的认识。N-Layer构架的三个关键层分别为:业务对象层，业务逻辑层和数据访问层。而其数据访问层会几乎不加改变的包含在本文的MVC项目中，Spaanjaar的文件详细描述了各个层是如何组织的。这篇文章仅仅讲述各个层所扮演的角色，但是不会深入到代码的细节中。

首先，我们来看Imar提供的程序，这是一个具有典型增删查改的程序,这个程序允许用户管理联系人，包括联系人的地址，电话，email。它能增，删，查，改任何实体。

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-03-03-asp-net-mvc-linq-to-sql/asp-net-mvc-linq-to-sql-nlayermvc1.gif)

程序内包括的实体有:ContactPersons, PhoneNumbers, Addresses EmailAddresses.他们都隶属于程序的业务对象（BO）层。上述的每一个类都包含可以获取或者赋值的属性，但并不包含任何方法。而所有方法存放于业务逻辑层（BLL）中的对应类中。在业务对象层和业务逻辑层的实体和实体manger是一对一的关系，在业务逻辑层中类包含的方法都会返回业务对象层\(BO\)的实例，或是实例集合，或者保存实例（更新或是添加），或是删除实例。业务逻辑层（BLL）中也可以包含一些业务规则验证，安全性检查的代码。但在本篇文章为了简便起见，就不添加这些了。如果你对业务规则和安全性有兴趣的话，可以去看Imar文章的[6 part series](http://imar.spaanjaars.com/QuickDocId.aspx?quickdoc=476)。

最后一层是数据访问层\(DAL\)，同样，DAL层的类也和业务逻辑层（BLL）内的类有着一对一的关系，在BLL层的类中会调用相关DAL层中的方法。而在这些层中，只有DAL层需要知道利用什么技术（linq,entity framework..）保存业务实体。在本例中，使用Sql Server Express数据库和Ado.net。而这样分层的思想是如果你需要更换数据源（XML，oracle，更或者是Web Service甚至是Linq to Sql或者其他ORM框架），因为DAL层给BLL层暴漏的方法的签名是一致的，所以只需要更换DAL层即可。而为了保证所有DAL的实现有着同样的签名，则利用接口即可。但我想或许是未来帖子中讨论的话题了吧。

### **MVC构架**

已经有很多优秀的文章中已经探讨了MVC程序的构架，所以本篇文章就不再累述相关细节了。如果想要了解更多，我推荐访问[Asp.net MVC官方站点](http://www.asp.net/mvc).简单二代说，M代表Model，也是包含BO,BLL,DAL的地方，V代表View，也是UI相关开发的部分，或者说是用户看到的部分，C是Controller的简写，也是控制用户请求与程序回复的部分。如果用户点击了一个指向特定地址的按钮，请求会和Controller的Action（类的方法）进行匹配，而Action负责处理请求，并返回响应。通常情况下是一个新的View，或者是更新现有的View。

下面用Visual Studio创建一个MVC应用程序并删除默认的View和Controller，然后将Imar的程序中的Bo,Bll和DAL复制到这个MVC程序的Model内，我还复制了响应的数据库文件和Style.css。

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-03-03-asp-net-mvc-linq-to-sql/asp-net-mvc-linq-to-sql-nlayermvc2.gif)

我还做了一些其他的修改，把数据库连接字符串添加到Web.Config中。除此之外，我还将复制过来的代码的命名空间做了响应的调整并把DAL层的代码升级到了3.0.虽然这并不是必须的。做完这些，我按Ctrl+Shift+F5来测试是否编译成功。------------------

### **Controller**

我添加了4个Controller\(Visual Studio附带的默认Controller已经被删除\)，和四个实体类相匹配。它们分别为：ContactController, PhoneController, AddressController and EmailController。

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-03-03-asp-net-mvc-linq-to-sql/asp-net-mvc-linq-to-sql-nlayermvc3.gif)

每个Controller都含有四个Action：List, Add, Edit and Delete。首先需要在Global.exe中为这些Action注册这些路由。
    
    
    public static void RegisterRoutes(RouteCollection routes)
    {
      routes.IgnoreRoute("{resource}.axd/{*pathInfo}");
    
      routes.MapRoute(
          "Default",                                              
          "{controller}/{action}/{id}",                           
          new { controller = "Contact", action = "List", id = "" }  
      );
    }

  
默认的View会显示所有联系人，BLL层中的ContactPersonManager类内的GetList（）方法会获取所有联系人的数据，响应的List\(\) Action代码如下：
    
    
    public ActionResult List()
    {
      var model = ContactPersonManager.GetList();
      return View(model);
    }

  


### **强类型View**

整个实例代码中，我都会使用强类型的View，因为这样不仅可以使用intellisense\(智能提示\)的好处，还不必依赖于使用String作为索引值的ViewData。为了让代码更加有序，我添加了一些命名空间到web.config中的<namespaces>节点，这些都是我用来替换Imar代码的方式：
    
    
    <namespaces>
    <add namespace="System.Web.Mvc"/>
    <add namespace="System.Web.Mvc.Ajax"/>
    <add namespace="System.Web.Mvc.Html"/>
    <add namespace="System.Web.Routing"/>
    <add namespace="System.Linq"/>
    <add namespace="System.Collections.Generic"/>
    <add namespace="ContactManagerMVC.Views.ViewModels"/>
    <add namespace="ContactManagerMVC.Models.BusinessObject"/>
    <add namespace="ContactManagerMVC.Models.BusinessObject.Collections"/>
    <add namespace="ContactManagerMVC.Models.BusinessLogic"/>
    <add namespace="ContactManagerMVC.Models.DataAccess"/>
    <add namespace="ContactManagerMVC.Models.Enums"/>
    </namespaces>

上面代码意味着我可以在程序的任何地方访问上述命名空间。上面GetList（）方法返回的类型是ContactPersonList,这个类型是ContactPerson对象的集合，在显示List的View中的Page声明如下：
    
    
    <%@ Page Title="" Language="C#" MasterPageFile="~/Views/Shared/Site.Master" 
        Inherits="System.Web.Mvc.ViewPage<ContactPersonList>" %>

  


我想你已经注意到了我使用了MasterPage,利用MasterPage,我借用了从Imar实例代码中的Css文件。用于显示ContactPerson对象的HTML如下：
    
    
    <table class="table">
        <tr>
          <th scope="col">Id</th>
          <th scope="col">Full Name</th>
          <th scope="col">Date of Birth</th>
          <th scope="col">Type</th>
          <th scope="col">&nbsp;</th>
          <th scope="col">&nbsp;</th>
          <th scope="col">&nbsp;</th>
          <th scope="col">&nbsp;</th>
          <th scope="col">&nbsp;</th>  
        </tr>
        <%
          if (Model != null)
          {
            foreach (var person in Model)
            {%>
        <tr>
          <td><%= person.Id %></td>
          <td><%= person.FullName %></td>
          <td><%= person.DateOfBirth.ToString("d") %></td>
          <td><%= person.Type %></td>
          <td title="address/list" class="link">Addresses</td>
          <td title="email/list" class="link">Email</td>
          <td title="phone/list" class="link">Phone Numbers</td>
          <td title="contact/edit" class="link">Edit</td>
          <td title="contact/delete" class="link">Delete</td>
        </tr>
        <%
            }
          }else{%>
        <tr>
          <td colspan="9">No Contacts Yet</td>
        </tr>  
         <% }%>
      </table>

  


  
我想你已经能发现强类型View的好处了吧，Model的类型是ContactPersonList,所以你可以任意使用ContactPersonList的属性而不用强制转换，而强制转换错误只有在运行时才能被发现，所以这样省了不少事。

在做Html时，我小小的作弊了一下，我本可以使用vs对list自动生成的view,但我没有。因为我需要和Imar的css文件相匹配的html.所以我运行了imar的程序，在浏览器中查看源代码，并把生成的html复制下来，imar使用GridView来生成列表，所以CSS会在运行时嵌入到html代码中。我将这些css代码移到一个外部的css文件中。并给<th>和<td>元素添加了一些额外样式，你可以在代码的下载链接中找到。

我还未一些表格的单元格添加了title属性。这些包含了访问其他action的链接。我希望用户在浏览电话本或者编辑或者删除电话本时页面不会post back,换句话说，我希望我的网站是ajax的。而title属性就发挥作用了。而“。link”这个css选择符可以让普通的文本看起来像超链接，也就是有下划线和鼠标hover时出现小手。

### **jQuery AJax**

在我们深入实现ajax功能的相关代码之前，下面3行代码是需要加入到html中：

  

    
    
    <input type="button" id="addContact" name="addContact" value="Add Contact" />
    <div id="details"></div>
    <div id="dialog" title="Confirmation Required">Are you sure about this?</div>

  


第一行代码的作用是一个允许用户添加新联系人的按钮，第二行代码是一个空div,方便后面显示信息，第三行代码是jQuery modal 提示验证对话框的一部分，用于提示用户是否删除一条记录。

还需要在页面中添加3个js文件，第一个是主要的jQuery文件，其他两个分别是jQuery UI的核心js,以及date picker和modal dialog部分的js
    
    
    <script src="../../Scripts/jquery-1.3.2.min.js" type="text/javascript"></script>
    <script src="../../Scripts/ui.core.min.js" type="text/javascript"></script>
    <script src="../../Scripts/jquery-ui.min.js" type="text/javascript"></script>

下面是我们生成后的列表显示视图以及完全的js代码：

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-03-03-asp-net-mvc-linq-to-sql/asp-net-mvc-linq-to-sql-nlayermvc4.gif)
    
    
    <script type="text/javascript">
      $(function() {
        // row colours
        $('tr:even').css('background-color', '#EFF3FB');
        $('tr:odd').css('background-color', '#FFFFFF');
        // selected row managment
        $('tr').click(function() {
          $('tr').each(function() {
            $(this).removeClass('SelectedRowStyle');
          });
          $(this).addClass('SelectedRowStyle');
        }); 
        // hide the dialog div
        $('#dialog').hide();
        // set up ajax to prevent caching of results in IE
        $.ajaxSetup({ cache: false });
        // add an onclick handler to items with the "link" css class
        $('.link').live('click', function(event) {
          var id = $.trim($('td:first', $(this).parents('tr')).text());
          var loc = $(this).attr('title');
          // check to ensure the link is not a delete link
          if (loc.lastIndexOf('delete') == -1) {
            $.get(loc + '/' + id, function(data) {
              $('#details').html(data);
            });
          // if it is, show the modal dialog   
          } else {
            $('#dialog').dialog({
              buttons: {
                'Confirm': function() {
                  window.location.href = loc + '/' + id;
                },
                'Cancel': function() {
                  $(this).dialog('close');
                }
              }
            }); 
            $('#dialog').dialog('open');
            }
          }); 
          // add an onclick event handler to the add contact button
          $('#addContact').click(function() {
            $.get('Contact/Add', function(data) {
              $('#details').html(data);
            });
          }); 
        });
    </script>

上面代码看起来让人望而却步，但实际上，使用jQuery，这非常简单。并且在上面代码中我多处加入了注释，代码一开始是用js代码是替换了数据源控件默认呈现出来的隔行变色的颜色。然后我加入了使点击行点击时可以变色的代码。然后下面的代码是防止IE对页面进行缓存。如果不禁止了IE缓存，你会为执行编辑或者删除以后，数据库改变了但页面却没有发生变化而撞墙的。

接下来的代码更有趣了，依靠live\(\)方法可以确$选择器中所有匹配的元素都被附加了相应的事件，无论元素当前是否存在于页面中。比如说，当你点击了Addresses链接，相应的结果就会在另一个表中出现：

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-03-03-asp-net-mvc-linq-to-sql/asp-net-mvc-linq-to-sql-nlayermvc5.gif)

上图中可以看出表中包含编辑和删除链接，如果不使用live\(\)方法，相应的链接就不会被附加事件。所有具有class为link的元素都会被委派上click事件。这个事件会首先获取到当前条目的id.以ContactPerson表为例，这个id就是ContactPersonId.在相应的子表中，则id会是电话号码或者是email地址。这些都是需要传递给controller action作为参数进行编辑，删除，或者显示的。

你现在可以看出为什么我为每个单元格加上title属性了吧。title属性包含相关的route信息，而完全的url则把id附加到route作为url.然后，上面js会做一个检查，来看route信息内是否包含delete,如果包含delelte,则弹出一个对话框来提示用户是否要删除。看，是不是很简单？

最后，代码会为添加联系人按钮添加click事件，在文章的下部分我们再进行讨论

### **添加联系人以及自定义View Models**

使用Asp.net添加一条记录时,通常的做法是提供一个包含一系列输入框的form.对于ContactPerson类的大多属性来说，都是可以直接赋值的，比如：姓，名字，生日。但是其中有一个属性却不能直接赋值--Type属性，这个值是从PersonType.cs\(朋友，同事等\)中的枚举类型中选择出来的.这意味着用户只能从有限的几种选项中选择一种。可以用DropDwonList来实现，但是ContactPerson对象并不包含枚举类型的所有选项，所以我们只能提供一个自定义版本的ContactPerson类传递给View.这也是为什么要用到自定义View Model

我看过很多关于在程序的哪里放置View Models的讨论，有些人认为自定义View Models是Model的一部分，但是我认为它和View紧密相关，View Models并不是MVC程序必不可少的一部分，也不能服用，所以它不应该放到Model中区。我把所有的View Model放入一个创建的ViewModel文件夹下，ContactPersonViewModel.cs的源代码如下：
    
    
    using System;
    using System.Collections.Generic;
    using System.Web.Mvc;
    
    namespace ContactManagerMVC.Views.ViewModels
    {
      public class ContactPersonViewModel
      {
        public int Id { get; set; }
        public string FirstName { get; set; }
        public string MiddleName { get; set; }
        public string LastName { get; set; }
        public DateTime DateOfBirth { get; set; }
        public IEnumerable<SelectListItem> Type { get; set; }
      }
    }

看上面类的最后一个属性，我将这个type属性设置成IEnumerable<SelectListItem>类型，这样就可以将Type绑定到View中的Html.DropDownList了。

对应的，也要在Controller中添加2个action,第一个action使用AcceptVerbs\(HttpVerbs.Get\)标签，第二个action使用AcceptVerbs\(HttpVerbs.Post\)标签，第一个方法用于从服务器向客户端传值，第一个方法处理从form提交的数据。
    
    
    [AcceptVerbs(HttpVerbs.Get)]
    public ActionResult Add()
    {
      var personTypes = Enum.GetValues(typeof (PersonType))
        .Cast<PersonType>()
        .Select(p => new
                       {
                         ID = p, Name = p.ToString()
                       });
      var model = new ContactPersonViewModel
                    {
                      Type = new SelectList(personTypes, "ID", "Name")
                    };
      return PartialView(model);
    }
    
    
    [AcceptVerbs(HttpVerbs.Post)]
    public ActionResult Add(ContactPerson person)
    {
      ContactPersonManager.Save(person);
      return RedirectToAction("List");
    }

上面第一个action的前几行代码将ContactType枚举类型转换成数组，数组中的每一个元素都是一个包含id和name属性的匿名对象，id是枚举值，Name是和对应枚举匹配的constant值，ContactPersonViewModel然后进行初始化并且Type属性被赋值相应的类型。我使用Partial View来添加联系人和使用ContactPersonViewModel类型的强类型，对应View部分的代码如下:
    
    
    <%@ Control Language="C#" Inherits="System.Web.Mvc.ViewUserControl<ContactPersonViewModel>" %>
    
    <script type="text/javascript">
      $(function() {
      $('#DateOfBirth').datepicker({ dateFormat: 'yy/mm/dd' });
      });
    </script>
    
    <% using (Html.BeginForm("Add", "Contact", FormMethod.Post)) {%>
          <table>
            <tr>
              <td class="LabelCell">Name</td>
              <td><%= Html.TextBox("FirstName") %></td>
            </tr>
            <tr>
              <td class="LabelCell">Middle Name</td>
              <td><%= Html.TextBox("MiddleName") %></td>
            </tr>
            <tr>v
              <td class="LabelCell">Last Name</td>
              <td><%= Html.TextBox("LastName") %></td>
            </tr>
            <tr>
              <td class="LabelCell">Date of Birth</td>
              <td><%= Html.TextBox("DateOfBirth", String.Empty)%></td>
            </tr>
            <tr>
              <td class="LabelCell">Type</td>
              <td><%=Html.DropDownList("Type")%>
              </td>
            </tr>
            <tr>
              <td class="LabelCell"></td>
              <td><input type="submit" name="submit" id="submit" value="Save" /></td>
            </tr>
          </table>
    <% } %>

在最上面的代码我使用了jQuery UI的Date picker插件作为DateOfBirth输入框的选择方式，而DateOfBirth的第二个参数保证这个textbox在初始状态下为空。此外，所有的输入框对ContactPerson的对应属性名相同，这是为了确保默认的model binder不出差错，MVC还自动为ContactType枚举进行绑定。

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-03-03-asp-net-mvc-linq-to-sql/asp-net-mvc-linq-to-sql-nlayermvc6.gif)

负责响应Post请求的方法可以自动将Request.Form的值和ContactPerson对象的对应属性进行匹配，然后调用BLL层的Save\(\)方法，然后RedicrectToAction会让页面刷新最后调用List这个action.

### **编辑一个联系人**

和前边一样，需要在Controller添加两个action来完成编辑，一个用于响应Get请求，另一个用于响应Post请求:
    
    
    [AcceptVerbs(HttpVerbs.Get)]
        public ActionResult Edit(int id)
        {
          var personTypes = Enum.GetValues(typeof (PersonType))
            .Cast<PersonType>()
            .Select(p => new { ID = p, Name = p.ToString() });
    
          var contactPerson = ContactPersonManager.GetItem(id);
          var model = new ContactPersonViewModel
                        { 
                          Id = id,
                          FirstName = contactPerson.FirstName,
                          MiddleName = contactPerson.MiddleName,
                          LastName = contactPerson.LastName,
                          DateOfBirth = contactPerson.DateOfBirth,
                          Type = new SelectList(personTypes, "ID", "Name", contactPerson.Type)
                        };
          return PartialView(model);
        }
    
        [AcceptVerbs(HttpVerbs.Post)]
        public ActionResult Edit(ContactPerson person)
        {
          ContactPersonManager.Save(person);
          return RedirectToAction("List");
        }

我们在前面已经看到jQuery是如何调用Edit这个action并把被编辑人的id作为参数进行传递的了，然后id用于通过众所周知的bll调用DAL从数据库将联系人的详细信息取出来。在这个过程中ContactPersonViewModel被创建来返回从数据库取出的值，SelectList的通过三个参数构造，第一个参数是Person的类型，第三个参数是DropDownList当前选择的值

partial view的代码和Add View几乎一样：
    
    
    <%@ Control Language="C#" Inherits="System.Web.Mvc.ViewUserControl<ContactPersonViewModel>" %>
    
    <script type="text/javascript">
      $(function() {
        $('#DateOfBirth').datepicker({dateFormat: 'yy/mm/dd'});
      });
    </script>
    
    <% using (Html.BeginForm("Edit", "Contact", FormMethod.Post)) {%> 
         <table>
            <tr>
              <td class="LabelCell">Name</td>
              <td><%= Html.TextBox("FirstName") %></td>
            </tr>
            <tr>
              <td class="LabelCell">Middle Name</td>
              <td><%= Html.TextBox("MiddleName") %></td>
            </tr>
            <tr>
              <td class="LabelCell">Last Name</td>
              <td><%= Html.TextBox("LastName") %></td>
            </tr>
            <tr>
              <td class="LabelCell">Date of Birth</td>
              <td><%= Html.TextBox("DateOfBirth", Model.DateOfBirth.ToString("yyyy/MM/dd")) %></td>
            </tr>
            <tr>
              <td class="LabelCell">Type</td>
              <td><%= Html.DropDownList("Type")%></td>
            </tr>
            <tr>
              <td class="LabelCell"><%= Html.Hidden("Id") %></td>
              <td><input type="submit" name="submit" id="submit" value="Save" /></td>
            </tr>
          </table>
    <% } %>

关键不同是DateOfBirth包含一个将生日信息转换更容易识别的方式，还有在提交按钮附近添加了一个Html.Hidden\(\)，用于保存被编辑用户的id。当然，form的action属性肯定是和Add的View不同。在Form中可以加一个参数用于告诉Action是Add View还是Edit View,这样就能减少代码的重复，但是在示例代码中我还是把他们分成了不同的action,来让职责划分的更清晰一些。

### **删除一个联系人**

删除action就简单多了，并且不需要与之相关的View.仅仅是重新调用List这个action,被删除的数据就不复存在了。
    
    
    public ActionResult Delete(int id)
    {
      ContactPersonManager.Delete(id);
      return RedirectToAction("List");
    }

上面代码是我对BLL和DAL做出改变的地方，原来的ContactPersonManager.Delete\(\)方法的参数是Person的实例，而在DAL中，只有id作为参数。我看不出传递整个对象给BLL,但BLL却只传递对象的唯一ID给DAL的意义所在，所以我将BLL的代码改成接受int类型的参数，这样写起来会更简单。

当删除链接被点击时，调用jQuery的confirmation modal dialog:

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-03-03-asp-net-mvc-linq-to-sql/asp-net-mvc-linq-to-sql-nlayermvc7.gif)

如果点击取消，则什么事也不发生，如果点击确认，则链接就会指向响应的delete action.

### **管理集合**

所有的集合--PhoneNumberList，EmailAddressLIst，AddressList被管理的方式如出一辙。所以，我仅仅挑选EmailAddressLIst作为示例来说明方法，你可以下载示例代码来看其他部分。

首先，我们来看显示被选择联系人的email地址，这包含了controller中List这个Action:
    
    
    public ActionResult List(int id)
    {
      var model = new EmailAddressListViewModel
                    {
                      EmailAddresses = EmailAddressManager.GetList(id),
                      ContactPersonId = id
                    };
      return PartialView(model);
    }

上面方法使用联系人的id作为联系人，并且返回一个自定义View Model—EmailAddressListViewModel.这也是将联系人的id传到View的方法：
    
    
    <%@ Control Language="C#" Inherits="System.Web.Mvc.ViewUserControl<EmailAddressListViewModel>" %>
    <script type="text/javascript">
      $(function() {
        $('#add').click(function() {
          $.get('Email/Add/<%= Model.ContactPersonId %>', function(data) {
            $('#details').html(data);
          });
        });
      });
    </script>
    <table class="table">
       <tr>
         <th scope="col">Contact Person Id</th>
         <th scope="col">Email</th>
         <th scope="col">Type</th>
         <th scope="col">&nbsp;</th>
         <th scope="col">&nbsp;</th>
       </tr>
       <%if(Model.EmailAddresses != null)
         {foreach (var email in Model.EmailAddresses) {%>
       <tr>
         <td><%= email.Id %></td>
         <td><%= email.Email %></td>
         <td><%= email.Type %></td>
         <td title="email/edit" class="link">Edit</td>
         <td title="email/delete" class="link">Delete</td>
       </tr>
            <%}
        }else
     {%>
       <tr>
         <td colspan="9">No email addresses for this contact</td>
       </tr>
     <%}%>
    </table>
    <input type="button" name="add" value="Add Email" id="add" />

你可以看出添加方法需要ContactPersonID作为参数，我们需要确保可以添加新的联系人到响应的联系人列表。编辑和删除方法也是如此--id参数通过url传递到相关action.而所有的单元格都有title属性，这样就可以使用前面部署的live\(\)方法:
    
    
    [AcceptVerbs(HttpVerbs.Get)]
    public ActionResult Add(int id)
    {
      var contactTypes = Enum.GetValues(typeof(ContactType))
        .Cast<ContactType>()
        .Select(c => new
        {
          Id = c,
          Name = c.ToString()
        });
      var model = new EmailAddressViewModel
                    {
                      ContactPersonId = id,
                      Type = new SelectList(contactTypes, "ID", "Name")
                    };
      return PartialView("Add", model);
    }
    
    
    [AcceptVerbs(HttpVerbs.Post)]
    public ActionResult Add(EmailAddress emailAddress)
    {
      emailAddress.Id = -1;
      EmailAddressManager.Save(emailAddress);
      return RedirectToAction("List", new {id = emailAddress.ContactPersonId});
    }

创建自定义View Model存在的目的是为了对现有的EmailAddress进行添加或编辑，这包括一些绑定IEnumerable<SelectListItem>集合到Type dropdown的属性，上面两个Add不同之处在于他们的返回不同，第一个返回partial view,第二个返回List这个action.

集合中的每一个选在在一开始都会将id设为-1,这是为了保证符合”Upsert”存储过程的要求，因为Imar对于添加和删除使用的是同一个存储过程，如果不设置成-1,则当前新建的联系人会更新掉数据库中的联系人。如果你想了解更多，请看他的文章。下面是添加email address的partial view:
    
    
    <%@ Control Language="C#" Inherits="System.Web.Mvc.ViewUserControl<EmailAddressViewModel>" %>
    
    <script type="text/javascript">
      $(function() {
        $('#save').click(function() {
          $.ajax({
            type: "POST",
            url: $("#AddEmail").attr('action'),
            data: $("#AddEmail").serialize(),
            dataType: "text/plain",
            success: function(response) {
              $("#details").html(response);
            }
          });
        });
      });
    </script>
    
    <% using(Html.BeginForm("Add", "Email", FormMethod.Post, new { id = "AddEmail" })) {%>
    <table class="table">
    <tr>
      <td>Email:</td>
      <td><%= Html.TextBox("Email")%></td>
    </tr>
    <tr>
      <td>Type:</td>
      <td><%= Html.DropDownList("Type") %></td>
    </tr>
    <tr>
      <td><%= Html.Hidden("ContactPersonId") %></td>
      <td><input type="button" name="save" id="save" value="Save" /></td>
    </tr>
    </table>
    <% } %>

上面jQuery代码负责通过Ajax提交form.jQuery给html button\(而不是input type=”submit”\)附加事件，然后将页面中的内容序列化并通过post 请求发送到使用合适AcceptVerbs标签修饰的名为add\(\)的action.

### **编辑和删除EmailAddress对象**

编辑EmailAddress对象所涉及的action和前面提到的很相似，仍然是两个action,一个用于处理get请求，另一个用于处理post请求：
    
    
    [AcceptVerbs(HttpVerbs.Get)]
    public ActionResult Edit(int id)
    {
      var emailAddress = EmailAddressManager.GetItem(id);
      var contactTypes = Enum.GetValues(typeof(ContactType))
        .Cast<ContactType>()
        .Select(c => new
        {
          Id = c,
          Name = c.ToString()
        });
      var model = new EmailAddressViewModel
      {
        Type = new SelectList(contactTypes, "ID", "Name", emailAddress.Type),
        Email = emailAddress.Email,
        ContactPersonId = emailAddress.ContactPersonId,
        Id = emailAddress.Id
      };
      return View(model);
    }
    
    [AcceptVerbs(HttpVerbs.Post)]
    public ActionResult Edit(EmailAddress emailAddress)
    {
      EmailAddressManager.Save(emailAddress);
      return RedirectToAction("List", "Email", new { id = emailAddress.ContactPersonId });
    }

下面的partial View代码现在应该很熟悉了吧：
    
    
    <%@ Control Language="C#" Inherits="System.Web.Mvc.ViewUserControl<EmailAddressViewModel>" %>
    
    <script type="text/javascript">
      $(function() {
        $('#save').click(function() {
          $.ajax({
            type: "POST",
            url: $("#EditEmail").attr('action'),
            data: $("#EditEmail").serialize(),
            dataType: "text/plain",
            success: function(response) {
              $("#details").html(response);
            }
          });
        });
      });
    </script>
    
    <% using(Html.BeginForm("Edit", "Email", FormMethod.Post, new { id = "EditEmail" })) {%>
    <table class="table">
    <tr>
      <td>Email:</td>
      <td><%= Html.TextBox("Email")%></td>
    </tr>
    <tr>
      <td>Type:</td>
      <td><%= Html.DropDownList("Type") %></td>
    </tr>
    <tr>
      <td><%= Html.Hidden("ContactPersonId") %><%= Html.Hidden("Id") %></td>
      <td><input type="button" name="save" id="save" value="Save" /></td>
    </tr>
    </table>

上面代码仍然和Add View很像，除了包含EmailAddress.Id的html隐藏域，这是为了保证正确的email地址被更新，而Delete action就不用过多解释了吧。
    
    
    public ActionResult Delete(int id)
    {
      EmailAddressManager.Delete(id);
      return RedirectToAction("List", "Contact");
    }

## **总结**

这篇练习的目的是为了证明Asp.net MVC在没有Linq To Sql和Entity framework的情况下依然可以很完美的使用。文章使用了现有分层结构良好的Asp.net 2.0 form程序，还有可重用的,business Objects层，bussiness logic层以及Data Access 层。而DAL层使用Ado.net调用Sql Server的存储过程来实现。

顺带的，我还展示了如何使用强类型的View Models和简洁的jQuery来让UI体验更上一层。这个程序并不是完美的，也不是用于真实世界。程序中View部分，以及混合编辑和删除的action都还有很大的空间可以重构提升，程序还缺少验证用户输入的手段，所有的删除操作都会返回页面本身。而更好的情况应该是显示删除后用一个子表来显示删除后的内容，这需要将ContactPersonId作为参数传递到相关action,这也是很好实现的。

\---------------------------------------------------

原文链接：<http://www.mikesdotnetting.com/Article/132/ASP.NET-MVC-is-not-all-about-Linq-to-SQL>

translated by [CareySon](http://www.cnblogs.com/careyson)
