# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。

"""
小红书个人收藏增量同步记录

通过 JSON 文件持久化「已经同步到本地的收藏链接」，
每次同步时跳过已记录过的链接，仅同步新增收藏。
"""

import json
import os
import pathlib
from typing import Dict, List, Set

from tools import utils
from tools.time_util import get_current_timestamp


class FavoritesSyncRecord:
    """基于 JSON 文件的收藏同步记录，用于增量去重。"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.records: List[Dict] = []
        self.synced_urls: Set[str] = set()
        self._load()

    def _load(self) -> None:
        """从磁盘加载已同步记录"""
        if not self.file_path or not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            records = data.get("synced", []) if isinstance(data, dict) else []
            for item in records:
                if not isinstance(item, dict):
                    continue
                url = item.get("note_url")
                if url:
                    self.synced_urls.add(url)
                    self.records.append(item)
        except (OSError, json.JSONDecodeError) as e:
            utils.logger.warning(
                f"[FavoritesSyncRecord._load] 读取同步记录失败: {e}，将重新开始"
            )
            self.records = []
            self.synced_urls = set()

    def contains(self, note_url: str) -> bool:
        """判断指定链接是否已经同步过"""
        return note_url in self.synced_urls

    def add(self, note_url: str, note_id: str = "", title: str = "") -> None:
        """新增一条已同步记录(内存中，需调用 save 持久化)"""
        if not note_url or note_url in self.synced_urls:
            return
        self.records.append(
            {
                "note_url": note_url,
                "note_id": note_id,
                "title": title,
                "sync_time": get_current_timestamp(),
            }
        )
        self.synced_urls.add(note_url)

    def save(self) -> None:
        """将同步记录写入 JSON 文件"""
        if not self.file_path:
            return
        try:
            pathlib.Path(os.path.dirname(self.file_path)).mkdir(parents=True, exist_ok=True)
            payload = {
                "version": 1,
                "last_sync_ts": get_current_timestamp(),
                "synced": self.records,
            }
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            utils.logger.info(
                f"[FavoritesSyncRecord.save] 同步记录已写入: {self.file_path} "
                f"(共 {len(self.records)} 条)"
            )
        except OSError as e:
            utils.logger.error(f"[FavoritesSyncRecord.save] 写入同步记录失败: {e}")

    def __len__(self) -> int:
        return len(self.synced_urls)
