---
layout: post
title: "JQuery Tips(1)----关于$.Ready()"
date: 2009-12-12
categories: blog
tags: [博客园迁移]
---

最近一直在研究JQuery,这个东西还是很博大精深的.下面分享一下我的学习总结.

## $\(document\).Ready\(\)方法 VS OnLoad事件 VS $\(window\).load\(\)方法

接触JQuery一般最先学到的是何时启动事件。在曾经很长一段时间里,在页面载入后引发的事件都被加载在”Body”的Onload事件里.

对于Body的Onload事件和JQuery的Ready方法相比，有很多弊端.比如:

> #### 1.加载多个函数的问题
>     
>     
>     <body onload="a();b();">
>     
>     </body>
> 
> 在Onload事件中只能这样加载，很丑陋…而在JQuery中你可以利用多个JQuery.Ready\(\)方法，它们会按次序依次执行
> 
> #### 2.代码和内容不分离
> 
> 这个貌似不用说了，让人深恶痛绝-.-\!\!
> 
> #### 3.执行先后顺序不同
> 
> 对于Body.Onload事件，是在加载完所有页面内容才会触发，我的意思是**所有内容,** 包括图片，flash等.如果页面的这些内容很多会让用户等待很长时间.
> 
> 而对于$\(document\).ready\(\)方法，这个方法只是在页面所有的DOM加载完毕后就会触发,无疑很大的加快了网页的速度.
> 
> 但是对于一些特殊应用，比如图片的放大缩小，图片的剪裁。需要网页所有的内容加载完毕后才执行的呢？我推荐使用$\(window\).load\(\)方法，这个方法会等到页面所有内容加载完毕后才会触发，并且同时又没有OnLoad事件的弊端.
>     
>     
>         <script type="text/javascript">
>             $(window).load(function() {
>                 alert("hello");
>             });
>             $(window).load(function() {
>                 alert("hello again");
>             });
>         </script>
> 
> 上面的代码会在页面所有内容加载完成后按先后顺序依次执行.

> 当然不要忘了与之对应的Unload方法
>     
>     
>     $(window).unload(function() {
>                 alert("good bye");
>             });

> 上面代码会在页面关闭时引发.

## **在所有DOM加载之前引发JS代码**

> 这个方法是我在调试的时候最喜欢的，有时候开发的时候也用这种方法
>     
>     
>     <body>
>         <script type="text/javascript">
>             (function() {
>                 alert("hi");
>             })(jQuery)
>         </script>
>     </body>

> 对，就是利用js闭包的形式将js代码嵌入body，这段代码会自动执行，当然也可以直接嵌入js代码,这种方式要注意顺序问题，如下：
>     
>     
>     <body>
>     <div id="test">this is the content</div>
>         <script type="text/javascript">
>     
>             alert($("#test").html());//I Can display the content
>             
>         </script>
>     </body>

> 
>     <body>
>     
>         <script type="text/javascript">
>     
>             alert($("#test").html());//I Can't display the content
>             
>         </script>
>         <div id="test">this is the content</div>
>     </body>

> 上面两段代码,第二段代码当中因为只能解释到当前代码之前的DOM,而test并不存在于已经解析的DOM数.所以第二段代码无法正确显示.
