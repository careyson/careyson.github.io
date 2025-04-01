---
layout: post
title: "关于JQuery的serialize方法.让我崩溃一天的问题解决了"
date: 2009-06-26
categories: blog
tags: [博客园迁移]
---

这几天做一个Ajax像服务器动态提交的表单然后给出即时反馈.这些表单内容都是一系列的.内容大同小异.所以代码和页面结构也是大同小异.但是其中有一个页面使用AJAX始终无法提取到服务器值.反而将此页的整个render出来的页面显示出来.关键代码如下:

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ContractedBlock.gif)![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ExpandedBlockStart.gif)Code  
$\(document\).ready\(function\(\) \{  
$\("\#Submit"\).click\(function\(\) \{  
var a = $\("\#aspnetForm"\).serialize\(\);  
/\*因为使用了masterpage,所以页面form的ID为aspnetForm\*/  
$.ajax\(\{  
url: "xxx.aspx",  
type: "get",  
data: a,  
success: function\(data\)\{  
$\("\#result"\).html\(data\);  
\}  
\}\);  
\}\);  
\}\);  


后台代码简略如下.只是为了让大家明白意思:

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ContractedBlock.gif)![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ExpandedBlockStart.gif)Code  
protected void Page\_Load\(object sender, EventArgs e\)  
\{  
if \(Request.QueryString\["length"\] \!= null\)  
\{  
Response.Clear\(\);  
Response.Write\("这里是回传的数据"\);  
Response.End\(\);  
\}  
  
\}

刚开始我挺奇怪.为什么几个页面都好好的.但是这个页面无论如何也无法收到queryString的值,我干脆将jquery代码重写了一遍.问题依旧.

后来发现在IE里不行.但是在FF里却没事..

用IE的httpwatch插件观察.发现表单无法提取到值.百思不得其解.以为是JQuery库的问题.换了.问题依旧.

上了asp.net的论坛和jquery论坛发邮件.有人说是utf-8编码问题.试了.还是无效-.-\!\!

最终我只能用“滚雷"的方法，看为什么其他页面行而这个不行.把一个个的html控件挨个删除.然后用httpwatch观察值,最终发现在

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ContractedBlock.gif)![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ExpandedBlockStart.gif)Code  
<input id="length" type="text" class="txt" name="length" />  


这个html控件上出了问题.如果页面里有这个控件serialize方法就无法提取任何值.

恩.对了.你们也肯定想到了.length是js数组的属性关键字.肯定冲突了.

打开js代码，发现原来serialize是用param方法对serializeArray的一个简单包装.

param方法的js代码:

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ContractedBlock.gif)![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ExpandedBlockStart.gif)Code  
param: function\( a \) \{  
/// <summary>  
/// This method is internal. Use serialize\(\) instead.  
/// </summary>  
/// <param name="a" type="Map">A map of key/value pairs to serialize into a string.</param>'  
/// <returns type="String" />  
/// <private />  
  
var s = \[ \];  
  
function add\( key, value \)\{  
s\[ s.length \] = encodeURIComponent\(key\) + '=' + encodeURIComponent\(value\);  
\};  
  
// If an array was passed in, assume that it is an array  
// of form elements  
if \( jQuery.isArray\(a\) || a.jquery \)  
// Serialize the form elements  
jQuery.each\( a, function\(\)\{  
add\( this.name, this.value \);  
\}\);  
  
// Otherwise, assume that it's an object of key/value pairs  
else  
// Serialize the key/values  
for \( var j in a \)  
// If the value is an array then the key names need to be repeated  
if \( jQuery.isArray\(a\[j\]\) \)  
jQuery.each\( a\[j\], function\(\)\{  
add\( j, this \);  
\}\);  
else  
add\( j, jQuery.isFunction\(a\[j\]\) ? a\[j\]\(\) : a\[j\] \);  
  
// Return the resulting serialization  
return s.join\("&"\).replace\(/%20/g, "+"\);  
\}

serializeArray方法的jquery定义

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ContractedBlock.gif)![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ExpandedBlockStart.gif)Code  
serializeArray: function\(\) \{  
/// <summary>  
/// Serializes all forms and form elements but returns a JSON data structure.  
/// </summary>  
/// <returns type="String">A JSON data structure representing the serialized items.</returns>  
  
return this.map\(function\(\)\{  
return this.elements ? jQuery.makeArray\(this.elements\) : this;  
\}\)  
.filter\(function\(\)\{  
return this.name && \!this.disabled &&  
\(this.checked || /select|textarea/i.test\(this.nodeName\) ||  
/text|hidden|password|search/i.test\(this.type\)\);  
\}\)  
.map\(function\(i, elem\)\{  
var val = jQuery\(this\).val\(\);  
return val == null ? null :  
jQuery.isArray\(val\) ?  
jQuery.map\( val, function\(val, i\)\{  
return \{name: elem.name, value: val\};  
\}\) :  
\{name: elem.name, value: val\};  
\}\).get\(\);  
\}

发现问题都不出在这两个函数上.继续跟踪..发现问题出在这serializeArray方法里调用的makeArray方法上

JQuery定义如下

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ContractedBlock.gif)![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-06-26-jquery-serialize/jquery-serialize-ExpandedBlockStart.gif)Code  
makeArray: function\( array \) \{  
/// <summary>  
/// Turns anything into a true array. This is an internal method.  
/// </summary>  
/// <param name="array" type="Object">Anything to turn into an actual Array</param>  
/// <returns type="Array" />  
/// <private />  
  
var ret = \[\]; if\( array \!= null \)\{  
  
  
var i = array.length;  
//问题就出在这  
if\( i == null || typeof array === "string" || jQuery.isFunction\(array\) || array.setInterval \)  
ret\[0\] = array;  
else  
while\( i \)  
ret\[\--i\] = array\[i\];  
\}  
  
return ret;  
\}

自习看makeArray的代码.发现这行

var i = array.length;  
问题就处在这

因为变量i是取传入的array数组的长度.

而我们知道.js中的array本质上就是一个对象.所以array\["length"\]和array.length是同一种东西

所以当我将textbox中的id设置为length时.这时就会和对象的length属性重名.造成变量I在下面的计算中出错.自然就返回空了.

解决方法：将textbox的ID换成其他的值

\-----------------------------------------------------------

写在后面：这个问题让我快用头撞墙了.刚开始还以为是灵异现象.重启动了好几次-.-\!\!

分享一下.希望对大家有帮助.
