@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:main
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                 MediaCrawler - 主菜单                         ║
echo ║                                                                ║
echo ║    社交媒体爬虫框架 - 支持小红书、抖音、快手等多个平台      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo.
echo 【爬虫任务】
echo   1. 爬虫启动器      - 交互式菜单，多个平台选择
echo   2. 快速启动        - 一行命令启动爬虫 (默认参数)
echo.
echo 【开发工具】
echo   3. WebUI 前端      - 启动前端开发服务器 (http://localhost:5173)
echo   4. API 后端        - 启动 API 服务 (http://localhost:8000)
echo.
echo 【帮助与文档】
echo   5. 查看脚本说明    - 详细的运行指南和参数说明
echo   6. 打开项目文件夹  - 在资源管理器中打开
echo.
echo 【其他】
echo   7. 退出
echo.
echo.

set /p choice="请选择 (1-7): "

if "%choice%"=="1" (
    call run_crawler.bat
    goto main
)

if "%choice%"=="2" (
    call run_quick.bat
    goto main
)

if "%choice%"=="3" (
    call run_webui.bat
    goto main
)

if "%choice%"=="4" (
    call run_api.bat
    goto main
)

if "%choice%"=="5" (
    if exist RUN_SCRIPTS_GUIDE.md (
        start RUN_SCRIPTS_GUIDE.md
    ) else (
        echo [提示] 未找到 RUN_SCRIPTS_GUIDE.md
        pause
    )
    goto main
)

if "%choice%"=="6" (
    explorer .
    goto main
)

if "%choice%"=="7" (
    echo.
    echo 感谢使用 MediaCrawler！
    echo.
    exit /b 0
)

echo [错误] 无效的选择，请重试
timeout /t 2 >nul
goto main
