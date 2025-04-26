---
layout: default
title: 首页
---

## 👋 
宋沄劍的個人博客

### 最近文章
{% for post in paginator.posts %}
  <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
  <p>{{ post.date | date: "%Y-%m-%d" }}</p>
  {{ post.excerpt }}
  <hr>
{% endfor %}

{% if paginator.total_pages > 1 %}
<nav>
  {% if paginator.previous_page %}
    <a href="{{ paginator.previous_page_path | relative_url }}">&laquo; 上一页</a>
  {% endif %}

  第 {{ paginator.page }} / {{ paginator.total_pages }} 页

  {% if paginator.next_page %}
    <a href="{{ paginator.next_page_path | relative_url }}">下一页 &raquo;</a>
  {% endif %}
</nav>
{% endif %}
