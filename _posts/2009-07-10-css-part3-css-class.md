---
layout: post
title: "写自己的CSS框架 Part3:CSS中的Class"
date: 2009-07-10
categories: blog
tags: [博客园迁移]
---

Tool make everything easier….

Anonymity

**3.1****框架中的工具******

这个CSS中工具有点像C\#中的static class,把一些常用的方法放到类里面达到可复用的效果.在CSS中.有很多CSS class是在我们在项目设计中一遍又一遍的要用到的.因此这些tool是CSS框架中必不可少的一部分。

**3.2****工具类的组成和组织方法******

一般现有框架会把这个.class的定义放到各个不同的文件中比如，from.css\(用于格式化表单\)，typography.css（用于格式化布局）,但是这个工具类却是我们自己写框架的精髓所在，因为这是我们框架中可以扩展的部分,所以我更喜欢把css class单独命名为tool.css来存放这些工具类.（因为这样在网站改版时就要愉快很多）

也许废话太多了.下面简单给出几行代码,让大家对所谓的Tool.css有初步了解。

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-07-10-css-part3-css-class/css-part3-css-class-ContractedBlock.gif)![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-07-10-css-part3-css-class/css-part3-css-class-ExpandedBlockStart.gif)Code  
1 /\* 用于格式化Form的CSS Tool  
2   
3 \-------------------------------------------------------------- \*/  
4   
5   
6   
7 .error,  
8   
9 .notice,   
10   
11 .success \{ padding: .8em; margin-bottom: 1em; border: 2px solid \#ddd; \}  
12   
13   
14   
15 .error \{ background: \#FBE3E4; color: \#8a1f11; border-color: \#FBC2C4; \}  
16   
17 .notice \{ background: \#FFF6BF; color: \#514721; border-color: \#FFD324; \}  
18   
19 .success \{ background: \#E6EFC2; color: \#264409; border-color: \#C6D880; \}  
20   
21   
22

这是用于表单的一些CSS类.有了这些.我可以让项目中每一个使用表单的地方风格实现统一.

而使用JS的地方可以更加简洁.下面一小部分代码是使用了JQUERY从服务器获得AJAX响应后的代码片段

Success:function\(data\)\{

$\(“<span>”+data+”</span>”\).addClass\(“success”\).appendTo\(“\#result”\);

\}

恩.是不是简单多了？

PS:看客：你不是号称CSS框架吗.这样写不就是把css放一起吗？吹的那么玄乎.

别急嘛.下面讲到CSS之间的组织方式

在我被CSS蹂躏的经历里，其实有很多CSS布局,以及CSS选择符方面问题，大部分是因为CSS选择符之间优先级的关系，这些问题因为简单，所以折磨的各位Developer痛不欲生.但是这些问题就像枪一样，好好利用可以保护你，如果利用不当会让你遭殃。

下面说说我总结的CSS的OCP原则（开放封闭原则），这个规则是设计模式里的，但我发现在CSS中同样适用.

**当你针对项目的****CSS****基本框架写好后，可以添加你所需要的元素，但如非必要，不要去修改它，而是在需要修改的地方重载。******

重载:

以上面的例子为例.如果我们在一个特定页面里，想让error颜色变得更加刺眼比如让error的color变成red，只需在你需要修改的特定页面头部的<style>标签中设置

1 .error\{  
2   
3 Color:red;  
4   
5 \}  
6

因为内页style比外联style有更高的权值（如果你对CSS的优先级问题不太了解，参考这个文章http://www.xker.com/page/e2009/0622/72573.html），所以error显示的字就会变成红的，但同时又会保留了background和border-color的属性.因此我可以更优雅的覆盖原有CSS，达到重载的目的.

扩展:

当我们需要一组新的css类时,只需要在tool.css相应部分增加即可，比如我们需要表单增加一个介于notice和error之间警告程度的alert用于显示那些有点警告意味的信息.我们只需要加入

1 .alert  
2   
3 \{   
4   
5 /\*\------代码写在这----\*/  
6   
7 \}  
8

这样做的优势:

1. 代码更加优雅,维护更加方便

2. 容易变换网站风格，举个例子，如果你原来的颜色风格偏深，那么你想换一套浅颜色的风格，只需要改变你所需要改变的部分，把你需要改变的部分重新写一个CSS来覆盖原来的CSS，示例代码如下:

<link href="css/tool.css" rel="stylesheet" type="text/css" />   
<link href="css/toolBlue.css" rel="stylesheet" type="text/css" />  


这样看起来tool.css是不是很“面向对象”,很像基类，而toolBlue像子类，继承那些padding和magin之类的布局属性，而重载color等风格属性,oh yes,life seems like more easier than ever bofore：-）

**3.3****写在最后******

下面我拿出一个简单的tool.css展示出来，让大家有个更直观的了解。

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-07-10-css-part3-css-class/css-part3-css-class-ContractedBlock.gif)![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-07-10-css-part3-css-class/css-part3-css-class-ExpandedBlockStart.gif)Code  
/\*用于格式化Form的CSS Tool  
  
\-------------------------------------------------------------- \*/  
  
  
  
.error,  
  
.notice,   
  
.success \{ padding: .8em; margin-bottom: 1em; border: 2px solid \#ddd; \}  
  
  
  
.error \{ background: \#FBE3E4; color: \#8a1f11; border-color: \#FBC2C4; \}  
  
.notice \{ background: \#FFF6BF; color: \#514721; border-color: \#FFD324; \}  
  
.success \{ background: \#E6EFC2; color: \#264409; border-color: \#C6D880; \}  
  
.error a \{ color: \#8a1f11; \}  
  
.notice a \{ color: \#514721; \}  
  
.success a \{ color: \#264409; \}  
  
/\*用于布局方面的css tool  
  
\-------------------------------------------------------------- \*/  
  
.clear \{  
  
clear: both;  
  
display: block;  
  
overflow: hidden;  
  
visibility: hidden;  
  
width: 0;  
  
height: 0;  
  
\}  
  
.clearfix \{  
  
display: inline-block;  
  
\}  
  
//用于显示方框，实际应用中我喜欢加边框  
  
.box \{   
  
padding: 1.5em;   
  
margin-bottom: 1.5em;   
  
background: \#E5ECF9;   
  
\}  
  
/\*根据项目自定义的css tool  
  
\-------------------------------------------------------------- \*/  
  
  
  
//以下几个是用于和js交互时使用  
  
.hide \{ display: none; \}  
  
.highlight \{ background:\#ff0; \}  
  
.added \{ background:\#060; color: \#fff; \}  
  
.removed \{ background:\#900; color: \#fff; \}  
  
//下面是关于字体的  
  
.small \{  
  
font-size: .8em;;   
  
\}  
  
.large \{  
  
font-size: 1.2em;   
  
\}  
  
//还有其他你自定义的class….etc…  


恩.基本经常要用到的就是这些，但tool.css的重点在于随着你项目的进展，这个tool.css也会越来越胖. J
