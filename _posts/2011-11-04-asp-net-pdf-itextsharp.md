---
layout: post
title: "【译】在Asp.Net中操作PDF – iTextSharp-列表"
date: 2011-11-04
categories: blog
tags: [博客园迁移]
---

在前文中，我们已经知道了如何利用iTextSharp创建PDF文档，设置字体样式和风格.本文开始讲述iTextSharp中的有序列表和无需列表.如果你还没阅读我前面的文章，那么地址是:

[在ASP.NET中创建PDF-iTextSharp起步](http://www.cnblogs.com/CareySon/archive/2011/11/02/2233174.html)

[在Asp.Net中操作PDF - iTextSharp - 使用字体](http://www.cnblogs.com/CareySon/archive/2011/11/03/2234342.html)

[在Asp.Net中操作PDF – iTextSharp -利用块，短语，段落添加文本](http://www.cnblogs.com/CareySon/archive/2011/11/03/2234625.html)

在iTextSharp中列表的创建是通过iTextSharp.text.List对象实现的。列表实质上是iTextSharp.text.ListItem的集合.也就是由ListItem组成的数组.ListItem继承了Paragraph对象（而Paragraph对象继承于Phrase,Phrase又继承于Arraylist\),所以生成的每一个List都会自动换行.就如同List在HTML分为<ul>和<ol>一样，iTextSharp中列表同样分为有序列表和无序列表.下面我们来直接看如何生成列表的代码:
    
    
    string path = Server.MapPath("PDFs");
     
    it.Document doc = new it.Document();
     
    try
     
    {
     
        PdfWriter.GetInstance(doc, new FileStream(path + "/Lists.pdf", FileMode.Create));
     
        doc.Open();
     
        it.List list = new it.List(it.List.UNORDERED);
     
        list.Add(new it.ListItem("One"));
     
        list.Add("Two");
     
        list.Add("Three");
     
        list.Add("Four");
     
        list.Add("Five");
     
        it.Paragraph paragraph = new it.Paragraph();
     
        string text = "Lists";
     
        paragraph.Add(text);
     
        doc.Add(paragraph);
     
        doc.Add(list);
     
    }
     
    catch (it.DocumentException dex)
     
    {
     
        Response.Write(dex.Message);
     
    }
     
    catch (IOException ioex)
     
    {
     
        Response.Write(ioex.Message);
     
    }
     
    finally
     
    {
     
        doc.Close();
     
    }

如果你对上面代码的意思并不了解.那么为什么要用”it"引用List的确需要解释一下.正如代码所示，it作为引用某些类，因为如果你直接在ASP.Net code-behind模式下工作，你会发现visual studio在引用iTextSharp的ListItem时和也包含ListItem的System.Web.UI.WebControls发生命名空间冲突.这意味着如果仅仅是用如下代码：
    
    
    ListItem li = new ListItem();

则会报不明确引用的警告。解决方法是使用完全引用:
    
    
    iTextSharp.text.ListItem li = new iTextSharp.text.ListItem();

但是使用完全引用又臭又长，所以这里使用了简洁引用:
    
    
    using it = iTextSharp.text;

现在，你就可以使用别名了.

回到讲述我们实际代码的作用，第一件事是创建一个List对象，并传入一个布尔类型的参数告诉List生成的是有序或无序列表.默认是False\(也就是无序列表\),然后为List加入了5个项。第一个项是通过匿名函数传入String参数类型来创建ListItem并传入，从第二个开始，则是直接传入String类型的参数.最后是创建一个Paragraph对象和list对象共同传入document.

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-04-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111041111177893.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111041111169105.gif)

如上图所见，每一个列表项都像Paragraph那样自己单占一行.还有列表是无序列表，每一个列表项之前都用一个横杠作为修饰，并且列表没有缩进。但iTextSharp提供了多种方法允许设置列表使其更加美观：
    
    
    it.List list = new it.List(it.List.UNORDERED, 10f);
     
    list.SetListSymbol("\u2022");
     
    list.IndentationLeft = 30f;

上面第二个参数（float类型\)传入List的构造函数，用于将每一个列表项的缩进设置成10\(也就是列表符号和列表项第一个字符的距离。\).然后我通过SetListSymbol方法将列表项符号改成更传统的”.”,最后我将整个列表向右缩进30，现在列表看起来就好多了：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-04-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111041111188251.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111041111182254.gif)

如果你使用有序列表并将罗马数字作为标识，你可以使用RomanList类：
    
    
    RomanList romanlist = new RomanList(true, 20);
     
    romanlist.IndentationLeft = 30f;
     
    romanlist.Add("One");
     
    romanlist.Add("Two");
     
    romanlist.Add("Three");
     
    romanlist.Add("Four");
     
    romanlist.Add("Five");
     
    doc.Add(romanlist);

由于某些奇怪的理由，传入RomanList构造函数的第二个参数是一个Int类型的值，第一个参数告诉RomanList究竟使用大写还是小写作为行项目标识:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-04-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111041111207006.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111041111197628.gif)

还有一个GreekList类支持使用希腊字符作为列表项目的标识，还有其它两个类ZapfDingbatsList 和ZapfDingbatsNumberList，由于他们使用了ZapfDingBats字体，所以这两个类对列表项符号提供了更多丰富的选项，希腊和罗马字符作为行项目标识时，分别不能超过24和26个行项目,而ZapfDingBatsNumberList最多只能处理10个字符，当字符超出范围后，列表又会从0开始.
    
    
    ZapfDingbatsList zlist = new it.ZapfDingbatsList(49, 15);
     
    zlist.Add("One");
     
    zlist.Add("Two");
     
    zlist.Add("Three");
     
    zlist.Add("Four");
     
    zlist.Add("Five");
     
    doc.Add(zlist);

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-04-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-20111104111122952.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111041111218543.gif)

列表之间还可以相互嵌套，因为List.Add\(\)方法接受一个Object类型的参数,所以你只要传入一个有效的List对象就行。下面代码首先创建了一个RomanList对象，然后再创建一个有序列表.我们将RomanList对象添加到有序列表上，则RomanList会相对于父有序列表自动向后缩进:
    
    
    RomanList romanlist = new RomanList(true, 20);
     
    romanlist.IndentationLeft = 10f;
     
    romanlist.Add("One");
     
    romanlist.Add("Two");
     
    romanlist.Add("Three");
     
    romanlist.Add("Four");
     
    romanlist.Add("Five");
     
     
     
    List list = new List(List.ORDERED, 20f);
     
    list.SetListSymbol("\u2022");
     
    list.IndentationLeft = 20f;
     
    list.Add("One");
     
    list.Add("Two");
     
    list.Add("Three");
     
    list.Add("Roman List");
     
    list.Add(romanlist);
     
    list.Add("Four");
     
    list.Add("Five");
     
     
     
    doc.Add(paragraph);
     
    doc.Add(list);

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-04-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111041111243753.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111041111234441.gif)

  
\-----------------   
原文链接:[Lists with iTextSharp](http://www.mikesdotnetting.com/Article/83/Lists-with-iTextSharp)   
translated by [CareySon](http://www.cnblogs.com/careyson)
