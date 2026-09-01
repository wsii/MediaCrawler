# Obsidian 集成指南

## 🎯 概述

已将 MediaCrawler 修改为支持 **Obsidian 最优方案**，可将爬取数据直接导出为 Obsidian vault 格式。

## 📝 修改内容

### 1. 配置文件 (`config/base_config.py`)

添加了两个新配置项：

```python
# ==================== Obsidian 配置 ====================
# 是否启用 Obsidian 模式 - 将爬取数据导出为 Obsidian vault 格式
# 启用后，笔记保存为 Markdown 格式，媒体文件保存到 Attachments 文件夹
ENABLE_OBSIDIAN_MODE = False

# Obsidian vault 路径（本地 Obsidian 库的路径）
# 例如: "C:\\Users\\YourName\\Documents\\MyVault" 或 "/Users/YourName/Documents/MyVault"
# 如果为空，则使用 SAVE_DATA_PATH 作为基础路径
OBSIDIAN_VAULT_PATH = ""
```

### 2. 异步文件写入器 (`tools/async_file_writer.py`)

添加了以下功能：

#### a) `_get_attachments_path()` 方法
- 返回 Obsidian Attachments 路径
- 格式：`{vault_path}/Attachments/xhs/{note_id}`

#### b) `write_to_markdown()` 方法
生成 Markdown 格式的笔记，包含：
- YAML 前置属性（平台、作者、日期、统计数据）
- 笔记标题和正文
- 图片和视频引用（Obsidian 格式）
- 标签
- 来源链接

**使用示例：**
```python
writer = AsyncFileWriter(platform="xhs", crawler_type="search", note_id="123", title="如何赚钱")
markdown_path = await writer.write_to_markdown(content_item)
```

#### c) `_build_markdown_content()` 方法
构建完整的 Markdown 内容，自动生成 YAML 前置属性。

#### d) 修改的 `save_image()` / `save_video()` 方法
- **Obsidian 模式**：保存到 `Attachments/{platform}/{note_id}/images/` 或 `videos/`
- **普通模式**：保存到文章文件夹的 `images/` 或 `videos/`

### 3. 小红书媒体存储 (`store/xhs/xhs_store_media.py`)

修改了 `XiaoHongShuImage` 和 `XiaoHongShuVideo` 类：

#### 修改的 `_get_note_folder()` 方法
```python
if config.ENABLE_OBSIDIAN_MODE:
    # Obsidian 模式：使用 Attachments 结构
    return f"{self.base_path}/Attachments/{self.platform}/{note_id}"
else:
    # 普通模式：使用原始结构
    return f"{self.base_path}/{self.platform}/{timestamp}_{title}_{note_id}"
```

## 🚀 快速开始

### 步骤 1：启用 Obsidian 模式

编辑 `config/base_config.py`：

```python
# 启用 Obsidian 模式
ENABLE_OBSIDIAN_MODE = True

# 指定你的 Obsidian vault 路径
# Windows 示例：
OBSIDIAN_VAULT_PATH = "C:\\Users\\YourName\\Documents\\MyVault"

# macOS/Linux 示例：
# OBSIDIAN_VAULT_PATH = "/Users/YourName/Documents/MyVault"

# 如果为空，则使用 SAVE_DATA_PATH 作为基础路径
OBSIDIAN_VAULT_PATH = ""
```

### 步骤 2：运行爬虫

```bash
# 按照原有流程运行
python main.py
```

### 步骤 3：查看生成的结构

```
MyVault/
├── 小红书(XHS)/
│   ├── 2025年9月/
│   │   ├── 20250901_150000_如何赚钱_note123456.md
│   │   └── 20250901_151000_护肤技巧_note123457.md
│   └── 2025年10月/
├── 抖音(DY)/
├── 快手(KS)/
├── Attachments/
│   ├── xhs/
│   │   ├── note123456/
│   │   │   ├── images/
│   │   │   │   ├── pic_1.jpg
│   │   │   │   └── pic_2.jpg
│   │   │   └── videos/
│   │   │       └── video_1.mp4
│   │   └── note123457/
│   ├── dy/
│   └── ks/
└── Attachments.json (Obsidian metadata)
```

## 📄 Markdown 文件格式示例

```markdown
---
platform: "xhs"
note_id: "note123456"
author: "张三"
title: "如何赚钱"
date: 2025-09-01T15:00:00
liked: 1234
collected: 567
commented: 89
shared: 12
tags: ["赚钱", "副业", "创业"]
url: "https://www.xiaohongshu.com/..."
---

# 如何赚钱

## 内容描述
[原始文章内容]

## 统计数据
- **点赞数**: 1234
- **收藏数**: 567
- **评论数**: 89
- **分享数**: 12

## 配图
![[xhs/note123456/pic_1.jpg]]
![[xhs/note123456/pic_2.jpg]]

## 视频
![[xhs/note123456/video_1.mp4]]

## 标签
#赚钱 #副业 #创业 

---
*来源: XHS | 原始链接: https://www.xiaohongshu.com/...*
```

## ✨ Obsidian 增强功能

启用 Obsidian 模式后，你可以充分利用以下功能：

### 1. 双向链接
```markdown
相关笔记：[[20250901_150000_护肤技巧_note123457]]
同作者内容：[[20250902_旅游攻略_note123458]]
```

### 2. 标签系统
在 Obsidian 中按标签过滤和查找：
- `#赚钱` - 所有赚钱相关笔记
- `#平台/小红书` - 按平台分类
- `#时间/2025年9月` - 按时间分类

### 3. 元数据查询（使用 Dataview 插件）
```dataview
TABLE
  author,
  liked,
  collected,
  commented
FROM "小红书"
WHERE liked > 1000
SORT liked DESC
```

### 4. 全文搜索
使用 Obsidian 强大的全文搜索找到任何内容。

### 5. 图谱视图
可视化所有笔记之间的链接关系。

### 6. 媒体管理
- 所有图片和视频集中在 `Attachments/` 文件夹
- 自动渲染 Markdown 中的嵌入媒体
- 支持缩略图预览

## 🔄 模式切换

### 切换回普通模式

只需在配置中禁用 Obsidian 模式：

```python
ENABLE_OBSIDIAN_MODE = False
```

**数据存储位置会自动切换为：**
```
data/
├── xhs/
│   └── 20250901_150000_如何赚钱_note123456/
│       ├── contents.jsonl
│       ├── comments.jsonl
│       ├── images/
│       └── videos/
```

## ⚙️ 配置选项对比

| 选项 | 普通模式 | Obsidian 模式 |
|------|--------|-------------|
| **笔记格式** | JSONL/CSV | Markdown |
| **笔记位置** | `data/xhs/{note_folder}/` | `vault/小红书/年月/` |
| **媒体位置** | `data/xhs/{note_folder}/images/` | `vault/Attachments/xhs/{note_id}/` |
| **双向链接** | ❌ | ✅ |
| **标签系统** | ❌ | ✅ |
| **全文搜索** | ❌ | ✅ |
| **元数据查询** | ❌ | ✅ (需Dataview) |

## 🚨 注意事项

### 1. Vault 路径必须存在
- 确保指定的 Obsidian vault 路径已创建
- 程序会自动创建子文件夹，但不会创建 vault 本身

### 2. 媒体文件引用
- Markdown 中的媒体引用使用相对于 Attachments 的路径
- 格式：`![[xhs/note_id/pic_1.jpg]]`
- 需要在 vault 中打开文件才能正确显示

### 3. 文件夹命名
- 年月文件夹格式：`2025年9月`
- 笔记文件名格式：`{YYYYMMDD_HHMMSS}_{标题}_{note_id}.md`
- 非法字符会被自动替换为下划线

### 4. 性能考虑
- Obsidian 每次打开 vault 都会扫描所有文件
- 大量小文件（Attachments）可能影响性能
- 考虑定期存档旧数据

## 📊 存储容量估算

以爬取 1000 篇小红书文章为例：

| 项目 | 普通模式 | Obsidian 模式 |
|------|--------|-------------|
| 笔记文件 | 1 × JSONL (10-50 MB) | 1000 × Markdown (10-100 KB 每个) |
| 图片 (3 张/篇) | 3000 × JPG | 3000 × JPG (相同) |
| 总大小 | ~100-500 MB | ~100-500 MB |
| 文件数量 | ~3000 | ~4000 |
| Inode 占用 | 较低 | 较高 |

## 🔧 故障排除

### 问题 1：图片无法显示
- **原因**：Obsidian 没有正确找到图片
- **解决**：确保 Obsidian vault 路径正确，媒体文件确实存在

### 问题 2：链接失效
- **原因**：笔记文件名或文件夹名不一致
- **解决**：检查文件夹名称是否包含非法字符

### 问题 3：YAML 前置属性格式错误
- **原因**：标签或其他字段包含特殊字符
- **解决**：这应该不会发生，如有问题请报告

## 📚 进阶用法

### 与数据库并行存储
```python
# config/base_config.py
ENABLE_OBSIDIAN_MODE = True  # 导出到 Obsidian
SAVE_DATA_OPTION = "sqlite"  # 同时保存到数据库
```

### 定期备份
```bash
# 定期备份 Obsidian vault
cp -r /path/to/vault /path/to/backup/vault_$(date +%Y%m%d)
```

### 批量导入历史数据
可以编写脚本将旧的 JSONL/CSV 数据转换为 Markdown 格式导入 Obsidian。

## ✅ 检查清单

使用 Obsidian 模式前，确保：

- [ ] Obsidian 已安装
- [ ] Vault 已创建
- [ ] `ENABLE_OBSIDIAN_MODE = True` 已设置
- [ ] `OBSIDIAN_VAULT_PATH` 指向正确的 vault 位置
- [ ] 至少启用了 `ENABLE_GET_MEIDAS = True` 以下载图片/视频

## 🎉 开始使用

现在你可以开始使用 Obsidian 模式！

1. **配置** Obsidian vault 路径
2. **启用** Obsidian 模式
3. **运行** 爬虫
4. **打开** Obsidian vault 查看导出的数据

所有爬取的数据将自动组织成优雅的 Markdown 笔记，准备好进行知识管理！🚀
