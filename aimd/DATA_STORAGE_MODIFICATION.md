# 小红书数据存储结构改动说明

## 📦 改动概述

已修改代码实现 **每篇文章一个文件夹** 的数据组织方式，所有相关文件（内容、评论、图片、视频、词云等）都存储在同一个文章文件夹内。

---

## 🗂️ 新的目录结构

### 文件夹命名规则

```
{时间戳}_{文章标题}_{note_id}
```

| 组件 | 说明 | 示例 |
|------|------|------|
| 时间戳 | 爬取该文章时的时间（YYYYMMDD_HHMMSS） | `20250901_150000` |
| 文章标题 | 自动清理非法字符，最多50字 | `如何副业赚钱` |
| note_id | 文章唯一ID | `64b95d01000000000c034587` |

### 完整目录树

```
data/xhs/
├── 20250901_150000_如何赚钱_64b95d01000000000c034587/
│   ├── contents.jsonl                    ← 文章内容（按格式选择）
│   ├── comments.jsonl                    ← 评论数据
│   ├── images/                           ← 图片文件夹
│   │   ├── image_001.jpg
│   │   ├── image_002.jpg
│   │   └── ...
│   ├── videos/                           ← 视频文件夹
│   │   ├── video_001.mp4
│   │   └── ...
│   └── wordcloud/                        ← 词云生成结果
│       ├── comments_wordcloud.png
│       └── word_frequency.csv
│
├── 20250901_160000_抖音涨粉技巧_789abc123def456/
│   ├── contents.jsonl
│   ├── comments.jsonl
│   ├── images/
│   ├── videos/
│   └── wordcloud/
│
└── ...
```

---

## 🔧 修改的文件

### 1️⃣ `tools/async_file_writer.py`

**新增参数**：
```python
AsyncFileWriter(
    platform: str,                    # 平台名称 (xhs, dy 等)
    crawler_type: str,                # 爬取类型 (search, detail, creator)
    note_id: Optional[str] = None,    # 【新增】文章ID
    title: Optional[str] = None       # 【新增】文章标题
)
```

**核心方法**：
- `_get_note_folder()` - 获取或创建文章文件夹
- `_sanitize_filename()` - 清理非法字符
- `save_image()` - 保存图片到 `images/` 子目录
- `save_video()` - 保存视频到 `videos/` 子目录

**向下兼容**：
- 如果不提供 `note_id` 和 `title`，会使用旧的路径方式
- 自动处理所有文件格式（JSON、JSONL、CSV）

### 2️⃣ `store/xhs/_store_impl.py`

**修改的类**：
- `XhsCsvStoreImplement`
- `XhsJsonStoreImplement`
- `XhsJsonlStoreImplement`

**关键改动**：
```python
class XhsJsonlStoreImplement(AbstractStore):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.writer_cache = {}  # 【新增】缓存不同文章的writer

    async def store_content(self, content_item: Dict):
        note_id = content_item.get("note_id")
        title = content_item.get("title")
        
        # 为每篇文章创建独立的writer
        if note_id not in self.writer_cache:
            self.writer_cache[note_id] = AsyncFileWriter(
                platform="xhs",
                crawler_type=crawler_type_var.get(),
                note_id=note_id,        # 【新增】
                title=title             # 【新增】
            )
        
        writer = self.writer_cache[note_id]
        await writer.write_to_jsonl(item_type="contents", item=content_item)
```

**好处**：
- ✅ 自动为每篇文章创建独立文件夹
- ✅ 文章数据完全隔离
- ✅ 便于单篇文章的管理和处理

### 3️⃣ `store/xhs/xhs_store_media.py`

**修改的类**：
- `XiaoHongShuImage`
- `XiaoHongShuVideo`

**核心改动**：
```python
async def store_image(self, image_content_item: Dict):
    """
    保存图片到文章文件夹的 images 子目录
    
    参数格式：
    {
        "note_id": "xxx123",           # 文章ID
        "title": "文章标题",           # 文章标题
        "pic_content": b'...',         # 图片二进制
        "extension_file_name": "image_001.jpg"
    }
    """
    note_id = image_content_item.get("note_id")
    title = image_content_item.get("title")
    pic_content = image_content_item.get("pic_content")
    extension_file_name = image_content_item.get("extension_file_name")
    
    await self.save_image(note_id, title, pic_content, extension_file_name)
```

**改进点**：
- 图片和视频不再存储在全局的 `images/videos` 文件夹
- 每篇文章的图片存储在对应文件夹的 `images/` 子目录
- 每篇文章的视频存储在对应文件夹的 `videos/` 子目录

---

## 📊 数据格式支持

### 文件存储格式

| 格式 | 文件名 | 特点 |
|------|--------|------|
| **JSONL** | `contents.jsonl`<br>`comments.jsonl` | ⭐ 推荐，流式写入，适合大数据 |
| **JSON** | `contents.json`<br>`comments.json` | 结构化，可读性强 |
| **CSV** | `contents.csv`<br>`comments.csv` | 可在Excel打开 |

### 配置方式

```python
# config/base_config.py

# 选择保存格式
SAVE_DATA_OPTION = "jsonl"  # json / jsonl / csv

# 自定义保存路径（默认 data/）
SAVE_DATA_PATH = "/path/to/data"

# 启用图片/视频下载
ENABLE_GET_MEIDAS = True

# 启用评论爬取
ENABLE_GET_COMMENTS = True

# 启用词云生成
ENABLE_GET_WORDCLOUD = True
```

---

## 🎯 使用示例

### 爬取小红书并组织数据

```python
import asyncio
from main import CrawlerFactory
import config

async def main():
    # 配置
    config.PLATFORM = "xhs"
    config.KEYWORDS = "编程副业"
    config.CRAWLER_TYPE = "search"
    config.SAVE_DATA_OPTION = "jsonl"
    config.ENABLE_GET_MEIDAS = True
    config.ENABLE_GET_COMMENTS = True
    
    # 爬取
    crawler = CrawlerFactory.create_crawler("xhs")
    await crawler.start()

asyncio.run(main())
```

### 结果目录结构

爬取完成后，数据将自动按以下结构组织：

```
data/xhs/
├── 20250901_150000_编程赚钱方法_note123/
│   ├── contents.jsonl
│   ├── comments.jsonl
│   ├── images/
│   │   ├── image_001.jpg
│   │   └── image_002.jpg
│   └── videos/
│       └── video_001.mp4
│
└── 20250901_151000_副业指南_note456/
    ├── contents.jsonl
    ├── comments.jsonl
    ├── images/
    └── videos/
```

---

## ⚠️ 重要事项

### 1️⃣ 时间戳冲突

**问题**：如果在同一秒内爬取相同标题的两篇文章，会产生相同的文件夹名。

**解决方案**：
- 文件夹名包含 `note_id`，即使标题相同也不会覆盖
- 但建议在实际应用中添加更精细的时间粒度（毫秒）

### 2️⃣ 文件名清理

**自动处理的非法字符**：`< > : " / \ | ? *`
- 这些字符会被替换为 `_`
- 文件夹名限制最多50字符

**示例**：
```
原标题：  如何用抖音赚钱？2024年最新方法！
处理后：  如何用抖音赚钱_2024年最新方法
```

### 3️⃣ 路径编码

**Windows 中文路径**：
- Python 3.11+ 默认支持UTF-8
- 确保文件系统和编辑器都使用UTF-8编码
- 如有问题，可修改配置使用拼音或ID代替中文

### 4️⃣ 数据库存储

**注意**：数据库存储（SQLite、MySQL等）不受此改动影响
- 数据库中的数据结构保持不变
- 每条记录仍存储完整信息
- 文件存储和数据库可并行使用

---

## 📈 迁移指南

### 从旧版本升级

如果之前使用旧的存储方式，需要注意：

```
【旧结构】                          【新结构】
data/xhs/                         data/xhs/
├── csv/                          ├── {timestamp}_{title}_{id}/
│   └── search_contents_*.csv     │   ├── contents.csv
├── json/                         │   ├── comments.csv
│   └── search_contents_*.json    │   ├── images/
├── jsonl/                        │   └── videos/
│   └── search_contents_*.jsonl   │
├── images/                       └── ...
│   └── {note_id}/
└── videos/
    └── {note_id}/
```

**迁移步骤**：
1. 保留旧数据（不会自动删除）
2. 新爬取的数据使用新结构
3. 可编写脚本手动迁移旧数据（如需要）

---

## 🔍 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 文件夹名包含乱码 | 编码问题 | 检查系统和Python编码设置 |
| 文件夹名过长 | 标题太长 | 自动截断到50字符 |
| 找不到图片/视频 | 未启用媒体下载 | 设置 `ENABLE_GET_MEIDAS = True` |
| 数据保存到错误的位置 | `note_id`为空 | 检查爬虫实现，确保提取了note_id |

---

## 📚 相关配置

```python
# config/base_config.py

# 平台选择
PLATFORM = "xhs"

# 数据保存选项
SAVE_DATA_OPTION = "jsonl"           # json/jsonl/csv/sqlite/mysql/postgres

# 保存路径
SAVE_DATA_PATH = ""                  # 留空使用 data/ 目录

# 媒体下载
ENABLE_GET_MEIDAS = False            # 改为 True 启用图片/视频下载

# 评论爬取
ENABLE_GET_COMMENTS = True           # 是否爬取评论
CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = 10  # 单篇文章的评论数

# 词云生成
ENABLE_GET_WORDCLOUD = False         # 改为 True 启用词云
CUSTOM_WORDS = {...}                 # 自定义词汇
STOP_WORDS_FILE = "./docs/hit_stopwords.txt"  # 停用词文件
FONT_PATH = "./docs/STZHONGS.TTF"    # 中文字体路径
```

---

## ✅ 总结

| 方面 | 改进 |
|------|------|
| **组织方式** | 从全局分类 → 按文章分组 |
| **数据隔离** | 每篇文章完全独立 |
| **易管理性** | ⭐⭐⭐⭐⭐ 大幅提升 |
| **向下兼容** | ✅ 保持向下兼容 |
| **数据库** | ✅ 不影响数据库存储 |
| **文件路径** | 自动生成和管理 |
