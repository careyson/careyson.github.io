---
layout: post
title: "JQuery Tips(2)----关于$()包装集你不知道的"
date: 2009-12-13
categories: blog
tags: [博客园迁移]
---

#### **包装集总是面向集合的**

我想这个理解起来很简单，被$\(\)包装的JQuery对象总是以集合的形式出现.就算包装集中只有一个对象.
    
    
    <div id="a"></div>
    <div id="b"></div>
        <script type="text/javascript">
            $("div").html("hi");
            
            
        </script>

上面被选择的两个DIV的内容都会被改变为”hi”

#### 

#### **包装集内元素的顺序**

在被JQuery包装的元素中,包装集中所包含的内部顺序是按照HTML流从先向后排列的，而不是选择顺序:
    
    
    <div id="a">here is a</div>
    <div id="b">here is b</div>
        <script type="text/javascript">
            var Se = $("#b,#a");
            alert(Se.get(0).innerHTML);
            alert(Se.get(1).innerHTML);
            
            
        </script>

上面代码可以看到，虽然是b先被选择，但是在执行alert的时候会先弹出”here is a”继而是“here is b”

**JQuery对象和DOM的转化**

**** 首先，是DOM转化成JQuery对象，这个很容易，只需包含在$\(\)里面即可.但有一点注意的是，再被JQuery包装的元素的事件内，this总是指向当前对象:
    
    
    <div id="a">here is a</div>
    <div id="b">here is b</div>
        <script type="text/javascript">
            $("div").click(function() {
                alert(this.id);//this Ö¸Ïòµ±Ç°µÄDOM
            });
            
            
        </script>

将JQuery包装集中的元素转为DOM对于JQuery来说也是很简单的事,大多数情况都使用JQuery的get方法
    
    
    <div id="a">here is a</div>
    <div id="b">here is b</div>
        <script type="text/javascript">
            var Jq = $("div");
            alert(Jq.get(0).id); //alert "a"
            alert(Jq.get()[0].id); //alert "a" as well
            alert(Jq[0].id);//alert "a"
            
        </script>

从面可以看出,通过get方法加索引作为参数，会返回索引值的DOM对象，而不加参数会返回JQuery包装集中的整个数组

还有一种简便方法是直接在JQuery包装集后面加数组符号，可以把上面的Jq\[0\]看做Jq.get\(0\)的简便方式:-\)

#### **检查当前JQuery包装集中的元素个数**

在很多时候,需要检查在JQuery包装集中的元素个数,我们可以直接通过包装集的length属性（这个属性在VS当中是不提示的）
    
    
    div id="a">here is a</div>
    <div id="b">here is b</div>
        <script type="text/javascript">
            var Jq = $("div");
            alert($("Div").length);//alert "2"
            
        </script>

这个属性还可以直接用于检测当前的包装集是否为空
    
    
    <div id="a">here is a</div>
    <div id="b">here is b</div>
        <script type="text/javascript">
            if ($("div").length) {
                alert("Not Empty");
            }
            if ($("div").get(0)) {
                alert("Not Empty");
            }
            
        </script>

上面两个alert都会被执行，第二个方式通过检测当前包装集中第一个元素是否为空来确定包装集为空. 

#### **包装集在某些特定情况下也“不总是面向集合”**

刚才不是号称总是面向集合吗，咋又变了？其实的确是面向集合，但在使用JQuery的某些方法进行提取时，就不是这样了，比如下面代码:
    
    
    <div id="a" >here is a</div>
    <div id="b">here is b</div>
        <script type="text/javascript">
            alert($("div").attr("id"));
            
        </script>

上面代码只会alert第一个div的id.那在这种情况下咋办呢？对，用JQuery的Each方法,each方法会遍历包装集中的每一个元素:
    
    
    <div id="a" >here is a</div>
    <div id="b">here is b</div>
        <script type="text/javascript">
            $("div").each(function() {
                alert($(this).attr("id"));
            });
            
        </script>

上面代码会执行两个alert:-\) 
