#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
博客园博客迁移到GitHub Pages脚本
功能：
1. 爬取博客园指定用户的博客文章
2. 将HTML格式转换为Markdown格式
3. 下载文章中的图片并保存到本地GitHub仓库的assets目录，每篇文章的图片存放在独立目录
4. 生成符合GitHub Pages格式的Markdown文件
5. 支持全量下载或增量更新模式
"""

import os
import re
import time
import requests
import json
from bs4 import BeautifulSoup
import html2text
import urllib.parse
from datetime import datetime
import argparse
import logging
import hashlib

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CnblogsToGitHub:
    def __init__(self, username, github_dir, incremental=True, base_url=''):
        """
        初始化参数
        :param username: 博客园用户名
        :param github_dir: 本地GitHub仓库目录
        :param incremental: 是否使用增量更新模式
        :param base_url: 网站的基础URL路径（默认为空）
        """
        self.username = username
        self.github_dir = github_dir
        self.post_dir = os.path.join(github_dir, '_posts')
        self.assets_dir = os.path.join(github_dir, '_posts', 'assets', 'images')  # 修改图片存储路径到_posts目录下
        self.data_dir = os.path.join(github_dir, '.cnblogs_data')
        self.incremental = incremental
        self.base_url = base_url.strip('/') if base_url else ''

        # 创建必要的目录
        os.makedirs(self.post_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

        # 已处理文章的元数据文件
        self.meta_file = os.path.join(self.data_dir, 'processed_articles.json')

        # 初始化已处理文章记录
        self.processed_articles = self.load_processed_articles()

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # 初始化HTML到Markdown转换器
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.escape_snob = True
        self.h2t.body_width = 0  # 禁用自动换行

        # 为已经迁移过的网站修正路径（将/assets/改为assets/）
        if os.path.exists(self.post_dir):
            self.fix_existing_image_paths()

    def fix_existing_image_paths(self):
        """
        修复已存在的Markdown文件中的图片路径，统一为assets/images/...格式
        """
        try:
            logger.info("正在检查并修复已有文章的图片路径...")
            fixed_count = 0

            for filename in os.listdir(self.post_dir):
                if not filename.endswith('.md'):
                    continue

                filepath = os.path.join(self.post_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 替换不同模式的路径到正确的格式
                updated_content = content

                # 替换各种可能的路径格式为简单的相对路径
                # 处理以/assets/开头的路径
                updated_content = re.sub(r'!\[.*?\]\(/assets/', r'![image](assets/', updated_content)

                # 处理以/blog/assets/开头的路径
                updated_content = re.sub(r'!\[.*?\]\(/blog/assets/', r'![image](assets/', updated_content)

                # 处理以blog/assets/开头的路径
                updated_content = re.sub(r'!\[.*?\]\(blog/assets/', r'![image](assets/', updated_content)

                if content != updated_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    fixed_count += 1

            logger.info(f"完成图片路径修复，共修复 {fixed_count} 篇文章")
        except Exception as e:
            logger.error(f"修复图片路径失败: {str(e)}")

    def load_processed_articles(self):
        """
        加载已处理文章记录
        :return: 已处理文章字典 {url: {title, date, hash}}
        """
        if os.path.exists(self.meta_file):
            try:
                with open(self.meta_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载已处理文章记录失败: {str(e)}")
        return {}

    def save_processed_articles(self):
        """
        保存已处理文章记录
        """
        try:
            with open(self.meta_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_articles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存已处理文章记录失败: {str(e)}")

    def get_content_hash(self, content):
        """
        计算内容的哈希值
        :param content: 内容字符串
        :return: 哈希值
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def get_article_list(self, page=1, max_pages=None):
        """
        获取博客园用户的文章列表
        :param page: 起始页码
        :param max_pages: 最大页数限制
        :return: 文章URL列表
        """
        article_urls = []
        current_page = page

        while True:
            if max_pages and current_page > max_pages:
                break

            list_url = f"https://www.cnblogs.com/{self.username}/default.html?page={current_page}"
            logger.info(f"获取文章列表: {list_url}")

            try:
                response = self.session.get(list_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # 查找文章列表
                post_list = soup.select('.postTitle a')

                if not post_list:
                    logger.info(f"第{current_page}页没有找到文章，停止获取")
                    break

                for post in post_list:
                    article_urls.append(post['href'])

                # 检查是否有下一页
                next_page = soup.select('.pager a')
                has_next = False
                for a in next_page:
                    if a.text.strip() == '下一页':
                        has_next = True
                        break

                if not has_next:
                    logger.info("已到达最后一页")
                    break

                current_page += 1
                # 适当延迟，避免请求过快
                time.sleep(1)

            except Exception as e:
                logger.error(f"获取文章列表失败: {str(e)}")
                break

        logger.info(f"共找到 {len(article_urls)} 篇文章")
        return article_urls

    def download_image(self, img_url, post_title, published_date):
        """
        下载图片并保存到assets目录，每篇文章单独一个目录
        :param img_url: 图片URL
        :param post_title: 文章标题(用于生成目录)
        :param published_date: 发布日期(用于生成目录)
        :return: 新的图片URL路径(相对于GitHub Pages)
        """
        try:
            # 清理文章标题，用作目录名
            safe_title = re.sub(r'[^a-zA-Z0-9\-_]', '-', post_title.lower())
            safe_title = re.sub(r'-+', '-', safe_title).strip('-')

            # 使用日期+标题作为目录名，确保每篇文章有独立目录
            post_dir_name = f"{published_date}-{safe_title}"
            img_dir = os.path.join(self.assets_dir, post_dir_name)
            os.makedirs(img_dir, exist_ok=True)

            # 提取文件名
            parsed_url = urllib.parse.urlparse(img_url)
            img_path = parsed_url.path
            img_name = os.path.basename(img_path)

            # 处理没有扩展名的情况
            if '.' not in img_name:
                img_name = f"{img_name}.png"

            # 处理URL中可能存在的查询参数
            if '?' in img_name:
                img_name = img_name.split('?')[0]

            # 确保文件名唯一但有意义
            img_name = f"{safe_title}-{img_name}"

            local_path = os.path.join(img_dir, img_name)

            # 处理相对URL
            if img_url.startswith('//'):
                img_url = f"https:{img_url}"
            elif not img_url.startswith(('http://', 'https://')):
                img_url = f"https:{img_url}" if img_url.startswith('//') else f"https://www.cnblogs.com{img_url}"

            # 下载图片
            response = self.session.get(img_url, stream=True)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # 构建相对路径格式 - 由于图片存储在_posts目录下，使用简单的相对路径即可
            github_path = f"assets/images/{post_dir_name}/{img_name}"
            logger.info(f"图片已下载: {img_url} -> {github_path}")
            return github_path

        except Exception as e:
            logger.error(f"下载图片失败 {img_url}: {str(e)}")
            return img_url  # 如果下载失败，返回原始URL

    def process_article(self, article_url):
        """
        处理单篇文章，将HTML转为Markdown并下载图片
        :param article_url: 文章URL
        :return: (标题, 处理后的Markdown内容, 发布时间)
        """
        try:
            logger.info(f"处理文章: {article_url}")

            # 如果是增量模式且文章已处理，检查是否需要更新
            if self.incremental and article_url in self.processed_articles:
                response = self.session.get(article_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # 获取文章内容
                content_elem = soup.select_one('#cnblogs_post_body')
                if not content_elem:
                    logger.warning(f"没有找到文章内容: {article_url}")
                    return None

                # 计算当前内容的哈希值
                current_hash = self.get_content_hash(str(content_elem))

                # 如果内容没有变化，跳过处理
                if current_hash == self.processed_articles[article_url]['hash']:
                    logger.info(f"文章内容未变化，跳过处理: {article_url}")
                    return None

                logger.info(f"文章内容已更新，重新处理: {article_url}")

            response = self.session.get(article_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 获取文章标题
            title_elem = soup.select_one('.postTitle')
            if title_elem:
                title = title_elem.get_text().strip()
            else:
                title = soup.title.string.strip()

            # 获取发布时间
            time_elem = soup.select_one('#post-date')
            if time_elem:
                published_date = time_elem.get_text().strip()
                try:
                    dt = datetime.strptime(published_date, '%Y-%m-%d %H:%M')
                    published_date = dt.strftime('%Y-%m-%d')
                except ValueError:
                    published_date = datetime.now().strftime('%Y-%m-%d')
            else:
                published_date = datetime.now().strftime('%Y-%m-%d')

            # 获取文章内容
            content_elem = soup.select_one('#cnblogs_post_body')
            if not content_elem:
                logger.warning(f"没有找到文章内容: {article_url}")
                return None

            # 计算内容的哈希值用于增量更新
            content_hash = self.get_content_hash(str(content_elem))

            # 处理图片
            for img in content_elem.select('img'):
                img_url = img.get('src')
                if img_url:
                    new_url = self.download_image(img_url, title, published_date)
                    img['src'] = new_url

            # 将HTML转为Markdown
            html_content = str(content_elem)
            markdown_content = self.h2t.handle(html_content)

            # 处理Markdown中的图片链接
            def replace_img_url(match):
                img_url = match.group(1)

                # 如果是已经处理过的正确路径格式，则不再处理
                if img_url.startswith("assets/images/"):
                    return f"![image]({img_url})"

                new_url = self.download_image(img_url, title, published_date)
                return f"![image]({new_url})"

            markdown_content = re.sub(r'!\[.*?\]\((.*?)\)', replace_img_url, markdown_content)

            # 更新已处理文章记录
            self.processed_articles[article_url] = {
                'title': title,
                'date': published_date,
                'hash': content_hash
            }

            return title, markdown_content, published_date

        except Exception as e:
            logger.error(f"处理文章失败 {article_url}: {str(e)}")
            return None

    def save_as_jekyll_post(self, title, content, published_date):
        """
        将处理后的内容保存为Jekyll格式的Markdown文件
        :param title: 文章标题
        :param content: Markdown内容
        :param published_date: 发布日期
        :return: 保存的文件路径
        """
        try:
            # 创建文件名: yyyy-mm-dd-title.md
            safe_title = re.sub(r'[^a-zA-Z0-9\-_]', '-', title.lower())
            safe_title = re.sub(r'-+', '-', safe_title).strip('-')
            filename = f"{published_date}-{safe_title}.md"
            filepath = os.path.join(self.post_dir, filename)

            # 添加Jekyll头信息
            yaml_header = f"""---
layout: post
title: "{title}"
date: {published_date}
categories: blog
tags: [博客园迁移]
---

"""
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(yaml_header + content)

            logger.info(f"已保存文章: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"保存文章失败 {title}: {str(e)}")
            return None

    def run(self, start_page=1, max_pages=None, limit=None):
        """
        执行主流程
        :param start_page: 起始页码
        :param max_pages: 最大页数
        :param limit: 最大文章数限制
        """
        article_urls = self.get_article_list(start_page, max_pages)

        if limit and limit < len(article_urls):
            article_urls = article_urls[:limit]

        # 统计信息
        success_count = 0
        skip_count = 0
        update_count = 0

        try:
            for i, url in enumerate(article_urls):
                logger.info(f"处理第 {i + 1}/{len(article_urls)} 篇文章: {url}")

                # 检查是否已处理过且是增量模式
                is_update = False
                if self.incremental and url in self.processed_articles:
                    logger.info(f"检查文章是否有更新: {url}")
                    is_update = True

                result = self.process_article(url)

                if result is None and is_update:
                    skip_count += 1
                    continue

                if result:
                    title, content, published_date = result
                    filepath = self.save_as_jekyll_post(title, content, published_date)
                    if filepath:
                        if is_update:
                            update_count += 1
                            logger.info(f"更新文章: {title}")
                        else:
                            success_count += 1
                            logger.info(f"新增文章: {title}")

                # 每处理10篇文章保存一次记录，避免中断导致数据丢失
                if (i + 1) % 10 == 0:
                    self.save_processed_articles()

                # 适当延迟，避免请求过快
                time.sleep(1)

        finally:
            # 保存已处理文章记录
            self.save_processed_articles()

        mode_str = "增量更新" if self.incremental else "全量下载"
        logger.info(f"{mode_str}完成! 总计处理: {len(article_urls)} 篇文章")
        logger.info(f"新增: {success_count} 篇, 更新: {update_count} 篇, 跳过(无变化): {skip_count} 篇")
        logger.info(f"输出目录: {self.github_dir}")


def main():
    parser = argparse.ArgumentParser(description='将博客园博客迁移到GitHub Pages')
    parser.add_argument('-u', '--username', required=True, help='博客园用户名')
    parser.add_argument('-g', '--github-dir', required=True, help='本地GitHub仓库目录路径')
    parser.add_argument('-p', '--page', type=int, default=1, help='起始页码')
    parser.add_argument('-m', '--max-pages', type=int, help='最大页数')
    parser.add_argument('-l', '--limit', type=int, help='最大文章数限制')
    parser.add_argument('-f', '--full', action='store_true', help='全量下载模式，默认为增量更新模式')
    parser.add_argument('-b', '--base-url', default='', help='网站的基础URL路径（现在已不需要）')

    args = parser.parse_args()

    cnblogs2github = CnblogsToGitHub(
        username=args.username,
        github_dir=args.github_dir,
        incremental=not args.full,
        base_url=args.base_url
    )

    cnblogs2github.run(args.page, args.max_pages, args.limit)


if __name__ == '__main__':
    main()