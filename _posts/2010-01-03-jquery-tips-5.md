---
layout: post
title: "jQuery Tips(5)----关于伪类选择符"
date: 2010-01-03
categories: blog
tags: [博客园迁移]
---

jQuery选择器的强大不仅在于选择器支持基本的css选择符，还支持很多CSS的伪类选择符，甚至可以自定义选择符，下面让我们来看看一些伪类选择符

##  **:nth-child的用法**

nth-child是一个css3伪类选择符,在jQuery中被实现了，在Jquery API中对nth-child的定义是：”匹配其父元素下的第N个子或奇偶元素“。读着感觉有点绕口，下面让我们通过例子来说明:
    
    
        <div>
        <ul>
        <li>one</li>
        <li>two</li>
        <li>three</li>
        <li>four</li>
        <li>five</li>
        <li>six</li>
        <li>seven</li>
        <li>eight</li>
        <li>nine</li>
        </ul>
        <ul>
        <li>1</li>
        <li>2</li>
        <li>3</li>
        <li>4</li>
        <li>5</li>
        <li>6</li>
        <li>7</li>
        <li>8</li>
        <li>9</li>
        </ul>
        </div>
        <script type="text/javascript">
            $("li:nth-child(2)").css("background-color", "blue");
        </script>

运行效果如下:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-01-03-jquery-tips-5/jquery-tips-5-1_thumb.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryTips5_11F7C/1_2.jpg)

API定义中的匹配其父辈指的是所选元素的父元素不同，则分开选择。在上面例子中虽然一共选择18个<li>但是这18<li>分属于2个不同的<ul>,所以会选择两个.如果将其放入同一个<ul>中，如果放入同一个<ul>执行上面代码，则：

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-01-03-jquery-tips-5/jquery-tips-5-2_thumb.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryTips5_11F7C/2_2.jpg)

理解了上面匹配父辈元素，下面来说说这个选择符参数的用法.

  1. 向上面那样直接给出选择的位置，但是这里注意，这个位置是以1为开始的，而不是0 
  2. n个倍数选择法，比如可以使3n+1,-3n+1，4n,等，匹配所有页面上存在的n的倍数 



例子:
    
    
        <div>
        <ul>
        <li>one</li>
        <li>two</li>
        <li>three</li>
        <li>four</li>
        <li>five</li>
        <li>six</li>
        <li>seven</li>
        <li>eight</li>
        <li>nine</li>
        
        </ul>
        </div>
        <script type="text/javascript">
            $("li:nth-child(3n-1)").css("background-color", "blue");
        </script>

效果:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-01-03-jquery-tips-5/jquery-tips-5-3_thumb.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryTips5_11F7C/3_2.jpg)

可见相对应的元素都被匹配

3.还有一种用法是我们熟知的odd和even,就是奇数和偶数，如下：
    
    
        <script type="text/javascript">
            $("li:nth-child(odd)").css("background-color", "blue");
        </script>

效果:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-01-03-jquery-tips-5/jquery-tips-5-4_thumb.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryTips5_11F7C/4_2.jpg)

## **:first-child &last-child**

从上面的nth-child可以看到”匹配父类下的“含义，first-child和last-child也同样是这样.它们可以看做nth-child的封装：

first-child和nth-child\(1\)等价，这里就不多说了.

而first-child目前我还找不到等价的nth-child表达式，匹配父类下的最后一个子元素:
    
    
        <ul>
        <li>1</li>
        <li>2</li>
        </ul>
        <ul>
        <li>1</li>
        <li>2</li>
        </ul>
    
        <script type="text/javascript">
            $("li:last-child").css("background-color", "blue");
        </script>

效果:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-01-03-jquery-tips-5/jquery-tips-5-5_thumb.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryTips5_11F7C/5_2.jpg)

## **:input并不只是匹配input**

个选择符我想大家都比较熟悉，但是要注意，input伪类选择符不只是匹配<input>标签，还会匹配<select>和<textarea>:
    
    
    第一个：<input type="input" />
    第二个：<select id="select">
    
    </select>
    第三个：<textarea></textarea>
    <script type="text/javascript">
        alert($(":input").length);//alert 3
    </script>

可以看到，不光<input>被选择，<select>和<textarea>也被选择了

## **伪类选择符可以嵌套**

通常情况下，我们可以通过嵌套伪类选择符来达到我们需要的效果,伪类选择符，如下：
    
    
        <ul>
        <li>1</li>
        <li>2</li>
        <li>3</li>
        <li>4</li>
        <li>5</li>
        <li>6</li>
        <li>7</li>
        </ul>
    
        <script type="text/javascript">
            $("li:not(:first):not(:last)").css("background-color", "blue");
        </script>

效果:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2010-01-03-jquery-tips-5/jquery-tips-5-z11111111111111111111111_thumb.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryTips5_11F7C/z11111111111111111111111_2.jpg)

可见，除了第一个和最后一个li,其它都被选择.当然，嵌套是有层数限制的，具体的次数我就不太清了\(各位高手记得麻烦告诉我下\),反正够你进行不是变态的使用:-\)

## **自定义伪类选择符**

jquery还提供给我们扩展原有选择符的方式，可以让我们根据自己的需要自定义选择符，下面通过一个有实际意义的例子看如何做到：

在我们使用jquery的serialize方法将当前表单中的元素提交到服务器时，总是会选上asp.net的ViewState\(<input type=”hidden” />\)这无疑浪费了好多资源，我们通过一个扩展的伪类选择符看如何不选择它:
    
    
    <form name="form1" method="post" action="default.aspx" id="form1">
    <div>
    <input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUJNzgzNDMwNTMzZGRWxo4mg/noF3+7k/L7nyw13HVnLQ==" />
    </div>
    
     
        <script type="text/javascript">
            $.expr[":"].noViewState = function(element) {
                return !$(element).attr("id") === "_VIEWSTATE";
            }
            alert($(":input:noViewState").size());//alert 0 ViewState has not been choosen
        </script>
     
        </form>

通过$.expr的方式对伪类选择符进行扩展，可以看出，上面的选择符使用:noViewState后,viewState没有被选择. 

## **小结:**

jQuery的伪类选择符是很强大的一项功能,它内置了很多种方便我们选择的选择符，我们可以嵌套甚至扩展这些伪类选择符.这让我们的js编程更加愉悦了许多.

By [CareySon](http://www.cnblogs.com/careyson)
