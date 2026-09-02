@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ====================================
echo     MediaCrawler - 爬虫启动脚本
echo ====================================
echo.

REM 检查uv是否已安装
uv --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到uv环境
    echo 请先安装uv: https://docs.astral.sh/uv/getting-started/installation/
    echo.
    pause
    exit /b 1
)

echo [✓] uv 环境检测完成
echo.

REM 显示菜单
echo ====================================
echo     选择运行模式
echo ====================================
echo.
echo 1. 小红书搜索爬虫 (默认参数)
echo 2. 抖音搜索爬虫
echo 3. 快手搜索爬虫
echo 4. Bilibili 搜索爬虫
echo 5. 微博搜索爬虫
echo 6. 自定义参数运行
echo 7. 退出
echo.

set /p choice="请选择 (1-7): "

if "%choice%"=="1" (
    echo [启动] 小红书搜索爬虫...
    echo.
    uv run python main.py --platform xhs --type search --keywords "编程副业" --crawler_max_notes_count 5
    goto end
)

if "%choice%"=="2" (
    echo [启动] 抖音搜索爬虫...
    echo.
    uv run python main.py --platform dy --type search --keywords "编程副业" --crawler_max_notes_count 5
    goto end
)

if "%choice%"=="3" (
    echo [启动] 快手搜索爬虫...
    echo.
    uv run python main.py --platform ks --type search --keywords "编程副业" --crawler_max_notes_count 5
    goto end
)

if "%choice%"=="4" (
    echo [启动] Bilibili 搜索爬虫...
    echo.
    uv run python main.py --platform bili --type search --keywords "编程副业" --crawler_max_notes_count 5
    goto end
)

if "%choice%"=="5" (
    echo [启动] 微博搜索爬虫...
    echo.
    uv run python main.py --platform wb --type search --keywords "编程副业" --crawler_max_notes_count 5
    goto end
)

if "%choice%"=="6" (
    echo.
    set /p platform="输入平台 (xhs/dy/ks/bili/wb/tieba/zhihu) [默认: xhs]: "
    if "!platform!"=="" set platform=xhs
    
    set /p type="输入爬虫类型 (search/detail/creator) [默认: search]: "
    if "!type!"=="" set type=search
    
    set /p keywords="输入关键词 [默认: 编程副业]: "
    if "!keywords!"=="" set keywords=编程副业
    
    set /p max_notes="输入最大爬虫数量 [默认: 5]: "
    if "!max_notes!"=="" set max_notes=5
    
    echo.
    echo [启动] 自定义爬虫任务...
    echo 平台: !platform! | 类型: !type! | 关键词: !keywords! | 数量: !max_notes!
    echo.
    
    uv run python main.py --platform !platform! --type !type! --keywords "!keywords!" --crawler_max_notes_count !max_notes!
    goto end
)

if "%choice%"=="7" (
    echo 退出程序
    goto end
)

echo [错误] 无效的选择
goto end

:end
echo.
echo ====================================
pause
