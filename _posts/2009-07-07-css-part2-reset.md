---
layout: post
title: "写自己的CSS框架 Part2:跨越浏览器的reset"
date: 2009-07-07
categories: blog
tags: [博客园迁移]
---

One world,one dream

\---slogan of 2008 Olympic

**2.1****浏览器的差异在何处******

****

**** 我想写CSS的人大多遇见过在IE里写的页面美轮美奂，而用FF打开却是分崩离析，反之亦然.这种痛苦是因为IE和FF对一些默认样式的解析并不相同所导致.

网上有很多为何不一样的例子，下面链接是一个比较全的不同之处，大家可以进去看看。

[http://hi.baidu.com/css%D6%AE%C3%C0/blog/item/f44628e6a506c229b83820ef.html](http://hi.baidu.com/css%D6%AE%C3%C0/blog/item/f44628e6a506c229b83820ef.html)

**2.2****如何实现跨浏览器******

**2.2.1****实现原理******

**** 既然问题出在FF和IE对各种不同HTML元素的解析上所有偏差.更不用说一些其他小市场份额的浏览器上.我们只需要针对性的把页面里大多数HTML元素重置即可.这样在各种浏览器里面显示的效果会是相同的.

**2.2.2****实现方式******

**** 重置我们选择的名称和大多数框架一样,reset.css,用我们Develper的思想理解—-----框架中所有元素的基类,就像.net里的Object对象一样。

下面我们来说说reset.css的构成.

1. 首先定义最基本的body,因为所有其他元素都由此继承.我喜欢的框架遵循“尽量保持小”的原则，所以我只简单清除padding和margin,以及设置字体\(设置成具体数值，因为在后面用’em’做单位的时候都要以这里做比较,页面风格需要整体变化时,重载这里.\)

2. 将大量浏览器预定义的块状元素清除magin和padding\(块装元素即在未定义样式的情况下浏览器render出来的方式为display:block;的元素\)

3. 让列表前面的符号消失,图片边框消失,p的上下边距为一行字.

我喜欢reset.css尽量保持简洁.只要实现了基本的重置即可.

PS:不过也不能过于简洁.记得曾经的框架喜欢对”\*”这个CSS选择符重置.可是这个杀伤力太大，往往是杀敌1000自伤800，遇到input之类的表单元素时还得重置回来.最后据传说这样还有性能问题-.-\!\!不过难以考证…

下面是满足上面条件最基本的reset.css

![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-07-07-css-part2-reset/css-part2-reset-ContractedBlock.gif)![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-07-07-css-part2-reset/css-part2-reset-ExpandedBlockStart.gif)Code  
1.body \{   
  
2\. padding: 0;   
  
3\. margin: 0;   
  
4\. font: 13px Arial, sans-serif;   
  
5\. \}   
  
6\. body,div,dl,dt,dd,ul,ol,li,h1,h2,h3,h4,h5,h6,pre,form,fieldset ,p,blockquote \{   
  
7\. padding: 0;  
  
8\. margin: 0;   
  
9\. font-weight: normal;   
  
10\. font-style: normal;   
  
11\. line-height: 1em;   
  
12\. font-size: 100%;   
  
13\. \}   
  
14\. table \{   
  
15\. font-size: inherit;   
  
16\. font: 100%;   
  
17\. \}   
  
18\. ul \{   
  
19\. list-style: none;   
  
20\. \}   
  
21\. img \{   
  
22\. border: 0;   
  
23\. \}   
  
24\. p \{   
  
25\. margin: 1em 0; \}  
  


这个reset.css是目前我个人最喜欢，因为reset.css就像.net中的Framework中的Object类一样，应该尽量保持精简,这个精简了很多.只留下了必要的重置.

在这里值得一说的是：在body里将font的大小和字体设置了具体的值,在其他元素里通过继承的方式来重写这样的方式是我最喜欢的，这样可以很容易的保持页面整体风格的统一

**2.3****一些注意事项******

**** Reset.css一经写好，除了BUG之外.永远不要去修改它.而是在其它页面中重载它（不知道用OO的方式理解CSS是否正确，即利用CSS的优先级特性覆盖.这个在下一章说到.）
