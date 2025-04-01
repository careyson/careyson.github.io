---
layout: post
title: "Silverlight 入门学习笔记（1）------Silverlight是什么"
date: 2011-02-08
categories: blog
tags: [博客园迁移]
---

Why Silverlight

谈起silverlight,不得不说起用户界面（UI）。

> 随着电脑性能的不断提高，用户UI也变得变得至关紧要。用户不仅仅满足于程序完成既有的功能，而且还需要程序有一个精美的界面。而编程人员也一直在性能和界面之间寻找一个平衡点。
> 
> 而internet的兴起，是基于HTML的程序开始流行，对于.net平台的开发人员来说，自然是asp.net。开发人员共多的去关注性能时，付出的代价就是惨不忍睹的UI界面。下图是基于html的web应用程序和基于windows的桌面程序性能和用户界面的图示：
> 
> [![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-02-08-silverlight-1-silverlight/silverlight-1-silverlight-201102081642492248.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/201102/201102081642485378.jpg)
> 
> 而在silverlight出现以前，互联网RIA（Rich Internet Applications）基本是被flash统治着，但由于缺少对应的开发工具，对于.net平台下的开发人员来说,和Flash的整和变得十分繁琐，所以很长时间内,flash对于.net平台的开发人员来说，仅仅是一个动画和链接，而没有实际的功能。而silverlight的出现，填补了这个空白:
> 
> [![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-02-08-silverlight-1-silverlight/silverlight-1-silverlight-20110208164250131.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/201102/201102081642508801.jpg)

Silverlight是什么

Silverlight是一RIA（Rich Internet Application）解决方案，而RIA都是在客户端的Runtime\(我的理解是服务器仅仅发送如何显示的代码，由客户端Runtime负责解析这些代码，并以相应的形式表现在浏览器中，HTML就算是一种，但不够Rich\)，Silverlight是一种跨平台，跨浏览器的客户端插件，可以根据服务器传来的特定代码生成对应的界面和功能，并镶嵌在现有的HTML中.

那Silverlight服务端向客户端\(浏览器\)发送的代码是什么形式呢？是一种称为XAML（Extensible Application Markup Language,发音为”zammel”\)的语言，XAML是一种基于XML的语言，它可以定义页面中各种元素如果布局和显示，但比HTML更加强大的是，它还能定义时间轴，渐变，动画，事件等…..

下面一个小例子说明Silverlight中XAML的形式:
    
    
    <UserControl x:Class="SilverlightApplication2.MainPage"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
        mc:Ignorable="d"
        d:DesignHeight="300" d:DesignWidth="400">
    <Border Margin="10" CornerRadius="10" BorderThickness="2">
            <Border.BorderBrush>
                <LinearGradientBrush>
                    <GradientStop Color="Black" Offset="0"></GradientStop>
                    <GradientStop Color="White" Offset="1"></GradientStop>
                </LinearGradientBrush>
                
            </Border.BorderBrush>
            <Border.Background>
                <LinearGradientBrush>
                    <GradientStop Color="black" Offset="0"></GradientStop>
                    <GradientStop Color="White" Offset="1"></GradientStop> 
                    </LinearGradientBrush>
            </Border.Background>
                <Button Height="180" Width="200">
            
            <StackPanel Orientation="Vertical">
                <StackPanel Margin="5" 
                VerticalAlignment="Center" 
                Orientation="Horizontal">
    
                    <Ellipse Fill="Yellow" Width="25" />
                    <TextBlock VerticalAlignment="Center" 
                    Margin="5" Text="Ìì¬¨?Æø?Ô¤¡è±¨À¡?µÄ?Ë¼?ÃÜ¨¹´ï?" />
    
                </StackPanel>
                <ListBox FontSize="11" Opacity="0.7" 
                Margin="2" x:Name="lstForecastGlance">
                    <ListBoxItem>
                        <TextBlock VerticalAlignment="Center" 
                        Text="Mon: Sunny " />
                    </ListBoxItem>
                    <ListBoxItem>
                        <TextBlock VerticalAlignment="Center" 
                        Text="Tue: Partly Cloudy" />
                    </ListBoxItem>
                    <ListBoxItem>
                        <TextBlock VerticalAlignment="Center" 
                        Text="Wed: Thunderstorms" />
                    </ListBoxItem>
                    <ListBoxItem>
                        <TextBlock VerticalAlignment="Center" 
                        Text="Thu: Thunderstorms" />
                    </ListBoxItem>
                    <ListBoxItem>
                        <TextBlock VerticalAlignment="Center" 
                        Text="Fri: Partly Cloudy" />
                    </ListBoxItem>
                    <ListBoxItem>
                        <TextBlock VerticalAlignment="Center" 
                        Text="Sat: Mostly Sunny" />
                    </ListBoxItem>
                    <ListBoxItem>
                        <TextBlock VerticalAlignment="Center" 
                        Text="Sun: Sunny" />
                    </ListBoxItem>
                </ListBox>
            </StackPanel>
        </Button>
        </Border>
    </UserControl>

下图是上述代码的显示结果:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2011-02-08-silverlight-1-silverlight/silverlight-1-silverlight-201102081642535406.jpg)](http://images.cnblogs.com/cnblogs_com/CareySon/201102/201102081642514459.jpg)

上面代码表示的是什么并不重要，重要的是可以看出XAML的表现形式基本上熟悉HTML的人都能很快上手.

Silverlight的优势

由于Silverlight第一个版本是2007年出的，相对时RIA技术里比较新的，所以Silverlight继承了所有RIA技术的优势，但除此之外，对于.Net平台的开发人员来说，Silverlight还有不少独到的优势:

1.多浏览器，多平台支持.

2.多个.net版本支持

3.XAML是一个基于文本，类似于XML的标记语言

4.Siliverlight使用.Net程序员所熟悉的技术

5.Siliverlight是Windows Phone7的主要开发平台

6.Siliverlight易于部署

………………………

小结

本文粗略了介绍了为什么选择Silverlight以及Siliverlight的大概样子以及使用Siliverlight的优势，后续文章会继续记录对于Silverlight的学习.
