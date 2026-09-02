# MediaCrawler 运行脚本指南

本项目提供多种便捷的批处理脚本，方便快速启动爬虫任务。

## 📋 可用的 BAT 脚本

### 1. **run_crawler.bat** - 爬虫启动器（推荐）
交互式菜单，选择不同的爬虫平台和参数。

**使用方式：**
```bash
run_crawler.bat
```

**功能：**
- ✓ 小红书搜索爬虫（预设参数）
- ✓ 抖音搜索爬虫
- ✓ 快手搜索爬虫
- ✓ Bilibili 搜索爬虫
- ✓ 微博搜索爬虫
- ✓ 自定义参数运行
- ✓ 友好的交互式界面

**示例：**
运行脚本后，按数字 1-6 选择对应的爬虫类型。

---

### 2. **run_quick.bat** - 快速启动脚本
一行命令启动爬虫，支持传递参数。

**使用方式：**
```bash
# 使用默认参数 (小红书, 编程副业, 5条)
run_quick.bat

# 自定义平台
run_quick.bat dy 短视频 10

# 自定义所有参数
run_quick.bat xhs "python编程" 20
```

**参数说明：**
- 参数 1：平台 (xhs/dy/ks/bili/wb/tieba/zhihu)，默认 xhs
- 参数 2：关键词，默认 "编程副业"
- 参数 3：最大爬虫数量，默认 5

**示例：**
```bash
# 爬虫小红书，关键词为"美妆教程"，最多爬取 15 条
run_quick.bat xhs 美妆教程 15

# 爬虫抖音，关键词为"Vlog"，最多爬取 20 条
run_quick.bat dy Vlog 20
```

---

### 3. **run_webui.bat** - WebUI 开发服务器
启动前端开发服务器。

**使用方式：**
```bash
run_webui.bat
```

**访问地址：**
- 本地: http://localhost:5173/
- 停止: 按 Ctrl+C

**功能：**
- ✓ 热更新（修改代码自动刷新）
- ✓ 开发者工具集成
- ✓ 实时编译 TypeScript

---

### 4. **run_api.bat** - API 服务启动器
启动 FastAPI 后端服务器。

**使用方式：**
```bash
run_api.bat
```

**访问地址：**
- API: http://localhost:8000/
- Swagger UI 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc
- 停止: 按 Ctrl+C

**功能：**
- ✓ RESTful API 服务
- ✓ 自动热重载
- ✓ 完整的 API 文档

---

## 🚀 常见使用场景

### 场景 1：简单爬虫任务
```bash
# 方式 A: 使用快速启动
run_quick.bat xhs 副业赚钱 10

# 方式 B: 使用菜单选择
run_crawler.bat
# 然后选择 1（小红书）
```

### 场景 2：多平台爬虫
```bash
# 先爬虫小红书
run_quick.bat xhs 编程 5

# 再爬虫抖音
run_quick.bat dy 编程 5

# 再爬虫快手
run_quick.bat ks 编程 5
```

### 场景 3：开发环境
```bash
# 终端 1: 启动 API 后端
run_api.bat

# 终端 2: 启动 WebUI 前端
run_webui.bat

# 终端 3: 运行爬虫任务
run_quick.bat xhs 测试 5
```

### 场景 4：生产环境
```bash
# 直接运行爬虫（后台无交互）
run_quick.bat xhs "关键词" 100
```

---

## ⚙️ 支持的平台

| 平台代码 | 平台名称 | 爬虫类型 |
|---------|---------|--------|
| **xhs** | 小红书 | search / detail / creator |
| **dy** | 抖音 | search / detail / creator |
| **ks** | 快手 | search / detail / creator |
| **bili** | Bilibili | search / detail / creator |
| **wb** | 微博 | search / detail / creator |
| **tieba** | 百度贴吧 | search / detail |
| **zhihu** | 知乎 | search / detail |

---

## 📝 命令行参数参考

```bash
# 完整参数列表
uv run python main.py [OPTIONS]

# 主要参数
--platform              平台选择 (默认: xhs)
--type                  爬虫类型: search/detail/creator (默认: search)
--keywords              搜索关键词，多个用逗号分隔 (默认: 编程副业,编程兼职)
--crawler_max_notes_count   最大爬虫数量 (默认: 15)
--start                 起始页码 (默认: 1)
--enable_get_meidas     下载图片视频 (默认: False)
--enable_get_comments   爬取评论 (默认: True)
--save_data_option      存储格式: json/jsonl/csv/db/sqlite/mysql/postgres/excel (默认: jsonl)

# 查看完整帮助
uv run python main.py --help
```

---

## 🔧 环境要求

- Python >= 3.11
- uv 包管理器（已安装）
- npm（用于 WebUI，可选）
- Chrome 或 Edge 浏览器（自动检测并使用）

---

## ⚡ 性能提示

### 爬虫性能优化
```bash
# 增加并发数量（提高速度）
# 在 config/base_config.py 中修改 MAX_CONCURRENCY_NUM

# 限制爬虫数量（快速测试）
run_quick.bat xhs 测试 1

# 大规模爬虫（需要更长时间）
run_quick.bat xhs 关键词 1000
```

### 媒体下载
```bash
# 不下载图片和视频（最快）
# 在 config/base_config.py 中修改 ENABLE_GET_MEIDAS = False

# 下载所有媒体（较慢）
# 在 config/base_config.py 中修改 ENABLE_GET_MEIDAS = True
```

---

## 🐛 故障排除

### 问题 1: 脚本无法运行
**解决方案：**
```bash
# 检查 uv 是否正确安装
uv --version

# 重新同步依赖
uv sync

# 手动运行
uv run python main.py --platform xhs --type search --keywords "测试" --crawler_max_notes_count 1
```

### 问题 2: 浏览器启动失败
**解决方案：**
- 确保系统已安装 Chrome 或 Edge 浏览器
- 检查浏览器是否为最新版本
- 在配置中指定自定义浏览器路径

### 问题 3: 中文显示乱码
**解决方案：**
- BAT 脚本已自动设置 UTF-8 编码 (chcp 65001)
- 确保使用 Windows PowerShell 而非 CMD

---

## 📊 数据保存位置

爬虫数据默认保存在项目根目录的 `data` 文件夹：

```
data/
├── xhs/              (小红书数据)
│   └── contents.jsonl
├── dy/               (抖音数据)
│   └── contents.jsonl
├── ks/               (快手数据)
│   └── contents.jsonl
└── ...
```

---

## 💡 进阶用法

### 并行运行多个爬虫
打开多个终端窗口，分别运行不同的爬虫任务：

```bash
# 终端 1
run_quick.bat xhs 编程 10

# 终端 2
run_quick.bat dy 编程 10

# 终端 3
run_quick.bat ks 编程 10
```

### 定时任务（Windows 任务计划程序）
1. 打开"任务计划程序"
2. 创建新任务
3. 操作中选择：运行程序
4. 程序：`cmd.exe`
5. 参数：`/c "%CD%\run_quick.bat xhs 编程 5"`
6. 设置触发条件（每天、每周等）

### 监控爬虫状态
查看实时日志输出，脚本会打印：
- 爬虫进度
- 数据保存位置
- 错误信息（如有）

---

## ❓ 常见问题

**Q: 爬虫速度很慢？**
A: 这是正常的，为了避免被平台检测，爬虫已配置合理的延迟。

**Q: 能否爬取所有数据？**
A: 受平台限制和网络限制，建议每次爬虫数量不超过 100 条。

**Q: 如何保存到数据库？**
A: 修改配置中的 `SAVE_DATA_OPTION = "sqlite"` 或其他数据库选项。

**Q: 数据在哪里保存？**
A: 默认在项目根目录的 `data` 文件夹中。

---

## 📞 帮助和反馈

有任何问题可以：
1. 查看项目 README
2. 检查配置文件注释
3. 运行 `uv run python main.py --help` 查看完整参数

---

**祝你使用愉快！** 🎉
