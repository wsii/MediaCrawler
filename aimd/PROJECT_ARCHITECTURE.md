# MediaCrawler 项目架构分析

## 📋 项目概述

**MediaCrawler** 是一个功能强大的多平台自媒体数据采集工具，采用模块化架构设计，支持7大主流平台的公开信息爬取。

- **项目名称**：MediaCrawler
- **核心技术**：Playwright（浏览器自动化）+ FastAPI（Web API）
- **开发语言**：Python 3.11+
- **主要特性**：
  - 基于登录态保持的浏览器自动化
  - 无需JS逆向，直接利用浏览器环境获取签名
  - 支持 CDP 模式（Chrome DevTools Protocol）
  - 多种数据存储方式（JSON、Excel、数据库）
  - 完整的代理池和反爬机制

---

## 🏗️ 整体架构设计

### 分层架构

```
┌─────────────────────────────────────────────┐
│          入口层 (main.py)                    │
│    CrawlerFactory - 爬虫工厂模式              │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│       业务逻辑层 (media_platform/)            │
│  ├─ XiaoHongShuCrawler (小红书)              │
│  ├─ DouYinCrawler (抖音)                     │
│  ├─ KuaishouCrawler (快手)                   │
│  ├─ BilibiliCrawler (B站)                    │
│  ├─ WeiboCrawler (微博)                      │
│  ├─ TieBaCrawler (贴吧)                      │
│  └─ ZhihuCrawler (知乎)                      │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│       基础层 (base/)                         │
│  ├─ AbstractCrawler (爬虫基类)               │
│  ├─ AbstractLogin (登录基类)                 │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│   基础设施层 (infrastructure)                 │
│  ├─ 配置系统 (config/)                       │
│  ├─ 数据存储 (store/, database/)             │
│  ├─ 缓存系统 (cache/)                        │
│  ├─ 代理管理 (proxy/)                        │
│  └─ 工具类 (tools/)                          │
└─────────────────────────────────────────────┘
```

---

## 📁 核心目录结构详解

### 1. **根目录层** - 入口点和配置

```
main.py                 # 主入口点，包含CrawlerFactory工厂类
var.py                  # 全局变量（如crawler_type_var）
requirements.txt        # 项目依赖
pyproject.toml         # UV包管理配置
```

**核心设计**：
- `CrawlerFactory` 使用**工厂模式**，支持7种爬虫的动态创建
- 平台标识映射：`{"xhs": XiaoHongShuCrawler, "dy": DouYinCrawler, ...}`

---

### 2. **config/** - 配置管理系统

```
config/
├── __init__.py          # 配置导入入口
├── base_config.py       # 基础配置（平台、关键词、代理等）
├── bilibili_config.py   # B站特定配置
├── dy_config.py         # 抖音特定配置
├── ks_config.py         # 快手特定配置
├── tieba_config.py      # 贴吧特定配置
├── weibo_config.py      # 微博特定配置
├── xhs_config.py        # 小红书特定配置
├── zhihu_config.py      # 知乎特定配置
└── db_config.py         # 数据库配置
```

**核心配置项**：
```python
PLATFORM               # 目标平台 (xhs|dy|ks|bili|wb|tieba|zhihu)
KEYWORDS              # 搜索关键词
LOGIN_TYPE            # 登录方式 (qrcode|phone|cookie)
CRAWLER_TYPE          # 爬取类型 (search|detail|creator)
ENABLE_IP_PROXY       # 是否启用IP代理
ENABLE_CDP_MODE       # 是否启用CDP模式
SAVE_DATA_OPTION      # 数据保存方式 (json|jsonl|excel|sqlite|mysql|db|postgres)
HEADLESS              # 是否无头浏览器
```

---

### 3. **base/** - 抽象基类和接口

```
base/
├── __init__.py
├── base_crawler.py      # 爬虫抽象基类
└── (隐含: AbstractLogin) # 登录抽象基类
```

**核心接口**：

```python
class AbstractCrawler(ABC):
    @abstractmethod
    async def start(self):              # 启动爬虫
        pass
    
    @abstractmethod
    async def search(self):             # 搜索功能
        pass
    
    @abstractmethod
    async def launch_browser(...):      # 启动浏览器
        pass
    
    async def launch_browser_with_cdp(...):  # CDP模式启动
        pass  # 默认实现

class AbstractLogin(ABC):
    @abstractmethod
    async def begin(self):              # 开始登录
        pass
    
    @abstractmethod
    async def login_by_qrcode(self):    # 二维码登录
        pass
    
    @abstractmethod
    async def login_by_mobile(self):    # 手机号登录
        pass
```

---

### 4. **media_platform/** - 平台爬虫实现

```
media_platform/
├── __init__.py
├── bilibili/              # B站爬虫
│   ├── client.py          # API客户端
│   ├── core.py            # 核心爬虫逻辑
│   ├── exception.py       # 异常定义
│   ├── help.py            # 辅助函数
│   ├── login.py           # 登录实现
│   ├── field.py           # 数据字段定义
│   └── __init__.py
├── douyin/                # 抖音爬虫（同上结构）
├── kuaishou/              # 快手爬虫（同上结构）
├── tieba/                 # 贴吧爬虫（同上结构）
├── weibo/                 # 微博爬虫（同上结构）
├── xhs/                   # 小红书爬虫（同上结构）
└── zhihu/                 # 知乎爬虫（同上结构）
```

**每个平台目录的标准结构**：

| 文件 | 功能 |
|------|------|
| `client.py` | HTTP客户端，处理API请求和签名 |
| `core.py` | 核心爬虫逻辑，实现搜索、获取详情等 |
| `login.py` | 登录实现，支持二维码/手机号登录 |
| `field.py` | 数据字段定义和映射 |
| `exception.py` | 平台特定异常类 |
| `help.py` | 辅助函数（数据解析、转换等） |

**平台爬虫的通用流程**：
```
启动 → 初始化浏览器 → 执行登录 → 根据crawler_type执行对应操作 → 数据存储 → 清理资源
```

---

### 5. **database/** - 数据库系统

```
database/
├── __init__.py
├── db.py                 # 数据库连接管理
├── db_session.py         # 数据库会话
├── models.py             # ORM模型定义（SQLAlchemy）
└── mongodb_store_base.py # MongoDB存储基类
```

**支持的数据库**：
- SQLite（轻量级）
- MySQL / AsyncMySQL
- PostgreSQL（asyncpg）
- MongoDB（Motor异步驱动）

---

### 6. **store/** - 数据存储层

```
store/
├── __init__.py
├── excel_store_base.py   # Excel存储基类
├── bilibili/
│   ├── bilibili_store.py
│   ├── bilibili_comment_store.py
│   ├── bilibili_creator_store.py
│   └── ...
├── douyin/
├── kuaishou/
├── tieba/
├── weibo/
├── xhs/
└── zhihu/
```

**存储策略**：
- **JSON/JSONL**：文件存储
- **Excel**：通过 `openpyxl` 生成电子表格
- **数据库**：结构化存储，支持关系型和文档型数据库

---

### 7. **cache/** - 缓存系统

```
cache/
├── __init__.py
├── abs_cache.py          # 缓存抽象基类
├── cache_factory.py      # 缓存工厂
├── local_cache.py        # 本地内存缓存
└── redis_cache.py        # Redis缓存
```

**用途**：
- 登录态缓存（保存浏览器状态）
- API响应缓存
- 请求结果缓存

---

### 8. **proxy/** - 代理管理系统

```
proxy/
├── __init__.py
├── base_proxy.py         # 代理基类
├── proxy_ip_pool.py      # 代理IP池管理
├── proxy_mixin.py        # 代理混入类
├── types.py              # 类型定义
└── providers/            # 代理提供商
    ├── kuaidaili.py      # 快代理
    ├── wandouhttp.py     # 豌豆HTTP
    └── static.py         # 静态代理
```

**代理特性**：
- 支持多个代理提供商
- 动态IP池管理
- 自动轮转代理
- 支持代理失效检测

---

### 9. **cmd_arg/** - 命令行参数解析

```
cmd_arg/
├── __init__.py
└── arg.py               # 命令行参数定义和解析
```

---

### 10. **model/** - 数据模型

```
model/
├── __init__.py
├── m_baidu_tieba.py    # 贴吧数据模型
├── m_bilibili.py        # B站数据模型
├── m_douyin.py          # 抖音数据模型
├── m_kuaishou.py        # 快手数据模型
├── m_weibo.py           # 微博数据模型
├── m_xiaohongshu.py     # 小红书数据模型
└── m_zhihu.py           # 知乎数据模型
```

**模型用途**：
- 定义各平台的数据结构
- 数据序列化/反序列化
- 与Pydantic集成进行数据验证

---

### 11. **tools/** - 工具函数库

```
tools/
├── __init__.py
├── app_runner.py        # 应用运行管理
├── async_file_writer.py # 异步文件写入
└── ...                  # 其他工具
```

**常用工具**：
- 文件IO操作
- 数据格式转换
- 词云生成

---

### 12. **api/** - FastAPI Web服务

```
api/
├── __init__.py
├── main.py              # FastAPI应用入口
├── routers/             # API路由
│   └── ...
└── schemas/             # Pydantic数据模型
```

**功能**：
- 提供HTTP API接口
- 查询已爬取的数据
- 管理爬虫任务

---

### 13. **tests/** 和 **test/** - 测试层

```
tests/                    # 单元测试
├── conftest.py
├── test_api_limits.py
├── test_bilibili_client_comments.py
├── test_cdp_browser.py
├── test_cmd_arg_tieba.py
└── ...

test/                     # 单元测试（另一个测试目录）
├── test_db_sync.py
├── test_expiring_local_cache.py
├── test_mongodb_integration.py
└── ...
```

---

## 🔄 核心流程设计

### 爬虫执行流程

```
┌─────────────────────────────────────────────────────────────┐
│ main.py: main()                                             │
│ ├─ 1. 解析命令行参数 (cmd_arg.parse_cmd)                   │
│ ├─ 2. 初始化数据库 (db.init_db)                            │
│ ├─ 3. 通过工厂创建爬虫 (CrawlerFactory.create_crawler)     │
│ └─ 4. 启动爬虫 (crawler.start)                             │
└──────────────────────────┬────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────┐
│ 具体平台爬虫 (e.g., DouYinCrawler).start()               │
│ ├─ 1. 初始化浏览器 (launch_browser / launch_browser_with_cdp)
│ ├─ 2. 执行登录 (Login.begin / login_by_qrcode)          │
│ ├─ 3. 根据CRAWLER_TYPE执行                              │
│ │   ├─ search: 关键词搜索                                │
│ │   ├─ detail: 指定帖子ID获取详情                        │
│ │   └─ creator: 创作者主页数据                           │
│ ├─ 4. 解析数据 (field.py中的字段映射)                   │
│ ├─ 5. 获取二级评论 (fetch_comments)                     │
│ └─ 6. 存储数据 (store/)                                 │
└──────────────────────────┬────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────┐
│ 数据存储                                              │
│ ├─ JSON/JSONL: AsyncFileWriter                      │
│ ├─ Excel: ExcelStoreBase.flush_all()                │
│ └─ Database: SQLAlchemy ORM                         │
└──────────────────────────┬────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────┐
│ 后处理                                                │
│ ├─ 生成评论词云 (generate_wordcloud_from_comments)  │
│ └─ 资源清理 (cleanup)                               │
└────────────────────────────────────────────────────┘
```

---

### 登录流程

```
┌───────────────────────────────────────────────┐
│ 登录入口: AbstractLogin.begin()              │
└──────────────┬────────────────────────────────┘
               │
        ┌──────▼──────┐
        │ LOGIN_TYPE? │
        └──────┬──────┘
        ┌──────┴────────────┬────────────┐
        │                   │            │
   ┌────▼────┐         ┌────▼────┐  ┌───▼───┐
   │ qrcode   │         │ phone    │  │ cookie │
   ├──────────┤         ├──────────┤  ├────────┤
   │ 生成二维码 │         │ 输入手机号 │  │ 使用已 │
   │ 扫码登录  │         │ 验证码登录 │  │ 保存的  │
   │ 保存状态  │         │ 保存状态  │  │ Cookie │
   └────┬────┘         └────┬────┘  └───┬────┘
        │                   │            │
        └───────────┬───────┴────────────┘
                    │
            ┌───────▼────────┐
            │ 登录成功        │
            │ 缓存登录态      │
            │ 返回到爬虫逻辑  │
            └────────────────┘
```

---

## 🎯 设计模式

### 1. **工厂模式** (Factory Pattern)
```python
class CrawlerFactory:
    CRAWLERS = {
        "xhs": XiaoHongShuCrawler,
        "dy": DouYinCrawler,
        ...
    }
    
    @staticmethod
    def create_crawler(platform: str) -> AbstractCrawler:
        return CrawlerFactory.CRAWLERS[platform]()
```

### 2. **抽象基类模式** (Abstract Base Class)
```python
class AbstractCrawler(ABC):
    @abstractmethod
    async def start(self): ...
    @abstractmethod
    async def search(self): ...
```

### 3. **混入模式** (Mixin)
```python
class ProxyMixin:  # 代理功能混入
    def get_proxy(self): ...
    def rotate_proxy(self): ...
```

### 4. **策略模式** (Strategy Pattern)
- 缓存策略：LocalCache vs RedisCache
- 数据存储策略：JSON vs Excel vs Database
- 代理提供商策略：KuaiDaiLi vs WanDouHttp vs Static

### 5. **单例模式** (Singleton)
- 数据库连接
- 缓存实例

---

## 🔐 关键技术特性

### 1. **异步编程** (Async/Await)
- 全面使用 `asyncio` 进行异步处理
- `motor` (MongoDB异步驱动)
- `aiomysql` / `asyncpg` (数据库异步驱动)

### 2. **Playwright浏览器自动化**
- 基于登录态的会话保持
- CDP模式支持（Chrome DevTools Protocol）
- 自动处理验证码和反爬

### 3. **数据验证和序列化**
- Pydantic模型进行强类型验证
- `pyhumps` 处理驼峰式命名转换
- FastAPI自动文档生成

### 4. **ORM框架**
- SQLAlchemy 2.0+ 支持异步
- Alembic 数据库版本控制
- 支持多种数据库后端

### 5. **代理和反爬机制**
- 动态代理池轮转
- User-Agent管理
- 请求频率控制（tenacity重试策略）

---

## 📊 数据流向

```
用户输入 (关键词、用户ID等)
    ↓
[命令行解析] (cmd_arg)
    ↓
[爬虫工厂] 创建平台爬虫
    ↓
[浏览器自动化] (Playwright)
    ├─ 登录（保存登录态）
    └─ 导航到目标页面
    ↓
[数据解析] (字段映射、XPath/CSS选择器)
    ↓
[数据验证] (Pydantic模型)
    ↓
[存储策略] 多种输出方式
    ├─ JSON/JSONL文件
    ├─ Excel电子表格
    └─ 数据库（SQLite/MySQL/PostgreSQL/MongoDB）
    ↓
[后处理] 词云生成、统计分析等
    ↓
[API接口] (FastAPI) 提供查询接口
```

---

## 🛠️ 项目配置系统

### 环境变量支持
- `.env` 文件加载（python-dotenv）
- `config/` 目录的配置覆盖

### 支持的爬虫类型
```
CRAWLER_TYPE 选项：
├─ search     : 关键词搜索
├─ detail     : 指定帖子ID获取详情 + 二级评论
└─ creator    : 创作者主页数据
```

### 数据保存方式
```
SAVE_DATA_OPTION 选项：
├─ json       : JSON文件（单文件）
├─ jsonl      : JSONL文件（行式JSON）
├─ excel      : Excel电子表格
├─ sqlite     : SQLite数据库
├─ mysql      : MySQL数据库
├─ db         : 同mysql
└─ postgres   : PostgreSQL数据库
```

---

## 📈 项目优势总结

| 方面 | 优势 |
|------|------|
| **架构** | 模块化设计，易于扩展新平台 |
| **技术** | 异步编程，高并发处理能力 |
| **反爬** | CDP模式，真实浏览器环境 |
| **灵活性** | 支持多种登录、存储、代理方案 |
| **可维护性** | 完整的错误处理、日志、类型提示 |
| **学习价值** | 展示企业级Python项目的最佳实践 |
| **测试** | 包含完整的单元测试套件 |
| **API** | FastAPI提供HTTP接口，便于集成 |

---

## 🚀 扩展性分析

### 添加新平台的步骤

```
1. 在 media_platform/ 创建新平台目录
   └─ 实现 client.py, core.py, login.py 等

2. 在 model/ 创建数据模型
   └─ 定义平台特定的数据结构

3. 在 config/ 创建平台配置
   └─ 定义平台特定的参数

4. 在 store/ 创建存储实现
   └─ 处理数据持久化

5. 在 CrawlerFactory 中注册新爬虫
   └─ CRAWLERS["new_platform"] = NewCrawler

6. 在 cmd_arg 中添加新平台支持
   └─ 更新参数验证

7. 添加测试用例
   └─ tests/test_new_platform.py
```

---

## 📝 总结

MediaCrawler 是一个**设计精良的企业级爬虫框架**，采用：
- ✅ 清晰的分层架构
- ✅ 完善的设计模式
- ✅ 强大的异步能力
- ✅ 灵活的配置系统
- ✅ 多样化的数据存储方案
- ✅ 健全的测试框架

这样的项目非常**适合学习现代Python应用的架构设计和最佳实践**。
