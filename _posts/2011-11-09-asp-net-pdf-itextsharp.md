---
layout: post
title: "【译】在Asp.Net中操作PDF - iTextSharp - 利用列进行排版"
date: 2011-11-09
categories: blog
tags: [博客园迁移]
---

在使用iTextSharp通过ASP.Net生成PDF的系列文章中，前面的文章已经讲述了iTextSharp所涵盖的大多数基本功能.本文主要讲述通过另外一种方法来对文档进行排版，那就是使用列\(columns\).本系列之前的文章如下:

[在ASP.NET中创建PDF-iTextSharp起步](http://www.cnblogs.com/CareySon/archive/2011/11/02/2233174.html)

[在Asp.Net中操作PDF - iTextSharp - 使用字体](http://www.cnblogs.com/CareySon/archive/2011/11/03/2234342.html)

[在Asp.Net中操作PDF – iTextSharp -利用块，短语，段落添加文本](http://www.cnblogs.com/CareySon/archive/2011/11/03/2234625.html)

[在Asp.Net中操作PDF – iTextSharp-列表](http://www.cnblogs.com/CareySon/archive/2011/11/04/2235834.html)

[在Asp.Net中操作PDF – iTextSharp - 使用链接和书签](http://www.cnblogs.com/CareySon/archive/2011/11/04/2236239.html)

[在Asp.Net中操作PDF – iTextSharp - 使用表格](http://www.cnblogs.com/CareySon/archive/2011/11/05/2237116.html)

[在Asp.Net中操作PDF – iTextSharp - 操作图片](http://www.cnblogs.com/CareySon/archive/2011/11/07/2239017.html)

[在Asp.Net中操作PDF - iTextSharp - 绘制矢量图](http://www.cnblogs.com/CareySon/archive/2011/11/08/2241154.html)

通常情况下.当你使用列时你都会喜欢使用多个列对文字进行排版。就像报纸那样。iTextSharp提供了MultiColumn对象使得实现多列排版变得非常简单。你仅仅需要告诉MultiColumn对象第一列的X轴坐标，第二列的X轴坐标，第二列结束的X轴坐标，列和列之间的距离，以及你需要多少列,下面代码在当前文档中加入两列，并在其内加入8次同样的段落\(paragraph\):
    
    
    string pdfpath = Server.MapPath("PDFs");
     
    string imagepath = Server.MapPath("Columns");
     
    Document doc = new Document();
     
    try
     
    {
     
        PdfWriter.GetInstance(doc, new FileStream(pdfpath + "/Columns.pdf", FileMode.Create));
     
       doc.Open();
     
        Paragraph heading = new Paragraph("Page Heading", new Font(Font.HELVETICA, 28f, Font.BOLD));
     
       heading.SpacingAfter = 18f;
     
       doc.Add(heading);
     
        string text = @"Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Suspendisse blandit blandit turpis. Nam in lectus ut dolor consectetuer bibendum. Morbi neque ipsum, laoreet id; dignissim et, viverra id, mauris. Nulla mauris elit, consectetuer sit amet, accumsan eget, congue ac, libero. Vivamus suscipit. Nunc dignissim consectetuer lectus. Fusce elit nisi; commodo non, facilisis quis, hendrerit eu, dolor? Suspendisse eleifend nisi ut magna. Phasellus id lectus! Vivamus laoreet enim et dolor. Integer arcu mauris, ultricies vel, porta quis, venenatis at, libero. Donec nibh est, adipiscing et, ullamcorper vitae, placerat at, diam. Integer ac turpis vel ligula rutrum auctor! Morbi egestas erat sit amet diam. Ut ut ipsum? Aliquam non sem. Nulla risus eros, mollis quis, blandit ut; luctus eget, urna. Vestibulum vestibulum dapibus erat. Proin egestas leo a metus?";
     
        MultiColumnText columns = new MultiColumnText();
     
        //float left, float right, float gutterwidth, int numcolumns
     
       columns.AddRegularColumns(36f, doc.PageSize.Width-36f, 24f, 2);
     
        Paragraph para = new Paragraph(text, new Font(Font.HELVETICA, 8f));
     
       para.SpacingAfter = 9f;
     
       para.Alignment = Element.ALIGN_JUSTIFIED;
     
        for (int i = 0; i < 8; i++)
     
        {
     
           columns.AddElement(para);
     
        }
     
        
     
       doc.Add(columns);
     
        
     
    }
     
    catch (Exception ex)
     
    {
     
       //Log(ex.Message);
     
    }
     
    finally
     
    {
     
       doc.Close();
     
    }

下面结果展示了当文本从一个列中溢出后额外的文本自动填充到第二列:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-09-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111091405286725.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111091405274348.gif)

AddRegularColumns\(\)方法会将其设置的每一列设置成相同的宽度,而AddSimpleColumn\(\)方法允许你对单个列设置宽度，也就是你可以添加非常规列:
    
    
    columns.AddSimpleColumn(36f, 170f);
     
    columns.AddSimpleColumn(194f, doc.PageSize.Width - 36f);

上面的代码取代了在前一个代码段中的AddRegularColumn\(\)方法来创建两个列.第一列距左36像素,2英尺宽\(170 - 36 = 144\),第二列在第一列的基础上向右24像素\(3分之一英尺\),结束于距离右边距36像素:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-09-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111091405301510.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111091405295753.gif)

在列中加入其他比如图片和表格的元素也是非常简单:
    
    
    string pdfpath = Server.MapPath("PDFs");
     
    string imagepath = Server.MapPath("Images");
     
    Document doc = new Document();
     
    try
     
    {
     
      PdfWriter.GetInstance(doc, new FileStream(pdfpath + "/Columns.pdf", FileMode.Create));
     
      doc.Open();
     
      Paragraph heading = new Paragraph("Page Heading", new Font(Font.HELVETICA, 28f, Font.BOLD));
     
      heading.SpacingAfter = 18f;
     
      doc.Add(heading);
     
      string text = @"Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Suspendisse blandit blandit turpis. Nam in lectus ut dolor consectetuer bibendum. Morbi neque ipsum, laoreet id; dignissim et, viverra id, mauris. Nulla mauris elit, consectetuer sit amet, accumsan eget, congue ac, libero. Vivamus suscipit. Nunc dignissim consectetuer lectus. Fusce elit nisi; commodo non, facilisis quis, hendrerit eu, dolor? Suspendisse eleifend nisi ut magna. Phasellus id lectus! Vivamus laoreet enim et dolor. Integer arcu mauris, ultricies vel, porta quis, venenatis at, libero. Donec nibh est, adipiscing et, ullamcorper vitae, placerat at, diam. Integer ac turpis vel ligula rutrum auctor! Morbi egestas erat sit amet diam. Ut ut ipsum? Aliquam non sem. Nulla risus eros, mollis quis, blandit ut; luctus eget, urna. Vestibulum vestibulum dapibus erat. Proin egestas leo a metus?";
     
      MultiColumnText columns = new MultiColumnText();
     
      columns.AddSimpleColumn(36f, 336f);
     
      columns.AddSimpleColumn(360f, doc.PageSize.Width - 36f);
     
      
     
      Paragraph para = new Paragraph(text, new Font(Font.HELVETICA, 8f));
     
      para.SpacingAfter = 9f;
     
      para.Alignment = Element.ALIGN_JUSTIFIED;
     
      
     
      PdfPTable table = new PdfPTable(3);
     
      float[] widths = new float[] { 1f, 1f, 1f };
     
      table.TotalWidth = 300f;
     
      table.LockedWidth = true;
     
      table.SetWidths(widths);
     
      PdfPCell cell = new PdfPCell(new Phrase("Header spanning 3 columns"));
     
      cell.Colspan = 3;
     
      cell.HorizontalAlignment = 0;
     
      table.AddCell(cell);
     
      table.AddCell("Col 1 Row 1");
     
      table.AddCell("Col 2 Row 1");
     
      table.AddCell("Col 3 Row 1");
     
      table.AddCell("Col 1 Row 2");
     
      table.AddCell("Col 2 Row 2");
     
      table.AddCell("Col 3 Row 2");
     
      
     
      Image jpg = Image.GetInstance(imagepath + "/Sunset.jpg");
     
      jpg.ScaleToFit(300f, 300f);
     
      jpg.SpacingAfter = 12f;
     
      jpg.SpacingBefore = 12f;
     
      
     
      columns.AddElement(para);
     
      columns.AddElement(table);
     
      columns.AddElement(jpg);
     
      columns.AddElement(para);
     
      columns.AddElement(para);
     
      columns.AddElement(para);
     
      columns.AddElement(para);
     
      doc.Add(columns);
     
      
     
    }
     
    catch (Exception ex)
     
    {
     
      //Log(ex.Message);
     
    }
     
    finally
     
    {
     
      doc.Close();
     
    }
     
     

上面例子中传入了我们之前文章中讲的图片和表格对象,将其和文本一起加入到列中.上面第一列是300像素宽，而第二列占据了页面剩下的区域:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-09-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111091405323264.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111091405311411.gif)

MultiColumnText对象可以让你只需要写很少的代码的情况下创建列，但其缺乏对列内元素的具体控制力.而与之相反的是，ColumnText对象提供了更多的控制力，但需要写更多的代码。下面例子中使用ColumnText对象创建非常规列，第一个列的左上角留出一块空余的地方来容纳一个图片，效果如下：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-11-09-asp-net-pdf-itextsharp/asp-net-pdf-itextsharp-201111091405349162.gif)](http://images.cnblogs.com/cnblogs_com/CareySon/201111/201111091405331213.gif)
    
    
    string pdfpath = Server.MapPath("PDFs");
     
    string imagepath = Server.MapPath("Images");
     
    FontFactory.RegisterDirectory("C:\\WINDOWS\\Fonts");
     
     
     
    Document doc = new Document();
     
    Font font1 = new Font(FontFactory.GetFont("adobe garamond pro", 36f, Color.GRAY));
     
    Font font2 = new Font(Font.TIMES_ROMAN, 9f);
     
    doc.SetMargins(45f, 45f, 60f, 60f);
     
    try
     
    {
     
      FileStream output = new FileStream(pdfpath + "/IrregularColumns.pdf", FileMode.Create);
     
      PdfWriter writer = PdfWriter.GetInstance(doc, output);
     
      doc.Open();
     
      PdfContentByte cb = writer.DirectContent;
       ColumnText ct = new ColumnText(cb);
     
      ct.Alignment = Element.ALIGN_JUSTIFIED;
     
     
     
      Paragraph heading = new Paragraph("Chapter 1", font1);
     
      heading.Leading = 40f;
     
      doc.Add(heading);
     
      Image L = Image.GetInstance(imagepath + "/l.gif");
     
      L.SetAbsolutePosition(doc.Left, doc.Top - 180);
     
      doc.Add(L);
     
     
     
      ct.AddText(new Phrase("orem ipsum dolor sit amet, consectetuer adipiscing elit. Suspendisse blandit blandit turpis. Nam in lectus ut dolor consectetuer bibendum. Morbi neque ipsum, laoreet id; dignissim et, viverra id, mauris. Nulla mauris elit, consectetuer sit amet, accumsan eget, congue ac, libero. Vivamus suscipit. Nunc dignissim consectetuer lectus. Fusce elit nisi; commodo non, facilisis quis, hendrerit eu, dolor? Suspendisse eleifend nisi ut magna. Phasellus id lectus! Vivamus laoreet enim et dolor. Integer arcu mauris, ultricies vel, porta quis, venenatis at, libero. Donec nibh est, adipiscing et, ullamcorper vitae, placerat at, diam. Integer ac turpis vel ligula rutrum auctor! Morbi egestas erat sit amet diam. Ut ut ipsum? Aliquam non sem. Nulla risus eros, mollis quis, blandit ut; luctus eget, urna. Vestibulum vestibulum dapibus erat. Proin egestas leo a metus?\n\n", font2));
     
      ct.AddText(new Phrase("Vivamus enim nisi, mollis in, sodales vel, convallis a, augue? Proin non enim. Nullam elementum euismod erat. Aliquam malesuada eleifend quam! Nulla facilisi. Aenean ut turpis ac est tempor malesuada. Maecenas scelerisque orci sit amet augue laoreet tempus. Duis interdum est ut eros. Fusce dictum dignissim elit. Morbi at dolor. Fusce magna. Nulla tellus turpis, mattis ut, eleifend a, adipiscing vitae, mauris. Pellentesque mattis lobortis mi.\n\n", font2));
     
      ct.AddText(new Phrase("Nullam sit amet metus scelerisque diam hendrerit porttitor. Aenean pellentesque, lorem a consectetuer consectetuer, nunc metus hendrerit quam, mattis ultrices lorem tellus lacinia massa. Aliquam sit amet odio. Proin mauris. Integer dictum quam a quam accumsan lacinia. Pellentesque pulvinar feugiat eros. Suspendisse rhoncus. Sed consectetuer leo eu nisi. Suspendisse massa! Sed suscipit lacus sit amet elit! Aliquam sollicitudin condimentum turpis. Nunc ut augue! Maecenas eu eros. Morbi in urna consectetuer ipsum vehicula tristique.\n\n", font2));
     
      ct.AddText(new Phrase("Donec imperdiet purus vel ligula. Vestibulum tempor, odio ut scelerisque eleifend, nulla sapien laoreet dui; vel aliquam arcu libero eu ante. Curabitur rutrum tristique mi. Sed lobortis iaculis arcu. Suspendisse mauris. Aliquam metus lacus, elementum quis, mollis non, consequat nec, tortor.\n", font2));
     
      ct.AddText(new Phrase("Quisque id diam. Ut egestas leo a elit. Nulla in metus. Aliquam iaculis turpis non augue. Donec a nunc? Phasellus eu eros. Nam luctus. Duis eu mi. Ut mollis. Nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Aenean pede. Nulla facilisi. Vestibulum mattis adipiscing nulla. Praesent orci ante, mattis in, cursus eget, posuere sed, mauris.\n\n", font2));
     
      ct.AddText(new Phrase("Nulla facilisi. Nunc accumsan risus aliquet quam. Nam pellentesque! Aenean porttitor. Aenean congue ullamcorper velit. Phasellus suscipit placerat tellus. Vivamus diam odio, tempus quis, suscipit a, dictum eu; lectus. Sed vel nisl. Ut interdum urna eu nibh. Praesent vehicula, orci id venenatis ultrices, mauris urna mollis lacus, et blandit odio magna at enim. Pellentesque lorem felis, ultrices quis, gravida sed, pharetra vitae, quam. Mauris libero ipsum, pharetra a, faucibus aliquet, pellentesque in, mauris. Cras magna neque, interdum vel, varius nec; vulputate at, erat. Quisque vitae urna. Suspendisse potenti. Nulla luctus purus at turpis! Vestibulum vitae dui. Nullam odio.\n\n", font2));
     
      ct.AddText(new Phrase("Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Sed eget mi at sem iaculis hendrerit. Nulla facilisi. Etiam sed elit. In viverra dapibus sapien. Aliquam nisi justo, ornare non, ultricies vitae, aliquam sit amet, risus! Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Phasellus risus. Vestibulum pretium augue non mi. Sed magna. In hac habitasse platea dictumst. Quisque massa. Etiam viverra diam pharetra ante. Phasellus fringilla velit ut odio! Nam nec nulla.\n\n", font2));
     
      ct.AddText(new Phrase("Integer augue. Morbi orci. Sed quis nibh. Nullam ac magna id leo faucibus ornare. Vestibulum eget lectus sit amet nunc facilisis bibendum. Donec adipiscing convallis mi. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Vivamus enim. Mauris ligula lorem, pellentesque quis, semper sed, tristique sit amet, justo. Suspendisse potenti. Proin vitae enim. Morbi et nisi sit amet sapien ve.\n\n", font2));
     
     
     
      float gutter = 15f;
     
      float colwidth = (doc.Right - doc.Left - gutter) / 2;
     
      float[] left = { doc.Left + 90f , doc.Top - 80f, 
    
                      doc.Left + 90f, doc.Top - 170f,
     
                      doc.Left, doc.Top - 170f,
     
                      doc.Left , doc.Bottom };
     
     
     
      float[] right = { doc.Left + colwidth, doc.Top - 80f,
     
                        doc.Left + colwidth, doc.Bottom };
     
     
     
      float[] left2 = { doc.Right - colwidth, doc.Top - 80f,
     
                        doc.Right - colwidth, doc.Bottom };
     
     
     
      float[] right2 = {doc.Right, doc.Top - 80f,
     
                        doc.Right, doc.Bottom };
     
     
     
      int status = 0;
     
      int i = 0;
     
      //Checks the value of status to determine if there is more text
     
      //If there is, status is 2, which is the value of NO_MORE_COLUMN
     
      while (ColumnText.HasMoreText(status))
     
      {
     
        if (i == 0)
     
        {
     
          //Writing the first column
     
          ct.SetColumns(left, right);
     
          i++;
     
        }
     
        else
     
        {
     
          //write the second column
     
          ct.SetColumns(left2, right2);
     
        }
     
        //Needs to be here to prevent app from hanging
     
        ct.YLine = doc.Top - 80f;
     
        //Commit the content of the ColumnText to the document
     
        //ColumnText.Go() returns NO_MORE_TEXT (1) and/or NO_MORE_COLUMN (2)
     
        //In other words, it fills the column until it has either run out of column, or text, or both
     
        status = ct.Go();
     
      }
     
    }
     
    catch (Exception ex)
     
    {
     
      //Log(ex.Message);
     
    }
     
    finally
     
    {
     
      doc.Close();
     
    }

ColumnText对象需要你使用PDFContentByte对象，就像前文矢量图里用过的那样.这基本是在你需要将一些东西放到固定位置时都需要的对象.上面代码在开始定义了一个document对象，并且创建了一些字体,设置了文档的页边距\(这一步需要在文档打开前进行）。创建的PdfWriter对象的DirectContent属性用于获取PDFContentByte对象的实例.然后创建了ColumnText对象。再然后添加了一个标题，为首字母L设置大些，随之添加了一些段落。

现在ColumnText对象已经有了文本内容，但还没有地方放。所以接下来我创建了两个列。第一个float数组用于设置第一个段落左上角的边距使其为要嵌入的图片腾出位置。第二个数组定义距离右边距的距离。第三个数组定义了第二列的样子。我们还创建了两个int类型来标识列内是否能加入更多文本\(s\)和当前的列数\(i\)。

ColumnText.HasMoreText\(status\)是一个接受int类型参数的很方便使用的函数。参数取决于是否有更多文本被加入到当前列，如果有，则返回true。false的值为1,这个函数一开始将返回值设置为0,所以这里HasMoreText返回true。因为变量i也同样为0,所以代码往下执行时，先加入第一列,然后将YLine设置到列的顶端,这一步是必须的，否则，程序就会一直等待直到超时.最后，调用了ColumnText.Go\(\)方法,这一步实际上也就是将ColumnText对象中的内容提交到文档，最后将其返回值赋值给变量status。这个返回值可以是NO\_MORE\_TEXT也就是1,或是NO\_MORE\_COLUMN \(2\),如果GO\(\)方法的返回值是NO\_MORE\_TEXT,则将所有内容提交到文档，否则就会创建第二个列，将剩余文本加入到第二列中。直到ColumnText.HasMoreText是false为止，再将内容写入文档。

基于此，如果文本的数量大于1页，则还会调用Document.NewPage\(\)方法，如果每加入一个Phrase都调用一次Go\(\)方法，我们还可以通过Y坐标的值来知道剩余页面空间的大小。这允许你管理页面窗口和被遗落的文本（也就是当只有一行文本溢出当前页面，这行文本应该被加到当前页面而不是新生成一页）。我们甚至还可以传入False作为参数到Go\(\)方法，这表明当前文本不被加入到列中，虽然如此，但是这种方法还是允许你获取到加入文本后Y的坐标.这样一来，你就能更好的控制页面布局了。

\-----------------------------------

原文链接:[iTextSharp - Page Layout with Columns](http://www.mikesdotnetting.com/Article/89/iTextSharp-Page-Layout-with-Columns)

Translated by [CareySon](http://www.cnblogs.com/careyson)
