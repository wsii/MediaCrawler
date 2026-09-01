# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tools/async_file_writer.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#
# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

import asyncio
import csv
import json
import os
import pathlib
from typing import Dict, List, Optional
import aiofiles
import config
from tools.utils import utils
from tools.words import AsyncWordCloudGenerator
from tools.time_util import get_current_timestamp

class AsyncFileWriter:
    def __init__(self, platform: str, crawler_type: str, note_id: Optional[str] = None, title: Optional[str] = None):
        self.lock = asyncio.Lock()
        self.platform = platform
        self.crawler_type = crawler_type
        self.note_id = note_id
        self.title = title
        self.wordcloud_generator = AsyncWordCloudGenerator() if config.ENABLE_GET_WORDCLOUD else None
        self.note_folder = None  # 缓存文章文件夹路径
        
    def _sanitize_filename(self, filename: str, max_length: int = 50) -> str:
        """
        清理文件名，移除非法字符，限制长度
        :param filename: 原始文件名
        :param max_length: 最大长度
        :return: 清理后的文件名
        """
        # 移除非法字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 限制长度
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        return filename.strip()

    def _get_note_folder(self) -> str:
        """
        获取或创建文章专用文件夹
        命名格式: {timestamp}_{sanitized_title}_{note_id}
        :return: 文章文件夹路径
        """
        if self.note_folder:
            return self.note_folder
            
        if not self.note_id:
            # 如果没有note_id，使用旧的方式（向下兼容）
            if config.SAVE_DATA_PATH:
                return f"{config.SAVE_DATA_PATH}/{self.platform}"
            else:
                return f"data/{self.platform}"
        
        # 生成文件夹名称：时间戳_标题_note_id
        timestamp = self._get_current_time_str()
        title_clean = self._sanitize_filename(self.title or "untitled", max_length=50)
        folder_name = f"{timestamp}_{title_clean}_{self.note_id}"
        
        if config.SAVE_DATA_PATH:
            note_folder = f"{config.SAVE_DATA_PATH}/{self.platform}/{folder_name}"
        else:
            note_folder = f"data/{self.platform}/{folder_name}"
        
        pathlib.Path(note_folder).mkdir(parents=True, exist_ok=True)
        self.note_folder = note_folder
        return note_folder
    
    def _get_current_time_str(self) -> str:
        """
        获取当前时间字符串格式：20250901_150000
        :return: 时间字符串
        """
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_file_path(self, file_type: str, item_type: str) -> str:
        """
        获取文件路径，文件直接存储在文章文件夹内
        :param file_type: 文件类型 (csv, json, jsonl)
        :param item_type: 内容类型 (contents, comments)
        :return: 文件完整路径
        """
        note_folder = self._get_note_folder()
        
        # 文件名：{item_type}.{file_type}
        file_name = f"{item_type}.{file_type}"
        file_path = f"{note_folder}/{file_name}"
        
        return file_path

    async def write_to_csv(self, item: Dict, item_type: str):
        """
        写入CSV文件（向下兼容，所有数据存储在文章文件夹内）
        :param item: 数据项
        :param item_type: 内容类型
        """
        file_path = self._get_file_path('csv', item_type)
        async with self.lock:
            file_exists = os.path.exists(file_path)
            async with aiofiles.open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=item.keys())
                if not file_exists or await f.tell() == 0:
                    await writer.writeheader()
                await writer.writerow(item)

    async def write_to_jsonl(self, item: Dict, item_type: str):
        """
        写入JSONL文件，每行一个JSON对象
        :param item: 数据项
        :param item_type: 内容类型
        """
        file_path = self._get_file_path('jsonl', item_type)
        async with self.lock:
            async with aiofiles.open(file_path, 'a', encoding='utf-8') as f:
                await f.write(json.dumps(item, ensure_ascii=False) + '\n')

    async def write_single_item_to_json(self, item: Dict, item_type: str):
        """
        写入JSON文件，将所有数据合并为数组
        :param item: 数据项
        :param item_type: 内容类型
        """
        file_path = self._get_file_path('json', item_type)
        async with self.lock:
            existing_data = []
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        content = await f.read()
                        if content:
                            existing_data = json.loads(content)
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
                    except json.JSONDecodeError:
                        existing_data = []

            existing_data.append(item)

            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(existing_data, ensure_ascii=False, indent=4))
    
    def _get_attachments_path(self) -> str:
        """
        获取 Obsidian Attachments 路径
        用于 Obsidian 模式下的媒体存储
        :return: Attachments 路径
        """
        if not config.ENABLE_OBSIDIAN_MODE:
            # 不使用 Obsidian 模式，返回相对于笔记的 images 路径
            return None
        
        vault_path = config.OBSIDIAN_VAULT_PATH or config.SAVE_DATA_PATH or "data"
        attachments_path = f"{vault_path}/Attachments/{self.platform}/{self.note_id}"
        return attachments_path

    async def save_image(self, image_content: bytes, filename: str) -> str:
        """
        保存图片到文章文件夹的 images 子目录（或 Obsidian Attachments）
        :param image_content: 图片二进制内容
        :param filename: 图片文件名
        :return: 保存路径
        """
        # Obsidian 模式：保存到 Attachments/xhs/{note_id}/
        attachments_path = self._get_attachments_path()
        if attachments_path:
            images_folder = f"{attachments_path}/images"
        else:
            # 普通模式：保存到文章文件夹/images/
            note_folder = self._get_note_folder()
            images_folder = f"{note_folder}/images"
        
        pathlib.Path(images_folder).mkdir(parents=True, exist_ok=True)
        
        file_path = f"{images_folder}/{filename}"
        async with self.lock:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(image_content)
        
        return file_path
    
    async def save_video(self, video_content: bytes, filename: str) -> str:
        """
        保存视频到文章文件夹的 videos 子目录（或 Obsidian Attachments）
        :param video_content: 视频二进制内容
        :param filename: 视频文件名
        :return: 保存路径
        """
        # Obsidian 模式：保存到 Attachments/xhs/{note_id}/
        attachments_path = self._get_attachments_path()
        if attachments_path:
            videos_folder = f"{attachments_path}/videos"
        else:
            # 普通模式：保存到文章文件夹/videos/
            note_folder = self._get_note_folder()
            videos_folder = f"{note_folder}/videos"
        
        pathlib.Path(videos_folder).mkdir(parents=True, exist_ok=True)
        
        file_path = f"{videos_folder}/{filename}"
        async with self.lock:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(video_content)
        
        return file_path

    async def write_to_markdown(self, content_item: Dict) -> str:
        """
        生成 Markdown 格式的笔记（用于 Obsidian）
        :param content_item: 内容项（包含标题、描述、统计数据等）
        :return: Markdown 文件路径
        """
        if not config.ENABLE_OBSIDIAN_MODE:
            raise ValueError("Obsidian 模式未启用")
        
        # 构建 Markdown 内容
        markdown_content = self._build_markdown_content(content_item)
        
        # 确定保存位置
        vault_path = config.OBSIDIAN_VAULT_PATH or config.SAVE_DATA_PATH or "data"
        
        # 获取年月文件夹
        from datetime import datetime
        year_month = datetime.now().strftime("%Y年%m月")
        
        # 构建文件名和路径
        title_clean = self._sanitize_filename(self.title or "untitled", 50)
        timestamp = self._get_current_time_str()
        filename = f"{timestamp}_{title_clean}_{self.note_id}.md"
        
        # 根据平台创建文件夹
        platform_display = {
            "xhs": "小红书(XHS)",
            "dy": "抖音(DY)",
            "ks": "快手(KS)",
            "bili": "Bilibili",
            "weibo": "微博",
            "tieba": "百度贴吧",
            "zhihu": "知乎"
        }
        platform_name = platform_display.get(self.platform, self.platform)
        
        note_dir = f"{vault_path}/{platform_name}/{year_month}"
        pathlib.Path(note_dir).mkdir(parents=True, exist_ok=True)
        
        file_path = f"{note_dir}/{filename}"
        
        # 写入文件
        async with self.lock:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(markdown_content)
        
        return file_path

    def _build_markdown_content(self, content_item: Dict) -> str:
        """
        构建 Markdown 内容，包括 YAML 前置属性和正文
        :param content_item: 内容项
        :return: Markdown 格式的字符串
        """
        import json
        from datetime import datetime
        
        # YAML 前置属性
        yaml_header = f"""---
platform: "{self.platform}"
note_id: "{content_item.get('note_id', '')}"
author: "{content_item.get('creator', content_item.get('nickname', ''))}"
title: "{content_item.get('title', '')}"
date: {content_item.get('create_time', datetime.now().isoformat())}
liked: {content_item.get('liked_count', 0)}
collected: {content_item.get('collected_count', 0)}
commented: {content_item.get('comment_count', 0)}
shared: {content_item.get('share_count', 0)}
tags: {json.dumps(content_item.get('tag_list', [])).replace('"', '')}
url: "{content_item.get('note_url', '')}"
---
"""
        
        # Markdown 正文
        title = content_item.get('title', '未命名')
        desc = content_item.get('desc', '')
        
        markdown_body = f"""# {title}

## 内容描述
{desc}

## 统计数据
- **点赞数**: {content_item.get('liked_count', 0)}
- **收藏数**: {content_item.get('collected_count', 0)}
- **评论数**: {content_item.get('comment_count', 0)}
- **分享数**: {content_item.get('share_count', 0)}

## 配图
"""
        
        # 添加图片引用
        image_list = content_item.get('image_list', [])
        if image_list:
            for idx, img_url in enumerate(image_list, 1):
                markdown_body += f"![[{self.platform}/{self.note_id}/pic_{idx}.jpg]]\n"
        else:
            markdown_body += "（无配图）\n"
        
        # 添加视频
        markdown_body += "\n## 视频\n"
        if content_item.get('video_url'):
            markdown_body += f"![[{self.platform}/{self.note_id}/video_1.mp4]]\n"
        else:
            markdown_body += "（无视频）\n"
        
        # 标签
        tag_list = content_item.get('tag_list', [])
        if tag_list:
            markdown_body += f"\n## 标签\n"
            for tag in tag_list:
                markdown_body += f"#{tag} "
            markdown_body += "\n"
        
        # 源信息
        markdown_body += f"\n---\n*来源: {self.platform.upper()} | 原始链接: {content_item.get('note_url', 'N/A')}*\n"
        
        return yaml_header + markdown_body

    async def generate_wordcloud_from_comments(self):
        """
        从评论数据生成词云
        仅在 ENABLE_GET_WORDCLOUD 和 ENABLE_GET_COMMENTS 都为 True 时工作
        """
        if not config.ENABLE_GET_WORDCLOUD or not config.ENABLE_GET_COMMENTS:
            return

        if not self.wordcloud_generator:
            return

        try:
            note_folder = self._get_note_folder()
            
            # 从 JSON 或 JSONL 文件读取评论
            comments_data = []
            jsonl_file_path = f"{note_folder}/comments.jsonl"
            json_file_path = f"{note_folder}/comments.json"

            if os.path.exists(jsonl_file_path) and os.path.getsize(jsonl_file_path) > 0:
                async with aiofiles.open(jsonl_file_path, 'r', encoding='utf-8') as f:
                    async for line in f:
                        line = line.strip()
                        if line:
                            try:
                                comments_data.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
            elif os.path.exists(json_file_path) and os.path.getsize(json_file_path) > 0:
                async with aiofiles.open(json_file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if content:
                        comments_data = json.loads(content)
                        if not isinstance(comments_data, list):
                            comments_data = [comments_data]

            if not comments_data:
                utils.logger.info(f"[AsyncFileWriter.generate_wordcloud_from_comments] 未找到评论数据")
                return

            # 过滤评论数据，仅保留内容字段
            filtered_data = []
            for comment in comments_data:
                if isinstance(comment, dict):
                    # 尝试不同的内容字段名
                    content_text = comment.get('content') or comment.get('comment_text') or comment.get('text') or ''
                    if content_text:
                        filtered_data.append({'content': content_text})

            if not filtered_data:
                utils.logger.info(f"[AsyncFileWriter.generate_wordcloud_from_comments] 未找到有效的评论内容")
                return

            # 生成词云
            words_folder = f"{note_folder}/wordcloud"
            pathlib.Path(words_folder).mkdir(parents=True, exist_ok=True)
            words_file_prefix = f"{words_folder}/comments_wordcloud"

            utils.logger.info(f"[AsyncFileWriter.generate_wordcloud_from_comments] 正在生成词云，共 {len(filtered_data)} 条评论")
            await self.wordcloud_generator.generate_word_frequency_and_cloud(filtered_data, words_file_prefix)
            utils.logger.info(f"[AsyncFileWriter.generate_wordcloud_from_comments] 词云生成成功: {words_file_prefix}")

        except Exception as e:
            utils.logger.error(f"[AsyncFileWriter.generate_wordcloud_from_comments] 生成词云出错: {e}")
