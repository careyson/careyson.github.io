---
layout: post
title: "【译】在Asp.Net中操作PDF - iTextSharp - 使用字体"
date: 2011-11-03
categories: blog
tags: [博客园迁移]
---

紧接着前面我对iTextSharp简介博文，iTextSharp是一个免费的允许Asp.Net对PDF进行操作的第三方组件。本篇文章讲述如何在你创建的PDF文档中使用各种字体。如果你还没有阅读我的[第一篇文章](http://www.cnblogs.com/CareySon/archive/2011/11/02/2233174.html),我强烈推荐你现在就阅读iTextSharp的简介.

iTextSharp默认支持14种字体，分别为：Courier, Courier Bold, Courier Italic, Courier Bold and Italic, Helvetica, Helvetica Bold, Helvetica Italic, Helvetica Bold and Italic, Times Roman, Times Roman Bold, Times Roman Italic, Times Roman Bold and Italic, Symbol, ZapfDingBats®.因为Times Roman已经有了替代品Times New Roman，所以iTextSharp的默认字体为Helvetica, 12pt,黑色，也就是所谓的正常\(Normal\)字体。

iTextSharp提供了3种主要方式来设置字体：一种是使用BaseFont.CreateFont\(\)方法,第二种方法是使用FontFactory.GetFont\(\)方法。第三种方法是直接生成一个新的Font对象,BaseFont.CreateFont\(\)有很多局限性，表现在仅仅是生成一个新的字体定义。new Font\(\)允许-------------，FontFactory.GetFont\(\)返回一个你可以直接操作的Font对象。并且提供了14种不同的重载来给你提供更多选项,所以通常来说你可能会使用这个方法，但是开始将这个方法之前，让我们先来看一看BaseFont.CreateFont\(\)方法:
    
    
    BaseFont bfTimes = BaseFont.CreateFont(BaseFont.TIMES_ROMAN, BaseFont.CP1252, false);
     
    Font times = new Font(bfTimes, 12, Font.ITALIC, Color.RED);

上面的代码创建了一个BaseFont对象并且使用内置的constant值来设置字体类型和编码类型。在是否将字体嵌入PDF中选择了False以减少PDF的大小.但是如果你的字体在大多数用户的电脑中都没有时，亦或是你打算在专业的印刷设备中印刷出你的pdf时，这项你必须选择为True.使用BaseFont来创建一个新的Font对象，下一行代码进一步从字体大小，字体风格，颜色来设置字体，当然，我们依然使用内置的constant类型值,下面，将上述风格字体加入段落:
    
    
    
    string path = Server.MapPath("PDFs");
     
    Document doc = new Document();
     
    PdfWriter.GetInstance(doc, new FileStream(path + "/Font.pdf", FileMode.Create));
    
    doc.Open();
     
    doc.Add(new Paragraph("This is a Red Font Test using Times Roman", times));
     
    doc.Close();

结果如下:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-03-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111031155526802.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111031155395091.gif)

现在开始说FontFactory.GetFont\(\)方法，这个方法提供了14种不同的重载来让你对字体的任何方面进行设置，包括：字体，颜色， 风格，是否嵌入，编码以及缓存等.每次你调用FontFactory.GetFont\(\)时都会返回一个新的对象.这个方法对于字体的设置可以对任何在iTextSharp中注册的字体进行生效。在iTextSharp中注册的字体包括windows字体的默认目录，在WIN XP下，这个目录一般为”C:/WINDOWS/Fonts”,如果你想知道哪些字体在iTextSharp中已注册，FontFactory.RegisteredFonts将会告诉你答案，查看这个列表对于我们想获得确切的字体名称尤为重要:
    
    
    int totalfonts = FontFactory.RegisterDirectory("C:\\WINDOWS\\Fonts");
    
    StringBuilder sb = new StringBuilder();
     
    foreach (string fontname in FontFactory.RegisteredFonts)
    
    {
     
      sb.Append(fontname + "\n");
     
    }
     
    doc.Add(new Paragraph("All Fonts:\n" + sb.ToString()));
    
     
     
     
    
     
     
    Font arial = FontFactory.GetFont("Arial", 28, Color.GRAY);
    
    Font verdana = FontFactory.GetFont("Verdana", 16, Font.BOLDITALIC, new Color(125, 88, 15));
     
    Font palatino = FontFactory.GetFont(
    
     "palatino linotype italique", 
    
      BaseFont.CP1252, 
    
      BaseFont.EMBEDDED, 
    
      10, 
    
      Font.ITALIC, 
    
      Color.GREEN
    
      );
     
    Font smallfont = FontFactory.GetFont("Arial", 7);
     
    Font x = FontFactory.GetFont("nina fett");
    
    x.Size = 10;
     
    x.SetStyle("Italic");
     
    x.SetColor(100, 50, 200);

如你所见，上面的一些方法使用iTextSharp的Color对象的constant值来设置字体颜色，还有诸如使用SetColor\(\)方法传入RGB值或是New一个Color对象传入。通常情况下，我们都可以传入int值作为字体风格参数,或者使用SetStyle\(\)方法传入一个字符串。当然，生成Font还有很多种参数传入方式，使用Intellisense或是对象浏览器来查看更确切的参数使用方法.

### **注册字体**

有时候你会遇到在WEB服务器上你没有权限安装字体，这时你必须显示在iTextSharp中注册字体了:
    
    
    
    string fontpath = Server.MapPath(".");
     
    BaseFont customfont = BaseFont.CreateFont(fontpath + "myspecial.ttf", BaseFont.CP1252, BaseFont.EMBEDDED);
    
    Font font = new Font(customfont, 12);
     
    string s = "My expensive custom font.";
     
    doc.Add(new Paragraph(s, font));

上面代码中你也许会注意到字体文件是嵌入PDF中的\(BaseFont.EMBEDDED\),因为很多情况下你创建的PDF中的字体在用户的电脑上并不存在。

\--------------------------- 原文地址:[Create PDFs in ASP.NET - getting started with iTextSharp](http://www.mikesdotnetting.com/Article/80/Create-PDFs-in-ASP.NET-getting-started-with-iTextSharp)   
translated by [careyson](http://www.cnblogs.com/careyson)
