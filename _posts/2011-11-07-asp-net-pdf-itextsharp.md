---
layout: post
title: "【译】在Asp.Net中操作PDF – iTextSharp - 操作图片"
date: 2011-11-07
categories: blog
tags: [博客园迁移]
---

作为我的iTextSharp系列的文章的第七篇,开始探索使用iTextSharp在PDF中操作图片，理解本篇文章需要看过系列文章的前六篇：

[在ASP.NET中创建PDF-iTextSharp起步](http://www.cnblogs.com/CareySon/archive/2011/11/02/2233174.html)

[在Asp.Net中操作PDF - iTextSharp - 使用字体](http://www.cnblogs.com/CareySon/archive/2011/11/03/2234342.html)

[在Asp.Net中操作PDF – iTextSharp -利用块，短语，段落添加文本](http://www.cnblogs.com/CareySon/archive/2011/11/03/2234625.html)

[在Asp.Net中操作PDF – iTextSharp-列表](http://www.cnblogs.com/CareySon/archive/2011/11/04/2235834.html)   
[在Asp.Net中操作PDF – iTextSharp - 使用链接和书签](http://www.cnblogs.com/CareySon/archive/2011/11/04/2236239.html)

[在Asp.Net中操作PDF – iTextSharp - 使用表格](http://www.cnblogs.com/CareySon/archive/2011/11/05/2237116.html)

iTextSharp支持所有主流的图片格式，比如:jpg, tif, gif, bmp, png和wmf.在iTextSharp中使用Image.GetInstance\(\)方法创建图片有很多种方式,或许最常用的方式应该是传入文件的路径和文件名到该方法中:
    
    
    string pdfpath = Server.MapPath("PDFs");
     
    string imagepath = Server.MapPath("Images");
     
    Document doc = new Document();
    
    try
     
    {
     
      PdfWriter.GetInstance(doc, new FileStream(pdfpath + "/Images.pdf", FileMode.Create));
     
      doc.Open();
    
     
     
      doc.Add(new Paragraph("GIF"));
     
      Image gif = Image.GetInstance(imagepath + "/mikesdotnetting.gif");
    
      doc.Add(gif);
     
    }
     
    catch (DocumentException dex)
     
    {
     
      Response.Write(dex.Message);
    
    }
     
    catch (IOException ioex)
     
    {
     
      Response.Write(ioex.Message);
     
    }
     
    catch (Exception ex)
    
    {
     
      Response.Write(ex.Message);
     
    }
     
    finally
     
    {
     
      doc.Close();
     
    }
     
     

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-07-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111071112062170.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111071112051745.gif)

其他可以使用的构造函数的重载可以是传入一个URL或是一个System.Drawing.Image对象（并不是iTextSharp.text.Image）.

注意：下面代码段的System.Drawing.Image.FromStream\(\)方法使用了命名空间的别名，在前面讲述List的文章中就已经提到过，使用命名空间的别名以防止两个不同Image类冲突:
    
    
    doc.Add(new Paragraph("JPG"));
     
    string url = "http://localhost:1805/PDF/Images/mikesdotnetting.jpg";
    
    Image jpg = Image.GetInstance(new Uri(url));
     
    doc.Add(jpg);
     
    doc.Add(new Paragraph("PNG"));
    
    using (FileStream fs = new FileStream(imagepath + "/mikesdotnetting.png", FileMode.Open))
     
    {
    
      Image png = Image.GetInstance(sd.Image.FromStream(fs),ImageFormat.Png);
     
      doc.Add(png);
     
    }

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-07-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111071112081938.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111071112079006.gif)

目前为止还不能辨别出我所提供的图片哪个是JPG,哪个是PNG，但在PDF中的结果图片分辨率并不好，在默认情况下，嵌入PDF的图片是72 dpi\(每英尺的点阵数\),这种分辨率如果实在PDF需要打印出来时，就非常不够了，一般来说，商业打印机需要的图片最小分辨率为300dpi.为了达到这个效果，你可以将72dpi的图片缩小至原图片的24%.实际上你是将原来300像素的图片缩小为72像素：72/300 \* 100 = 24%。这时嵌入pdf的图片从大小来说一模一样，但是在文档占用方面却少了很多:
    
    
    doc.Add(new Paragraph("TIF Scaled to 300dpi"));
     
    Image tif = Image.GetInstance(imagepath + "/mikesdotnetting.tif");
    
    tif.ScalePercent(24f);
     
    doc.Add(tif);

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-07-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111071112103103.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111071112098742.gif)

现在，我有一个比较大的图片想作为logo放在pdf中，这个图片大小为:300x890像素,所以在72dpi的情况下，这个图片占用4.17英尺宽，12.36英尺高。如果将图片的分辨率改为300dpi的话，那图片的占用就会变成1英尺宽，2.97英尺高.如果仅仅是实现这个功能的话，上面给出的代码已经可以达到这个功能。但是，现在我想将这个图片放到PDF中的特定位置，也就是右上方,使用SetAbsolutePosition\(\)这个方法可以实现这个目标，但我还需要计算绝对位置.

SetAbsolutePosition\(\)方法接受两个float类型的参数，第一个参数是X轴坐标，是从文档最左边开始算起，第二个参数是Y轴坐标，是从文档下方开始算起。A4纸的的默认参数是595像素宽，842像素高，四周的页边距都为36像素.

传入的坐标参数点实际上是图片的左下角坐标。图片距离右边的距离为宽度72像素\(1英尺）+页边距36像素\(总共108像素\)，所以X的坐标为595-108=487.对于Y轴来说,和X轴坐标的计算方法大同小异，Y轴坐标为842 - \(213.6 + 36\) = 592.4.实际上我并不需要知道所有纸张类型的大小来做数学题，虽然我需要设置图片在文中的绝对值。幸运的是，我可以使用Document.PageSize对象来帮我记住这个数字:
    
    
    Image tif = Image.GetInstance(imagepath + "/verticallogo.tif");
     
    tif.ScalePercent(24f);
     
    tif.SetAbsolutePosition(doc.PageSize.Width - 36f - 72f, 
          doc.PageSize.Height - 36f - 216.6f);
     
    doc.Add(tif);

doc.PageSize.Width告诉我文档的宽度为多少像素,我仅仅是从这个宽度中减去了图片宽度\(72px\)和页边距\(36px\).Y轴坐标的设置方法也是遵循了同样的方法:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-07-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111071112155116.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111071112116592.gif)

将我公司的Logo放进去了:-\)

还有的应用场景比如说，你需要在PDF中为用户上传的图片提供一个容器。我使用WinXp中默认带的示例图片“日落”来说明如何使用ScaleToFit\(\)方法实现这个效果.下面代码展示了如何改变一个800 \* 600的图片大小,在不改变其纵横比的情况下将其放入一个250像素长的正方形容器中:
    
    
    Image jpg = Image.GetInstance(imagepath + "/Sunset.jpg");
     
    jpg.ScaleToFit(250f, 250f);
    
    jpg.Border = Rectangle.BOX;
     
    jpg.BorderColor = Color.YELLOW;
     
    jpg.BorderWidth = 5f;
     
    doc.Add(jpg);
     
    doc.Add(new Paragraph("Original Width: " + jpg.Width.ToString()));
    
    doc.Add(new Paragraph("Original Height " + jpg.Height.ToString()));
     
    doc.Add(new Paragraph("Scaled Width: " + jpg.ScaledWidth.ToString()));
    
    doc.Add(new Paragraph("Scaled Height " + jpg.ScaledHeight.ToString()));
     
    float Resolution = jpg.Width / jpg.ScaledWidth * 72f;
     
    doc.Add(new Paragraph("Resolution: " + Resolution));
    
     

上面代码中，我还为嵌入的图片加上了一个5像素宽的黄色边框.并且在下面显示了缩放前和缩放后的大小,还有图片的分辨率，下面是结果:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-07-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111071112182310.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111071112166096.jpg)

如果你使用SetAbsolutePosition\(\)方法和设置Image.UNDERLYING所得到的效果一样的话，除非你想对图片设置水印什么的，否则还是设置Image.TEXTWRAP比较好:
    
    
     
    
    Image jpg = Image.GetInstance(imagepath + "/Sunset.jpg");
     
    Paragraph paragraph = new Paragraph(@"Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Suspendisse blandit blandit turpis. Nam in lectus ut dolor consectetuer bibendum. Morbi neque ipsum, laoreet id; dignissim et, viverra id, mauris. Nulla mauris elit, consectetuer sit amet, accumsan eget, congue ac, libero. Vivamus suscipit. Nunc dignissim consectetuer lectus. Fusce elit nisi; commodo non, facilisis quis, hendrerit eu, dolor? Suspendisse eleifend nisi ut magna. Phasellus id lectus! Vivamus laoreet enim et dolor. Integer arcu mauris, ultricies vel, porta quis, venenatis at, libero. Donec nibh est, adipiscing et, ullamcorper vitae, placerat at, diam. Integer ac turpis vel ligula rutrum auctor! Morbi egestas erat sit amet diam. Ut ut ipsum? Aliquam non sem. Nulla risus eros, mollis quis, blandit ut; luctus eget, urna. Vestibulum vestibulum dapibus erat. Proin egestas leo a metus?");
    
    paragraph.Alignment = Element.ALIGN_JUSTIFIED;
     
    jpg.ScaleToFit(250f, 250f);
     
    jpg.Alignment = Image.TEXTWRAP | Image.ALIGN_RIGHT;
     
    jpg.IndentationLeft = 9f;
     
    jpg.SpacingAfter = 9f;
     
    jpg.BorderWidthTop = 36f;
    
    jpg.BorderColorTop = Color.WHITE;
     
    doc.Add(jpg);
     
    doc.Add(paragraph);

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-07-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111071112212536.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111071112191273.jpg)

上面例子中，我为图片加上了白色的边框并使其居于文本上方.并给图片左方和下方加上了一些内衬距离使其不会紧贴文本.左边和下边的内衬距离可以通过设置IndentationLeft和IndentationRight属性实现,也可以通过SpacingBefore和SpacingAfter来实现.你或许会疑惑我为什么设置白色边框而不是设置SpacingBefore属性,这是个好问题。实际上，我设置了SpacingBefore属性在这个例子中不知道为什么不起作用。如果谁知道，请告诉我为什么，我很乐意知道。

最后，如果你需要将图片进行旋转,可以通过Rotation属性进行。这个属性是float类型的变量用于表示图片旋转的弧度。如果你在学校数学比我学的好的话，下面的例子使用起来会让你更舒服.如果你数学像我一样烂并且见到下面例子会惊叫出”这是虾米?”的话，你可以读[这篇](http://en.wikipedia.org/wiki/Radian)关于度数的文章就能知道Math.PI /2实际上就是90度，或者是设置RotationDegrees属性，这个属性的度数是逆时针的.下面代码中的两种方法实现了相同的效果:
    
    
    jpg.Rotation = (float)Math.PI / 2;
     
    jpg.RotationDegrees = 90f;

\------------------------------

原文链接: [iTextSharp - Working with images](http://www.mikesdotnetting.com/Article/87/iTextSharp-Working-with-images)

Translated by [CareySon](http://www.cnblogs.com/careyson)
