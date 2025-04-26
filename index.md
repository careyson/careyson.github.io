---
layout: default
title: 首页
---

## 👋 你好，我是宋雨竹
这里记录我的数据库研发与 AI 实验。

### 最近文章
<ul>
{% for post in site.posts limit:5 %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> <small>{{ post.date | date: "%Y-%m-%d" }}</small></li>
{% endfor %}
</ul>
