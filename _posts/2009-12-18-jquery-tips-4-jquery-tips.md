---
layout: post
title: "JQuery Tips(4)----一些关于提高JQuery性能的Tips"
date: 2009-12-18
categories: blog
tags: [博客园迁移]
---

如今咱祖国已经崛起了..电脑的配置也是直线上升.可是js的性能问题依然不可小觑..尤其在万恶的IE中..js引擎速度本来就慢..如果JS如果再写不好，客户端多开几个窗口假死肯定是家常便饭了.废话不说了，下面说说js性能提升的一些小Tips.

**在选择时，最好以ID选择符作为开头**

我想这个很好理解，因为JQuery内部使用document.getElementByID方法进行ID选择，这种方法比其他所有对DOM选择的方法更快，所以以$\("\#"\)开头是最好的,比如:
    
    
    <div id="a">
       <div class="b">
          <div class="c">
              <div class="d"></div>
          </div>
       </div>
    </div>
        <script type="text/javascript">
            $(".b .c .d")//slow one
            $("#a .b .c .d")//fast one
        </script>

#### **提供$\(\)的上下文**

在使用$\(\)选择页面元素时，提供选择的范围可以减少选择的时间，换句话说，让选择器只在页面的一小片范围内筛选而不是整个页面当然会减少筛选时间，通过在$\(\)函数内提供第二个参数作为上下文可以实现这一点
    
    
        <div id="test">
           <div class="inner">hi</div>
        </div>
        <script type="text/javascript">
            alert($(".inner", document.getElementById("test")).text());//increase the speed by provide context
            alert($(".inner").text());//traverse all the element so that is slower than above
        </script>

当然，在jquery定义\(或者js函数\)事件内,可以通过this来指代上下文:
    
    
        <div id="test">
           <div class="inner">hi</div>
        </div>
        <script type="text/javascript">
            $("#test").click(function() {
                var text = $(".inner", this).text(); //this means $("#test")
                alert(text);//alert hi
            });
        </script>

当然，上面的例子也可以写成下面两种方式：
    
    
        <div id="test">
           <div class="inner">hi</div>
        </div>
        <script type="text/javascript">
            alert($("#test .inner").text()); //method 1
            alert($("#test").find(".inner").text());//method 2 and it was best one
        </script>

其中利用find方法是所有方法中效率最高的

当然，如果你是通过id选择符，也就是$\("\#.."\)来选择，不需要提供上下文参数.这对速度没有影响

#### **将经常用的JQuery包装好的元素进行保存**

如题，这点比较重要，因为使用$\(\)对页面元素进行选择是需要耗费时间的.而保存为变量进行使用时，可以避免这种浪费，比如：
    
    
        <ul>
        <li>one</li>
        <li>two</li>
        <li>three</li>
        <li>four</li>
        <li>five</li>
        </ul>
        <script type="text/javascript">
            for (i = 0; i < $("ul li").length; i++) {//very bad,select $("ul li") so many times,waste a lot of time
                alert($("ul li")[i].innerHTML);//same here,very bad
            }
            var $li = $("ul li");
            for (i = 0; i < $li.length; i++) {//good one,only selct $("ul li") once
                alert($li[i].innerHTML); //same here,good
            }
        </script>

从代码可以看到，避免多次重复选择可以提高性能:-\)

#### **尽量少用选择符**

JQuery的选择器是面向数组的，所以在条件允许的情况下尽量少用选择器，比如：
    
    
    <div id="Div0"></div>
    <div id="Div1"></div>
    <div id="Div2"></div>
        <script type="text/javascript">
            $("#Div0").slideDown("slow");
            $("#Div1").slideDown("slow");
            $("#Div2").slideDown("slow");//slow
    
            $("Div0,Div1,Div2").slideDown("slow");//fast
        </script>

可以看出，使用选择器并用逗号将被选择的元素分开，并选择多个元素不仅让代码更加简洁，并且通过减少创建JQuery的实例所以在性能上也稍胜一筹\!

#### **在循环次数很多时避免使用$\(\).each,而使用for循环**

使用$\(\).each方法让在进行循环时，会让编程更加轻松，少量的循环在使用$\(\).each时对性能的影响可以忽略不计，但是当这个数字很大的时候，对性能的影响便开始变得可观了.

这个数字，我查了下资料，据说是1000以下可以使用$\(\).each方法，而这个数字如果继续增加，则应该使用for循环语句。

#### **尽量减少对DOM的操作**

在页面中对DOM操作是比较消耗的（比如在页面插入或删除一段文字），把这个改动降至最小是保持性能的最佳实践！比如：
    
    
        <ul id="test">
        </ul>
        <script type="text/javascript">
            var $list = $("#test");
            for (i = 1; i < 101; i++) {
                $list.append("<li>Item" + i + "</li>");
            } //very bad,change dom 100 times
    
            var listItem = "";
            for (j = 1; j < 101; j++) {
                listItem += "<li>Item" + j + "</li>";
            }
            $list.html(listItem);
            //good practice,only modify dom once
            
        </script>

可以看出，第一个例子对DOM修改100次，而第二个只对DOM修改1次，这上面的性能差距是显而易见的。

#### **可以屏蔽JQuery的动画效果**

在某些情况下，如果，可以关闭JQuery动画，能对性能进行一定提升，屏蔽的方法是：
    
    
        <script type="text/javascript">
            jQuery.fx.off = true;
        </script>

#### **如果参数可以是JS对象，尽量使用对象**

很对JQuery插件，或者JQuery的css和attr方法都接受键/值 或 js键/值对象 对作为参数，传递键值对象可以减少JQuery对象的创建，比如:
    
    
    <div></div>
        <script type="text/javascript">
            $("div").css("display", "block");
            $("div").css("background-color", "blue")
            //slow,because it create more Jquery object
    
            $("div").css({ "display": "block", "background-color": "blue" });
            //fast,only create one object
        </script>

当然也可以使用连缀的方式:
    
    
    <div></div>
        <script type="text/javascript">
            $("div").css("display", "block").css("background-color", "blue");
            
        </script

但是这种方式的性能不如上面那种.需要使用两个方法，并且需要多生成临时对象.

以上都是一些对JQuery性能提升的小Tips

By:[CareySon](http://www.cnblogs.com/CareySon/)
