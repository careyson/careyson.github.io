---
layout: post
title: "【译】在Asp.Net中操作PDF - iTextSharp - 绘制矢量图"
date: 2011-11-08
categories: blog
tags: [博客园迁移]
---

在上一篇iTextSharp文章中讲述了如何将现有的图片插入PDF中并对其进行操作。但有时，你需要在PDF中绘制不依赖于任何图片文件的矢量图形。iTextSharp既包含了绘制简单矢量图功能，也包含了绘制复杂矢量图的功能。这篇文章将会帮助你入门。本系列文章之前的文章如下:

[在ASP.NET中创建PDF-iTextSharp起步](http://www.cnblogs.com/CareySon/archive/2011/11/02/2233174.html)

[在Asp.Net中操作PDF - iTextSharp - 使用字体](http://www.cnblogs.com/CareySon/archive/2011/11/03/2234342.html)

[在Asp.Net中操作PDF – iTextSharp -利用块，短语，段落添加文本](http://www.cnblogs.com/CareySon/archive/2011/11/03/2234625.html)

[在Asp.Net中操作PDF – iTextSharp-列表](http://www.cnblogs.com/CareySon/archive/2011/11/04/2235834.html)

[在Asp.Net中操作PDF – iTextSharp - 使用链接和书签](http://www.cnblogs.com/CareySon/archive/2011/11/04/2236239.html)

[在Asp.Net中操作PDF – iTextSharp - 使用表格](http://www.cnblogs.com/CareySon/archive/2011/11/05/2237116.html)

[在Asp.Net中操作PDF – iTextSharp - 操作图片](http://www.cnblogs.com/CareySon/archive/2011/11/07/2239017.html)

在前面的文章所讲述的内容中，直到现在为止，所有添加到PDF文档的内容都只是依赖于将页面中的内容加入到排版流中的简单iText排版.简单的iText排版还负责如果文字内容溢出当前页面，则生成新的页面。而对于处理矢量图来说，就需要另一种方法了。那就是使用PdfContentByte\(\)对象，这个对象的实例可以从PdfWriter对象的DirectContent属性获得.这也意味着不像前面那样仅仅是使用PdfWriter.GetInstance方法了，我们还需要获得PdfWrite类的实例:
    
    
      string pdfpath = Server.MapPath("PDFs");
     
      Document doc = new Document();
     
      try
     
      {
     
        PdfWriter writer = PdfWriter.GetInstance(doc, new FileStream(pdfpath + "/Graphics.pdf", FileMode.Create));
     
        doc.Open();
     
        PdfContentByte cb = writer.DirectContent;
         ...

现在我们就可以使用PdfContentByte对象来画矢量图了：
    
    
    cb.MoveTo(doc.PageSize.Width / 2, doc.PageSize.Height / 2);
     
    cb.LineTo(doc.PageSize.Width / 2, doc.PageSize.Height);
     
    cb.Stroke();
     
    cb.MoveTo(0, doc.PageSize.Height/2);
     
    cb.LineTo(doc.PageSize.Width, doc.PageSize.Height / 2);
     
    cb.Stroke();

第一行代码将光标移动到传入的X，Y坐标轴参数，也就是文档的正中间.下一行代码从当前光标的位置画一条线到传入的坐标参数点。这里就是从文档中间画一条线到文档上边。当然，这个方法还没有开始”画”这条线，这个方法仅仅是记录我们要画这条线的意图，直到调用了Stroke\(\)方法后，这条线才能真正写入PDF文档。第二段代码从文档中间的最左边画到中间的最右边，形成了一个上面2分的文档大纲:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-08-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111081458565956.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111081458566022.gif)

使用同样的方法，我们可以在文档左上的格子中加入一个正方形：
    
    
    cb.MoveTo(100f, 700f);
     
    cb.LineTo(200f, 700f);
     
    cb.LineTo(200f, 600f);
     
    cb.LineTo(100f, 600f);
     
    cb.ClosePath();
     
    cb.Stroke();

我们并没有直接指定画出正方形的最后一条边,使用ClosePath\(\)方法可以直接从当前点画回到原点坐标.其实，我们还可以使用iTextSharp所提供的画正方形的快捷方法，下面代码展示如何利用这个快捷方法在右上方画出正方形:
    
    
    cb.Rectangle(doc.PageSize.Width-200f, 600f, 100f, 100f);
     
    cb.Stroke();

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-08-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111081459004655.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111081459003084.gif)

让我们继续在页面添加四个正方形,每个正方形最后都使用了不同于Stroke\(\)的方法来将其写入文档，如果你是用过Photoshop或是firework就应该知道，实际上Stroke\(\)其实是对象的轮廓，而Fill实际上就是对象的填充色,在这里我使用CMYK颜色，将边框颜色设置成蓝绿色，而填充颜色设置为黄色：
    
    
    cb.SetColorStroke(new CMYKColor(1f, 0f, 0f, 0f));
     
    cb.SetColorFill(new CMYKColor(0f, 0f, 1f, 0f));
     
     
     
    cb.MoveTo(70, 200);
     
    cb.LineTo(170, 200);
     
    cb.LineTo(170, 300);
     
    cb.LineTo(70, 300);
     
    //Path closed and stroked
     
    cb.ClosePathStroke();
     
     
     
    cb.MoveTo(190, 200);
     
    cb.LineTo(290, 200);
     
    cb.LineTo(290, 300);
     
    cb.LineTo(190, 300);
     
    //Filled, but not stroked or closed
     
    cb.Fill();
     
     
     
    cb.MoveTo(310, 200);
     
    cb.LineTo(410, 200);
     
    cb.LineTo(410, 300);
     
    cb.LineTo(310, 300);
     
    //Filled, stroked, but path not closed
     
    cb.FillStroke();
     
     
     
    cb.MoveTo(430, 200);
     
    cb.LineTo(530, 200);
     
    cb.LineTo(530, 300);
     
    cb.LineTo(430, 300);
     
    //Path closed, stroked and filled
     
    cb.ClosePathFillStroke();

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-08-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111081459026474.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111081459014904.gif)

当你使用Rectangle对象而不是手动去画矩形时，传入的第一个和第二个参数是矩形右下角的坐标，而其他两个参数分别为矩形的宽和高.iTextSharp中还包括其他矢量图，比如说圆，圆中传入的坐标则是圆心的坐标,第三个参数则为半径的大小。上面的四个正方形中不难看出正方形的边长为100像素，正方形的中心坐标则为120 x, 250 y，下面代码可以在正方形中加入一个圆:
    
    
    cb.SetCMYKColorStroke(255, 255, 0, 0);
     
    cb.SetCMYKColorFill(0, 255, 255, 0);
     cb.SetLineWidth(2f);
     
    cb.Circle(120f, 250f, 50f);
     
    cb.Fill();

我猜想你是不是在想我在代码中用过的CMYK的四个参数分别代表什么。这并不直观，CMYK分别代表四种颜色所占的百分比,比如暖红色实际上是C:0%,M100%,Y100%,K100%.CMYK的构造函数需要的四个参数都为float类型，你可以传入代表着百分比的数字.我还可以传入0和1，其实传入的参数可以是任何大小的float类型，百分比实际上是几个参数的比例。所以如果我想设置成100%的蓝色\(蓝绿\),我可以使用3000f,0,0,0这样的参数.注意这里不要不小心多打了一个0.

SetCMYKColorFill\(\)方法接受一个int类型的参数.我觉得可能是因为这个方法是基于百分比来设置CMYK的吧，所以对于暖红色的设置我传入了0,100,100,0,但我得到的却是一个粉色。我认为这是一个bug.是由于之前使用过一次SetCMYKColorFill\(\)方法而影响到了这次的颜色，所以我重置了CMYK的颜色并再次实验，还是不行。最后我发现CMYKColor对象是派生于ExtendedColor类，而所能接受的最大int值为255,这和RGB有些类似，如果你不知道这个类的工作原理，那你会很迷惑。所以我按照这个进行了设置，终于得到了我想要的颜色.为了进行验证，我还传入了大于255的数字，最后发现任何大于255的数字都会被iTextSharp截断，比如256就等于1，510就等于255.至少，这是在我的测试中得到的结论.

让我们回到正题，下面的第一个正方形中放入了一个红色有着蓝色边框（2px）的圆:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-08-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111081459035263.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111081459027280.gif)

接下来，让我们来看看使用iTextSharp提供的预定义的其他形状，椭圆。首先，定义一个长方形，然后将一个椭圆加入到长方形之内:
    
    
    // x, y of bottom left corner, width, height
     
    cb.Rectangle(100f, 200f, 300f, 100f);
     
    cb.Stroke();
     
    //Bottom left and top right coordinates
     
    cb.Ellipse(100f, 200f, 400f, 300f);
     
    cb.Stroke();

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-08-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111081459071453.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111081459032165.gif)

如果上面两个图形中第一个和第三个参数不同，第二个和第四个参数相同，最后结果会是一个圆。

接下来的代码展示如何使用另一个预定义的图形：圆角矩形.圆角矩形的构造函数分别为左下角的坐标，宽和高，以及圆角的度数。为了演示圆角矩形圆角的度数原理，我还在这个圆角矩形的左下角加入一个圆:
    
    
    //Bottom left coordinates followed by width, height and radius of corners
     
    cb.RoundRectangle(100f, 500f, 200f, 200f, 20f);
     
    cb.Stroke();
     
     
     
    cb.Circle(120f, 520f, 20f);
     
    cb.Stroke();
     
     
     
    cb.MoveTo(118f, 520f);
     
    cb.LineTo(122f, 520f);
     
    cb.Stroke();
     
    cb.MoveTo(120f, 518f);
     
    cb.LineTo(120f, 522f);
     
    cb.Stroke();

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-08-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111081459083829.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111081459087799.gif)

三角形就更容易画了，只需要画三条线就好，下面代码展示了如何画一个直角三角形，并标出直角:
    
    
    cb.MoveTo(350f, 450f);
     
    cb.LineTo(350f, 600f);
     
    cb.LineTo(500f, 450f);
     
    cb.ClosePathStroke();
     
     
     
    cb.MoveTo(350f, 460f);
     
    cb.LineTo(360f, 460f);
     
    cb.LineTo(360f, 450f);
     
    cb.Stroke();

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-08-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111081459094569.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/20111108145909731.gif)

### **曲线和弧**

贝塞尔曲线是矢量图中很重要的一种。这种曲线的画法是基于数学公式而不是仅仅点到点。贝塞尔曲线的画法是通过指定一个开始点，一个结束点，和两个控制点。第一个控制点产生的效果是基于开始点，第二个控制点产生的效果是基于结束点。贝塞尔曲线从开始点朝向结束点，中间的弯曲是取决于控制点。但曲线本身会很接近控制点，但不会穿过控制点，如果你使用过PhotoShop或是Firework,控制点可以理解为你进行拖拽用来控制弧度的”控键（handles\)”:

下面是一个画曲线的例子，开始点设置为\(200,10\),结束点设置为\(350,150\):
    
    
    //Start Point
     
    cb.MoveTo(200f, 10f); 
    
    //Control Point 1, Control Point 2, End Point
     
    cb.CurveTo(150f, 30f, 450f, 70f, 350f, 150f);
     
    cb.Stroke();

这个曲线由开始点朝向第一个控制点，并向第二个控制点弯曲，在到达结束点之前，曲线如下：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-08-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111081459114993.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111081459106139.gif)

上面的图片或许并不是那么容易让人理解，所以我加上了一些”控键（handles\)”:
    
    
    cb.MoveTo(200f, 10f);
     
    cb.LineTo(150f, 30f);
     
    cb.Stroke();
     
     
     
    cb.MoveTo(450f, 70f);
     
    cb.LineTo(350f, 150f);
     
    cb.Stroke();
     
     
     
    cb.Circle(450f, 70f, 1f);
     
    cb.Stroke();
     
    cb.Circle(150f, 30f, 1f);
     
    cb.Stroke();

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-08-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111081459123433.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111081459111547.gif)

第一个控制点的“控键（handles\)”相对比较短，所以曲线仅仅朝第一个控制点弯曲了一点，第二个控制点相对较长，所以曲线在其影响下朝着第二个控制点弯曲比较多,理解这个意思的最好办法是将第二个控制点的“控键（handles\)”再次延长：
    
    
    cb.SetColorStroke(Color.GREEN);
     
    //start point (x,y)
     
    cb.MoveTo(200f, 10f);
     
    //control point 1 (x,y), control point 2 (x,y), end point (x,y)
     
    cb.CurveTo(150f, 30f, 550f, 100f, 350f, 150f);
     
    cb.Stroke();
     
     
     
    cb.MoveTo(550f, 100f);
     
    cb.LineTo(350f, 150f);
     
    cb.Stroke();
     
     
     
    cb.Circle(550f, 100f, 1f);
     
    cb.Stroke();
     
     
     
    cb.SetColorStroke(Color.LIGHT_GRAY);
     
     
     
    //Bottom Left(x,y), Top Right(x,y), Start Angle, Extent
     
    cb.Arc(350f, 70f, 550f, 130f, 270f, 90f);
     
    cb.SetLineDash(3f, 3f);
     
    cb.Stroke();
     
     
     
    cb.SetLineDash(0f);
     
    cb.MoveTo(550f, 100f);
     
    cb.LineTo(535f, 95f);
     
    cb.Stroke();
     
    cb.MoveTo(550f, 100f);
     
    cb.LineTo(552f, 88f);
     
    cb.Stroke();

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-08-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111081459132744.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111081459135319.gif)

原来的曲线用黑色显示.后加入的曲线用绿色显示。现在你可以看到绿色的控制点已经展示出它的影响.从开始点开始，绿色曲线开始慢慢的低于黑色曲线，然后分开.因为第二个控制点离曲线的结束点比较远，使得绿色的曲线更加的圆一些。也就是在到达终点之前朝向控制点偏离的更多一些。

对于上面展示的新添加的代码，还有其他一些需要说明的地方。其中之一就是Arc对象，这里用于画一个带箭头的从原来的控制点到新的控制点的曲线。弧是曲线的一部分.这里弧从左下角的\(350,70\)到右上角的\(550,130\).弧的度数默认是按逆时针算的。这里的弧度是270，相当于顺时针90度.除此之外，SetLineDash\(\)方法的用途是将所画的弧线变为虚线。

\-------------------------------------------

原文链接:[iTextSharp - Drawing shapes and Graphics](http://www.mikesdotnetting.com/Article/88/iTextSharp-Drawing-shapes-and-Graphics)

Translate by [CareySon](http://www.cnblogs.com/careyson)
