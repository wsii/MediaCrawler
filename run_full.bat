@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           MediaCrawler - 完整启动 (WebUI + API)               ║
echo ╚════════════════════════════════════════════════════════════════╝
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

REM 启动 API 服务
echo [1/2] 启动 API 服务器 (http://localhost:8000/)
echo [等待] API 服务器启动中...
start "MediaCrawler API" uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

REM 等待 API 启动
timeout /t 4 /nobreak

REM 启动 WebUI 服务
echo.
echo [2/2] 启动 WebUI 开发服务器 (http://localhost:5173/)
echo [等待] WebUI 服务器启动中...
cd webui
start "MediaCrawler WebUI" npm run dev

REM 等待 WebUI 启动
timeout /t 3 /nobreak

REM 自动打开浏览器
echo.
echo ====================================
echo   ✓ 所有服务已启动！
echo ====================================
echo.
echo 访问地址：
echo   - WebUI 前端: http://localhost:5173/
echo   - API 后端: http://localhost:8000/
echo   - API 文档: http://localhost:8000/docs
echo.
echo 提示：
echo   - 按 Ctrl+C 可停止服务
echo   - 两个服务窗口均会在后台运行
echo   - 修改代码会自动热更新
echo.

echo [打开] 浏览器访问 WebUI...
start http://localhost:5173/

echo.
pause
