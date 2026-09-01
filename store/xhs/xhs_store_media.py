# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/store/xhs/xhs_store_media.py
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

# -*- coding: utf-8 -*-
# @Author  : helloteemo
# @Time    : 2024/7/11 22:35
# @Desc    : Xiaohongshu media storage
import pathlib
from typing import Dict, Optional
from datetime import datetime

import aiofiles

from base.base_crawler import AbstractStoreImage, AbstractStoreVideo
from tools import utils
import config


class XiaoHongShuImage(AbstractStoreImage):
    def __init__(self):
        """初始化，根据 Obsidian 模式选择存储位置"""
        if config.ENABLE_OBSIDIAN_MODE:
            self.base_path = config.OBSIDIAN_VAULT_PATH if config.OBSIDIAN_VAULT_PATH else config.SAVE_DATA_PATH if config.SAVE_DATA_PATH else "data"
        else:
            self.base_path = config.SAVE_DATA_PATH if config.SAVE_DATA_PATH else "data"
        self.platform = "xhs"

    def _sanitize_filename(self, filename: str, max_length: int = 50) -> str:
        """
        清理文件名，移除非法字符，限制长度
        :param filename: 原始文件名
        :param max_length: 最大长度
        :return: 清理后的文件名
        """
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        return filename.strip()

    def _get_current_time_str(self) -> str:
        """获取当前时间字符串格式：20250901_150000"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_note_folder(self, note_id: str, title: Optional[str] = None) -> str:
        """
        获取文章文件夹路径
        :param note_id: 笔记ID
        :param title: 笔记标题
        :return: 文章文件夹路径
        """
        title_clean = self._sanitize_filename(title or "untitled", max_length=50)
        timestamp = self._get_current_time_str()
        folder_name = f"{timestamp}_{title_clean}_{note_id}"
        return f"{self.base_path}/{self.platform}/{folder_name}"

    async def store_image(self, image_content_item: Dict):
        """
        保存图片到文章文件夹的 images 子目录
        
        Args:
            image_content_item: 包含以下字段
                - note_id: 笔记ID
                - title: 笔记标题（可选）
                - pic_content: 图片二进制内容
                - extension_file_name: 图片文件名（带扩展名）
        """
        note_id = image_content_item.get("note_id")
        title = image_content_item.get("title", "untitled")
        pic_content = image_content_item.get("pic_content")
        extension_file_name = image_content_item.get("extension_file_name")
        
        if not note_id or not pic_content or not extension_file_name:
            utils.logger.warning("[XiaoHongShuImage.store_image] 缺少必要参数")
            return
        
        await self.save_image(note_id, title, pic_content, extension_file_name)

    async def save_image(self, note_id: str, title: str, pic_content: bytes, extension_file_name: str):
        """
        保存图片到文章文件夹
        
        Args:
            note_id: 笔记ID
            title: 笔记标题
            pic_content: 图片二进制内容
            extension_file_name: 图片文件名
        """
        note_folder = self._get_note_folder(note_id, title)
        images_folder = f"{note_folder}/images"
        pathlib.Path(images_folder).mkdir(parents=True, exist_ok=True)
        
        save_file_name = f"{images_folder}/{extension_file_name}"
        async with aiofiles.open(save_file_name, 'wb') as f:
            await f.write(pic_content)
        
        utils.logger.info(f"[XiaoHongShuImage.save_image] 图片保存成功: {save_file_name}")


class XiaoHongShuVideo(AbstractStoreVideo):
    def __init__(self):
        """初始化，根据 Obsidian 模式选择存储位置"""
        if config.ENABLE_OBSIDIAN_MODE:
            self.base_path = config.OBSIDIAN_VAULT_PATH if config.OBSIDIAN_VAULT_PATH else config.SAVE_DATA_PATH if config.SAVE_DATA_PATH else "data"
        else:
            self.base_path = config.SAVE_DATA_PATH if config.SAVE_DATA_PATH else "data"
        self.platform = "xhs"

    def _sanitize_filename(self, filename: str, max_length: int = 50) -> str:
        """
        清理文件名，移除非法字符，限制长度
        :param filename: 原始文件名
        :param max_length: 最大长度
        :return: 清理后的文件名
        """
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        return filename.strip()

    def _get_current_time_str(self) -> str:
        """获取当前时间字符串格式：20250901_150000"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_note_folder(self, note_id: str, title: Optional[str] = None) -> str:
        """
        获取文章文件夹路径或 Attachments 路径
        Obsidian 模式：返回 Attachments/xhs/{note_id}
        普通模式：返回 data/xhs/{timestamp}_{title}_{note_id}
        :param note_id: 笔记ID
        :param title: 笔记标题
        :return: 文章文件夹路径
        """
        if config.ENABLE_OBSIDIAN_MODE:
            # Obsidian 模式：使用 Attachments 结构
            return f"{self.base_path}/Attachments/{self.platform}/{note_id}"
        else:
            # 普通模式：使用原始结构
            title_clean = self._sanitize_filename(title or "untitled", max_length=50)
            timestamp = self._get_current_time_str()
            folder_name = f"{timestamp}_{title_clean}_{note_id}"
            return f"{self.base_path}/{self.platform}/{folder_name}"

    async def store_video(self, video_content_item: Dict):
        """
        保存视频到文章文件夹的 videos 子目录
        
        Args:
            video_content_item: 包含以下字段
                - note_id: 笔记ID
                - title: 笔记标题（可选）
                - video_content: 视频二进制内容
                - extension_file_name: 视频文件名（带扩展名）
        """
        note_id = video_content_item.get("note_id")
        title = video_content_item.get("title", "untitled")
        video_content = video_content_item.get("video_content")
        extension_file_name = video_content_item.get("extension_file_name")
        
        if not note_id or not video_content or not extension_file_name:
            utils.logger.warning("[XiaoHongShuVideo.store_video] 缺少必要参数")
            return
        
        await self.save_video(note_id, title, video_content, extension_file_name)

    async def save_video(self, note_id: str, title: str, video_content: bytes, extension_file_name: str):
        """
        保存视频到文章文件夹
        
        Args:
            note_id: 笔记ID
            title: 笔记标题
            video_content: 视频二进制内容
            extension_file_name: 视频文件名
        """
        note_folder = self._get_note_folder(note_id, title)
        videos_folder = f"{note_folder}/videos"
        pathlib.Path(videos_folder).mkdir(parents=True, exist_ok=True)
        
        save_file_name = f"{videos_folder}/{extension_file_name}"
        async with aiofiles.open(save_file_name, 'wb') as f:
            await f.write(video_content)
        
        utils.logger.info(f"[XiaoHongShuVideo.save_video] 视频保存成功: {save_file_name}")
