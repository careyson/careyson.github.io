---
layout: post
title: "jQuery Google Charts----一个封装google chart api的jquery插件"
date: 2009-12-26
categories: blog
tags: [博客园迁移]
---

Google Charts想必大家都已经耳熟能详了吧，它允许我们很轻松的通过简单的数据就能生成复杂的图表.而Jgcharts插件就是对这个api的封装，让我们调用google api更加容易.废话不多说，先来看看效果:

柱状图:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-12-26-jquery-google-charts-google-chart-api-jquery/jquery-google-charts-google-chart-api-jquery-chart_thumb.png)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryGoogleChartsgooglechartapijquery_9EED/chart_2.png)

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-12-26-jquery-google-charts-google-chart-api-jquery/jquery-google-charts-google-chart-api-jquery-chart1_thumb.png)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryGoogleChartsgooglechartapijquery_9EED/chart1_2.png)

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-12-26-jquery-google-charts-google-chart-api-jquery/jquery-google-charts-google-chart-api-jquery-chart2_thumb.png)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryGoogleChartsgooglechartapijquery_9EED/chart2_2.png)

折线图:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-12-26-jquery-google-charts-google-chart-api-jquery/jquery-google-charts-google-chart-api-jquery-chart4_thumb.png)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryGoogleChartsgooglechartapijquery_9EED/chart4_2.png)

饼图:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-12-26-jquery-google-charts-google-chart-api-jquery/jquery-google-charts-google-chart-api-jquery-chart5_thumb.png)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryGoogleChartsgooglechartapijquery_9EED/chart5_2.png)

3d饼图:

[![image](https://cdn.jsdelivr.net/gh/careyson/careyson.github.io@main/assets/images/2009-12-26-jquery-google-charts-google-chart-api-jquery/jquery-google-charts-google-chart-api-jquery-chart6_thumb.png)](http://images.cnblogs.com/cnblogs_com/CareySon/WindowsLiveWriter/jQueryGoogleChartsgooglechartapijquery_9EED/chart6_2.png)

这个插件只需要在头部引入：
    
    
    <script src="jquery-1.3.2.min.js" type="text/javascript"></script>
    <script src="jgcharts.js" type="text/javascript"></script>

这个插件的原理是根据拼接的url，Google 图表 API 会返回一幅 PNG 格式的图片来响应一个网址。可以生成多种类型的图片，包括折线图、条形图和饼图。您可以为每种图片类型指定属性，例如大小、颜色和标签。 

通过将网址嵌入 `<img>` 标签内，您可以将图表 API 图片包括在网页中。当网页在浏览器中显示时，图表 API 会呈现该网页中的这幅图片。

具体可以参考:<http://code.google.com/intl/zh-CN/apis/chart/>

这jgchart插件则可以帮助你动态的拼接这个url传递给google.

示例代码如下:
    
    
    var api = new jGCharts.Api(); 
    jQuery('<img>') 
    .attr('src', api.make({data : [[153, 60, 52], [113, 70, 60], [120, 80, 40]]})) 
    .appendTo("#bar1");

这就是最上面那个饼状图的生成方法,只需要生成jGCharts.api的实例并通过make方法来返回拼接好的字符串.通过data属性可以设置图表的数据，以js数组的方式进行.

我们还可以通过make内参数对象的type属性来设置不同的图表类型，比如折线图可以加上:“type : lc”来获取.

jGChart插件和Demo可以从这里获得:<http://www.maxb.net/scripts/jgcharts/include/demo/>

下面是我自己做的一个小Demo来对获得的图表进行简单的模拟:

第一个数字:   
第二个数字:  
  
饼图 折线图 柱状图 3d饼图 横向柱状图   


你可以加入相应的数字并且点击生成图表来进行模拟.也可以使用清空数据来将刚加入的数据清空.

上面Demo的代码如下:
    
    
        <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script>
        <script src="https://files.cnblogs.com/CareySon/jgcharts.pack.js" type="text/javascript"></script>
        <div style="border:1px dashed green; margin:30px 10px;">
        <div id="result"></div>
        <div id="bar1"></div>
        第一个数字:<input id="no1" />
        <br />
        第二个数字:<input id="no2" /><br />
        <input type="button" value="加入数据" id="add"/><input type="button" value="清空数据" id="clear" />
        <br />
        <select id="t">
        <option value="p">饼图</option>
        <option value="lc">折线图</option>
        <option value="">柱状图</option>
        <option value="p3">3d饼图</option>
        <option value="bhg">横向柱状图</option>
        </select>
        <br />
        <input type="button" value="生成图表" id="submitx" />
        <script type="text/javascript">
            var dataArray = new Array();
            $("#add").click(function() {
                var temp = new Array();
                temp.push($("#no1").val());
                temp.push($("#no2").val());
    
                dataArray.push(temp);
                $("#result").append("数据加入成功,数据为:" + $("#no1").val() + "," + $("#no2").val()+"<br />");
                temp = null;
                $("#no1")[0].value = "";
                $("#no2")[0].value = "";
    
            });
            $("#clear").click(function() {
                dataArray = new Array();
                $("#result").html("");
                $("#bar1").html("");
    
            });
            $("#submitx").click(function() {
            $("#bar1").html("");
                var api = new jGCharts.Api();
                var xdata = "[";
                for (i = 0; i < dataArray.length; i++) {
                    xdata += "[";
                    for (j = 0; j < dataArray[i].length; j++) {
    
                        xdata += dataArray[i][j];
                        xdata += ",";
                    }
                    xdata = xdata.slice(0, xdata.length - 1);
                    xdata += "]";
                    xdata += ",";
                }
                xdata = xdata.slice(0, xdata.length - 1);
                xdata += "]";
                jQuery('<img>').attr('src', api.make({ data:eval(xdata),type:$("#t").val() })).appendTo("#bar1");
            });
            
        </script>
        </div>

\-----------------

enjoy it.By [CareySon](www.cnblogs.com/careyson)
