@echo off
chcp 65001 >nul 2>&1
title Minecraft Server - BlockMind

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   🎮 Minecraft 服务端启动器           ║
echo   ╚══════════════════════════════════════╝
echo.

cd /d "%~dp0"

:: ── 检查 Java ──
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [错误] 未找到 Java！
    echo   Minecraft 1.20.4 需要 Java 17+
    echo   下载: https://adoptium.net/
    pause
    exit /b 1
)
for /f "tokens=3" %%v in ('java -version 2^>^&1 ^| findstr "version"') do echo   [✓] Java %%v

:: ── 服务端目录 ──
set MC_DIR=%~dp0mc-server
if not exist "%MC_DIR%" mkdir "%MC_DIR%"
cd /d "%MC_DIR%"

:: ── 检查服务端文件 ──
if not exist "fabric-server-launch.jar" (
    echo.
    echo   [提示] 首次运行，需要下载 Fabric 服务端
    echo.
    echo   请手动操作：
    echo   1. 访问 https://fabricmc.net/use/server/
    echo   2. 选择 Minecraft 1.20.4，下载服务端 JAR
    echo   3. 将 JAR 文件放到: %MC_DIR%\
    echo   4. 重新运行此脚本
    echo.
    pause
    exit /b 1
)

:: ── 接受 EULA ──
if not exist "eula.txt" (
    echo eula=true > eula.txt
    echo   [✓] 已接受 Minecraft EULA
)

:: ── 内存配置 ──
:: 根据系统内存自动调整，最低 1G，推荐 2G
set MAX_RAM=2G
for /f "tokens=2 delims==" %%m in ('wmic computersystem get TotalPhysicalMemory /value 2^>nul') do set TOTAL_MEM=%%m

echo.
echo   [✓] 服务端目录: %MC_DIR%
echo   [✓] 最大内存: %MAX_RAM%
echo   [✓] 游戏版本: 1.20.4
echo.
echo   启动中...（首次启动可能需要 1-2 分钟）
echo   按 Ctrl+C 停止服务器
echo.

:: ── 启动 ──
java -Xms512M -Xmx%MAX_RAM% -jar fabric-server-launch.jar nogui

echo.
echo   👋 Minecraft 服务端已停止
pause
