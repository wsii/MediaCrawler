@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ====================================
echo     MediaCrawler - WebUI 启动
echo ====================================
echo.

REM 检查uv是否已安装
uv --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到uv环境
    echo 请先安装uv: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

echo [✓] uv 环境检测完成
echo.

REM 进入 webui 目录并启动开发服务器
echo [启动] WebUI 开发服务器 (http://localhost:5173/)
echo.
echo 提示: 按 Ctrl+C 停止服务器
echo.

cd webui

REM 在后台启动开发服务器
start "MediaCrawler WebUI" npm run dev

REM 等待服务器启动
echo [等待] 服务器启动中...
timeout /t 3 /nobreak

REM 自动打开浏览器
echo [打开] 浏览器访问 http://localhost:5173/
start http://localhost:5173/

REM 保持窗口打开
pause
