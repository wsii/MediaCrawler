@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ====================================
echo     MediaCrawler - 启动脚本 (uv版)
echo ====================================
echo.

REM 检查uv是否已安装
uv --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到uv环境
    echo 请先安装uv: https://docs.astral.sh/uv/getting-started/installation/
    echo.
    echo 快速安装命令:
    echo   powershell -ExecutionPolicy BypassUser -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

echo [✓] uv环境检测完成
echo.

REM 同步依赖并运行主程序
echo [同步依赖中...]
uv sync
if errorlevel 1 (
    echo [错误] 依赖同步失败
    pause
    exit /b 1
)

echo [✓] 依赖同步完成
echo.
echo ====================================
echo     启动MediaCrawler
echo ====================================
echo.

REM 运行主程序
uv run python main.py %*
pause
