---
layout: post
title: "【译】在ASP.NET中创建PDF-iTextSharp起步"
date: 2011-11-02
categories: blog
tags: [博客园迁移]
---

.Net framework 中自身并不包含可以和pdf打交道的方法。所以，当你需要你的ASP.Net Web应用程序中包含创建或与PDF文件交互的部分时，就不得不去找可用的第三方组件.使用谷歌可以搜索到在你预算之内的收费组件，当然同时也有一些开源组件。其中之一就是[iTextSharp](http://sourceforge.net/project/platformdownload.php?group_id=72954),这个程序是著名的JAVA工具[iText](http://www.lowagie.com/iText/)的.Net版本.

但是iTextSharp最大问题是缺少文档.虽然官网上有一些起步教程，但大多数程序员还是选择去看[JAVA版本的文档](http://www.lowagie.com/iText/docs.html)-也就是iText的文档.或者是去买市面上唯一一本关于这方面的书iText in Action.然而，这本书是针对Java版本的iText的书.iText in Action中大多数代码仅仅需要少量修改就可以在.Net下使用,但如果你的C\#水平还是相对比较菜时，Java和.Net两个版本之间类库命名的差别和.Net版本下缺少文档,往往会让你抓狂。最终无奈之下，你只能用[Reflector](http://www.red-gate.com/products/reflector)来查看某些方法到底是干什么用的.所以，作为”How to”系列文章，本文将讲述如何开始使用C\#版的iTextSharp.

第一件事是在[这里](http://sourceforge.net/project/platformdownload.php?group_id=72954)下载iTextSharp,下载完成后解压zip文件得到itextsharp.dll文件,在Visual Studio或Web Developer中创建一个新的网站,通过添加Asp.net文件夹选项添加bin目录,在bin目录下右键选择添加引用选项，在浏览选项卡中，选择itextsharp.dll:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-02-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111021555235849.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111021555215458.gif)

然后点击OK,这个dll随后会被加到bin目录下,现在你可以在你的网站或项目中使用iTextSharp了.

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-02-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111021555243176.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111021555246307.gif)

我还添加了一个用于存放生成的PDF的文件夹命名为PDFs.,为了避免每次使用iTextSharp类时都使用完全路径，我还添加了几个using语句:
    
    
    using iTextSharp.text;
    
    using iTextSharp.text.pdf;

另外，你还需要引用System.IO命名控件，因为你需要创建，打开和关闭文件，这个命名空间中的一些Class也必不可少.

iTextSharp的核心对象是 _Document_ 对象,你需要通过Document对象的实例来操作内存中的pdf文件，所以首先需要实例化一个Document对象：
    
    
    var doc1 = new Document();

上述代码在在内存中使用默认设置来实例化一个Document对象,默认的文档大小是A4（也就是210毫米x297毫米，或是8.26英尺x11.69英尺\),页边距默认都是半英尺.下一步要做的就是将内存中的Document对象保存到硬盘中,使用 _iTextSharp.text.pdf.PdfWriter_ 类来实现这个功能:
    
    
    //use a variable to let my code fit across the page...
     
    string path = Server.MapPath("PDFs");
    
    PdfWriter.GetInstance(doc1, new FileStream(path + "/Doc1.pdf", FileMode.Create));

现在就可以对文档进行操作了，首先打开文档，往里写一段内容，最后关闭文档:
    
    
    doc1.Open();
     
    doc1.Add(new Paragraph("My first PDF"));
    
    doc1.Close();

就是这么简单,下面刷新PDFS文件夹，你就会发现一个新的文件-Doc1.pdf,打开这个文件，刚才添加的段落已经成功显示.

很多时候，你并不希望通过默认设置创建默认大小，默认边距的PDF文档，所以iTextSharp允许你自定义这些设置,所以Document对象还提供了其他两个构造函数:
    
    
    public Document(iTextSharp.text.Rectangle pageSize);
    
    public Document(iTextSharp.text.Rectangle pageSize, float, float, float, float);

第一个构造函数可以这样使用:
    
    
    var doc = new Document(PageSize.A5);

_PageSize_ 类包含了一系列 _Rectangle_ 对象代表了大多数纸张的大小,从A0到A10,B0到B10,legal,分类账,信封，明信片，剪报等，如果 _PageSize_ 类内的纸张大小无法满足你的需求,你可以自定义一个 _Rectangle_ 对象,对其设置值后作为参数传给 _Document_ 构造函数:
    
    
    var doc = new Document(new Rectangle(100f, 300f));
     
    PdfWriter.GetInstance(doc, new FileStream(path + "/Doc2.pdf", FileMode.Create));
     
    doc.Open();
     
    doc.Add(new Paragraph("This is a custom size"));
    
    doc.Close();

上面代码中，创建的PDF文档为100像素宽，300像素长，因为是72像素/英尺，所以这个文档并不大,实际上为1.39 英尺 x 4.17 英尺\(\).

第二个构造函数以Rectangle和四个float类型的数字作为参数允许你通过float类型的变量自定义页边距，同样，单位是像素，默认半英尺的像素为36像素.

如果你使用PageSize类的构造函数,或者是自定义Rectangle,你还可以为文档设置背景色,这个设置可以通过RGB颜色值，或是CMYK值。如果你生成的PDF文档将会在专业的平板印刷机中印刷,你必须通过CMYK来设置.但对于大多数数码打印机来说，使用RGB更容易被接受，当然，如果你的PDF用于WEB，则优先使用RGB，设置文档的背景色，通过Rectangle对象的 _BackgroundColorproperty_ 进行设置:
    
    
    r.BackgroundColor = new CMYKColor(25, 90, 25, 0);
     
    r.BackgroundColor = new Color(191, 64, 124);

上面两行代码都会将文档的背景色设置为迷人的粉红色…

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-02-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111021555279357.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111021555258061.gif)

本文简单介绍了iTextSharp,也是你学习iTextSharp的入口，后续文章将会详细介绍这个敏捷的组件的一系列功能.

原文地址:<http://www.mikesdotnetting.com/Article/80/Create-PDFs-in-ASP.NET-getting-started-with-iTextSharp>

Translated by [CareySon](www.cnblogs.com/careyson)

\---------------

写在后面：翻译这篇文章是因为项目中最近需要用到操作PDF，可是.Net下这个组件文档相对比较少，即使有一些资料，也不系统，所以我找到了这个系列的文章，在翻译的过程中，也是对我自己的学习和提高.后续文章翻译中….
