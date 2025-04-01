---
layout: post
title: "Asp.net控件开发学习笔记(七)----WebControl基类"
date: 2009-10-10
categories: blog
tags: [博客园迁移]
---

**WebControl****基类******

**** 在Asp.net控件开发中，WebControl基类给我们提供了对于控件的Style更加灵活的解决方案，因为在System.Web.UI.Control基类中只能手动的输入呈现在客户端的代码，但如果开发的服务器控件对style的要求较高。那Control基类的局限性就显而易见了，而继承WebControl类作为基类将会是很好的选择。

System.web.UI.WebControls.Webcontrol直接继承与Control类。在继承了Control的特性的基础上，WebControl基类不仅在生成客户端html使用了另一种更好的render方式，并且还提供了对于老版本浏览器的兼容。

**WebControl****的 ControlStyle****属性**

****

**** ControlStyle属性其实是System.Web.UI.WebControls.Style的一个实例，这个属性用于读取或者设置常用的CSS类，以下是System.Web.UI.WebControls.Style的属性和CSS属性的对应关系。

**Style****的属性** |  **CSS****标准属性**  
---|---  
**BackColor******|  background-color  
**BorderColor******|  border-color  
**BorderStyle******|  border-style  
**BorderWidth******|  border-width  
**CssClass******|  CSS的类名  
**Font******|  Font weight, style, family, and so on  
**ForeColor******|  color  
**Height** |  height  
**width** |  width  
  
而在ControlStyle.Font是一些设置字体的属性，是System.Web.UI.FontInfo对象的实例。和标准CSS属性的对照如下表：

**Font****属性** |  **CSS****标准属性**  
---|---  
**Bold******|  font-weight: bold  
**Italic******|  font-style: italic  
**Name******|  font-family  
**Names******|  font-family  
**Overline******|  text-decoration: overline  
**Underline** |  text-decoration: underline  
**Size******|  font-size  
**Strikeout******|  text-decoration: line-through  
  
**WebControl****基类 ControlStyle****属性的简化**

**** 下面这行代码:

webcontrol.ControlStyle.BorderWidth = 1;

和

webcontrol.BorderWidth = 1;

代码是等价的，WebControl基类可以不通过ControlStyle属性而访问ControlStyle内的成员，这样在前台可以直接对控件进行style设置，刚才的后台代码于如下前台代码是等价的：

<cc:WebControl id="WebControl" runat="server" borderwidth="1"/>

**WebControl****的****Style****属性******

因为ControlStyle属性只暴露了一部分可用于操控CSS的属性，而除了上述ControlStyle暴露的基本的CSS属性设置之外，WebControl基类还为我们提供了Style属性用于对CSS进行精确完整的操作，可以用如下图让概念更加清晰:

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-10-10-asp-net-webcontrol/asp-net-webcontrol-7-1.jpg)  
Style属性是System.Web.UI.CssStyleCollection这个类的实例，style属性大多在.aspx文件中用到，比如:

<asp:Button ID="Button1" runat="server" Text="Button" style=" background:blue;" />

而与上面对Style赋值等价的后台代码则是：

Button1.Style\["background"\] = "blue";

或者

Button1.Style.Add\("background", "blue"\);

**一个新的****Render****系统******

**** 和集成Control并重写Render方法不同，WebControl给我们提供了一个新的系统用于Render控件。下面写一个Label的Demo：

**Demo:label****控件******

代码如下:

\[ToolboxData\("<\{0\}:label runat=server></\{0\}:label>"\),DefaultProperty\("Text"\)\]

public class Label : WebControl

\{

public Label\(\): base\(HtmlTextWriterTag.Span\)

\{

\}

public virtual string Text

\{

get

\{

object text = ViewState\["Text"\];

if \(text == null\)

return string.Empty;

else

return \(string\)text;

\}

set

\{

ViewState\["Text"\] = value;

\}

\}

override protected void RenderContents\(HtmlTextWriter writer\)

\{

writer.Write\(Text\);

\}

\}

在构造函数中，我们可以看出public Label\(\): base\(HtmlTextWriterTag.Span\)和从前继承于Control基类的方式有所不同，通过HtmlTextWriterTag枚举对象，我们所有生成的内容都会在Html的<span>标签内.而在最后用RednerContents函数来render内容时并不需要自己写相应的html标签，而是构造函数内的选择了span，则webcontrol帮你生成相应的html标签。

WebControl本身内置的render系统分为四个函数，依次进行，可以用下图表示：   


![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-10-10-asp-net-webcontrol/asp-net-webcontrol-7-2.jpg)  
其中AddAttributesToRender函数在后面说到，根据顺序我们可以发现，WebControl在生成Html方面要大大强于Control基类的生成方式。就这个Label控件来说，生成的过程会是

1:RenderBeginTag

根据HtmlTextWriterTag枚举类型来确定生成的html标签的种类，在这里这个方法会生成

<span

2:AddAttributesToRender函数生成控件相关的html属性在这里可能会接着上面生成

<span title=”xx”

3:renderContents函数生成控件中的内容，在这个Label控件会接着生成类似如下：

<span title=”xx”>这里是文本内容

4：RenderEndTag这个函数也是根据HtmlTextWriteTag枚举来确定生成的html关闭标签，在这里会接着上面生成：

<span title=”xx”>这里是文本内容</span>

因为在这个Demo中我们只覆盖了RenderContents函数，而没有涉及到AddAttributesToRedner函数,而RenderBeginTag和RenderEndTag会根据基类构造函数中的HtmlTextWriterTag枚举类型生成相应的html标签.如果在前台这么用这个控件：

<asp:Label runat="server" Text="测试Text"></asp:Label>

则render后生成相应的Html代码是:

<span>测试Text</span>

这样的render方式.可以让你省去手动输入html，而只需要重载你需要自己实现的步骤。在通常情况下RenderBeginTag和RenderEndTag几乎很少被重载。而被重载最多的也就是AddAttributeToRender和RenderContents方法.

**AddAttributeToRender****方法**

**** AddAttributeToRender方法是最常用的,这个方法通过键/值对添加属性，比如前几章的TextBox控件，如果Render的过程中引入了这个方法，那么会容易很多.页面的Render部分只需要如下一些代码即可:

public Textbox\(\): base\(HtmlTextWriterTag.Input\)

\{

\}

override protected void AddAttributesToRender\(HtmlTextWriter writer\)

\{

writer.AddAttribute\("type", "text"\);

writer.AddAttribute\("name", UniqueID\);

writer.AddAttribute\("value", Text\);

base.AddAttributesToRender\(writer\);

\}

需要特别注意的是，在override AddAttributesToRedner方法时，一定不要忘了加上最后的那句base.AddAttributesToRender\(writer\);

****
