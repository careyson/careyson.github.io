---
layout: post
title: "JQuery Tips（3）----关于$()包装集内元素的改变"
date: 2009-12-14
categories: blog
tags: [博客园迁移]
---

#### JQuery包装集内的元素在一开始的选定后，还可以通过一系列JQuery提供的方法对包装集内的元素进行扩充，修改，筛选，删除

#### **find\(\)方法 VS filter\(\)方法**

这两个方法是比较容易搞混的.

filter方法表示的是对当前内部的元素进行筛选,这个接受两种参数，一个返回bool的function,或者是JQuery的选择表达式,包装集内的元素只会小于等于当前包装集内的元素，并且含有的元素属于原来包装集内元素的子集：
    
    
    <div id="one">the one</div>
    <div id="two"><p>the two</p></div>
    <div id="three"><p>the three</p></div>
        <script type="text/javascript">
            alert($("div").filter(":not(:first):not(:last)").html()); //out put<p>the two</p>
            alert($("div").filter(function() { return this.id == "two"; }).html());//output <p>the two</p> as well
            
        </script>

而find方法却是在当前元素内（子元素）部进行查找，并返回**新的包装集** ,这意味着包装集可能会增加:
    
    
    <div id="one">the one</div>
    <div id="two"><p>the two</p><p></p><p></p></div>
    <div id="three"><p>the three</p></div>
        <script type="text/javascript">
            alert($("div").find("p").text()); //alert "the twothe three"
            alert($("div").find("p").length); //alert 4 instead of original 3
        </script>

从上面可以看出新包装集内的元素增加了

#### **parents\(\)方法 VS closest\(\)方法**

这两个方法都是由当前元素向上查找所匹配的元素，不同之处如下:
    
    
        <div id="wrapper">
            <div id="two">
                <p id="p1">
                    the two</p>
            </div>
            </div>
        <script type="text/javascript">
            alert($("#p1").parents("div").length); //alert 2 include <div id="two"> and <div id="wrapper">
            alert($("#p1").closest("div").length); //alert 1 and only include <div id="two">
            alert($("#p1").parents("p").length);  //alert 0 because it does not include current element
            alert($("#p1").closest("p").length);  //alert 1 because it contain itself <p id="p1">
        </script>

对于parents方法来说，会将当前元素向上的所有匹配元素加入新的包装集并返回，而closest方法只会包含离当前元素最近的元素,所以使用closest方法后当前包装集内的元素只能为1个或者0个

而parents方法并不包括当前包装集内的元素，而closest方法会包含当前包装集内的元素

#### **直系子元素 VS 所有子元素**

使用children可以返回直系子元素，而用find加通配符的方法可以返回除了文本节点之外的所有子元素：
    
    
        <div id="wrapper">
            text node here
            <div id="two">
                <p id="p1">
                    the two</p>
            </div>
            </div>
        <script type="text/javascript">
            alert($("#wrapper").children().length);//alert 1 because only direct children included
            alert($("#wrapper").find("*").length); //alert 2 because all desendants included
            alert($("#wrapper").find(">*").length);//alert 1 because only direct children included
        </script>

可以看出children方法只会含有当前元素的直系子元素，而使用find\(“>\*也会产生同样的效果”\).若想采纳所有的直系子元素直接在find内传”\*”通配符

#### **回到过去的end\(\)方法以及andself\(\)方法**

上述所有的方法，以及比如add\(\),next\(\),nextAll\(\),prev\(\)等对包装集内元素进行改变的方法都可以使用end\(\)方法来进行返回:
    
    
        <div id="wrapper">
            text node here
            <div id="two">
                <p id="p1">
                    the two</p>
            </div>
            </div>
        <script type="text/javascript">
            alert($("#wrapper").find(">*").end().get(0).id);//alert "wrapper" instead of "two" because of end() method has been used
        </script>

end\(\)方法总是和最近的一个和包装集改变的方法相抵消，而抵消其他方法:
    
    
        <div id="wrapper">
            text node here
            <div id="two">
                <p id="p1">
                    the two</p>
            </div>
            </div>
        <script type="text/javascript">
            alert($("#wrapper").find("#p1").html("new value").end().get(0).id);//alert wrapper because end method
            alert($("#p1").text())//alert new value bacause the html method in previous has not been cancelled
        </script>

如果需要在改变包装集内元素的情况下还需要包含原始的包装集内元素，使用andself方法:
    
    
        <div id="wrapper">
            text node here
            <div id="two">
                <p id="p1">
                    the two</p>
            </div>
            </div>
        <script type="text/javascript">
            var $a = $("#wrapper").find("#two").andSelf();
            alert($a[0].id);//alert two first
            alert($a[1].id);//alert wrapper after that
        </script>

我们会发现首先alert two,因为two先被选择

\-------------------------------------传说中的分隔符---------------------------

PS:liver writer代码高亮插件我一加中文就是乱码，很郁闷的说-.-\!\!所以注释都是鸟语了
