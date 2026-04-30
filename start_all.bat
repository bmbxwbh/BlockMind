@echo off
chcp 65001 >nul 2>&1
title BlockMind - 全部启动

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   🧠 BlockMind 一键启动               ║
echo   ╚══════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo   [1/2] 启动 Minecraft 服务端...
echo   (将在新窗口中打开)
echo.

:: 在新窗口启动 MC 服务端
if exist "mc-server\fabric-server-launch.jar" (
    start "Minecraft Server" cmd /c "cd /d "%~dp0" && call start_mc.bat"
    echo   [✓] MC 服务端窗口已打开
) else (
    echo   [!] 未找到 mc-server\fabric-server-launch.jar
    echo   [!] 请先运行 start_mc.bat 下载服务端
)

:: 等待几秒让 MC 服务端启动
echo.
echo   等待 5 秒让 MC 服务端初始化...
timeout /t 5 /nobreak >nul

echo.
echo   [2/2] 启动 BlockMind 后端...
echo.

:: 在当前窗口运行 BlockMind
python -m src.main

echo.
echo   👋 BlockMind 已退出
echo   (MC 服务端可能仍在另一个窗口运行)
pause
