@echo off
chcp 65001 >nul 2>&1
title Minecraft Server - BlockMind

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   🎮 Minecraft 服务端自动安装+启动     ║
echo   ╚══════════════════════════════════════╝
echo.

cd /d "%~dp0"

:: ── 配置 ──
set MC_VERSION=1.20.4
set FABRIC_VERSION=0.15.3
set MC_DIR=%~dp0mc-server
set INSTALLER_JAR=fabric-installer.jar
set INSTALLER_URL=https://maven.fabricmc.net/net/fabricmc/fabric-installer/%FABRIC_VERSION%/fabric-installer-%FABRIC_VERSION%.jar

:: ── 检查 Java ──
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [✗] 未找到 Java！
    echo.
    echo   Minecraft %MC_VERSION% 需要 Java 17+
    echo   下载地址: https://adoptium.net/
    echo.
    pause
    exit /b 1
)
for /f "tokens=3" %%v in ('java -version 2^>^&1 ^| findstr "version"') do (
    echo   [✓] Java %%v
)

:: ── 创建目录 ──
if not exist "%MC_DIR%" (
    mkdir "%MC_DIR%"
    echo   [✓] 创建目录: %MC_DIR%
)

:: ══════════════════════════════════════
:: 第一步：下载 Fabric 安装器
:: ══════════════════════════════════════
if not exist "%MC_DIR%\%INSTALLER_JAR%" (
    echo.
    echo   [1/4] 下载 Fabric 安装器...
    echo   URL: %INSTALLER_URL%

    :: 优先用 curl（Win10+自带），否则用 PowerShell
    curl --version >nul 2>&1
    if %errorlevel% equ 0 (
        curl -L -o "%MC_DIR%\%INSTALLER_JAR%" "%INSTALLER_URL%"
    ) else (
        powershell -Command "Invoke-WebRequest -Uri '%INSTALLER_URL%' -OutFile '%MC_DIR%\%INSTALLER_JAR%'"
    )

    if not exist "%MC_DIR%\%INSTALLER_JAR%" (
        echo   [✗] 下载失败！请手动下载:
        echo   %INSTALLER_URL%
        pause
        exit /b 1
    )
    echo   [✓] Fabric 安装器已下载
) else (
    echo   [✓] Fabric 安装器已存在
)

:: ══════════════════════════════════════
:: 第二步：安装 Fabric 服务端
:: ══════════════════════════════════════
if not exist "%MC_DIR%\fabric-server-launch.jar" (
    echo.
    echo   [2/4] 安装 Fabric 服务端 (MC %MC_VERSION%)...
    java -jar "%MC_DIR%\%INSTALLER_JAR%" server -dir "%MC_DIR%" -mcversion %MC_VERSION% -loader %FABRIC_VERSION% -downloadMinecraft

    if not exist "%MC_DIR%\fabric-server-launch.jar" (
        echo   [✗] 安装失败！请检查网络连接
        pause
        exit /b 1
    )
    echo   [✓] Fabric 服务端安装完成
) else (
    echo   [✓] Fabric 服务端已存在
)

:: ══════════════════════════════════════
:: 第三步：下载 BlockMind Mod
:: ══════════════════════════════════════
set MODS_DIR=%MC_DIR%\mods
if not exist "%MODS_DIR%" mkdir "%MODS_DIR%"

:: 检查是否已有 Mod
dir /b "%MODS_DIR%\blockmind-mod-*.jar" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo   [3/4] 下载 BlockMind Mod...

    :: 从 GitHub Releases 获取最新下载链接
    set RELEASE_URL=https://api.github.com/repos/bmbxwbh/BlockMind/releases/latest

    curl --version >nul 2>&1
    if %errorlevel% equ 0 (
        :: 用 curl 获取最新 release 的 asset URL
        curl -sL "%RELEASE_URL%" | findstr "browser_download_url" | findstr "blockmind-mod" > "%TEMP%\bm_url.txt"
        for /f "tokens=2 delims=\"" %%u in ('type "%TEMP%\bm_url.txt"') do (
            echo   下载: %%u
            curl -L -o "%MODS_DIR%\blockmind-mod.jar" "%%u"
        )
        del "%TEMP%\bm_url.txt" >nul 2>&1
    ) else (
        :: PowerShell 方式
        powershell -Command ^
            "$r = Invoke-RestMethod -Uri '%RELEASE_URL%'; " ^
            "$asset = $r.assets | Where-Object { $_.name -like 'blockmind-mod*' } | Select-Object -First 1; " ^
            "if ($asset) { Invoke-WebRequest -Uri $asset.browser_download_url -OutFile '%MODS_DIR%\blockmind-mod.jar' }"
    )

    if exist "%MODS_DIR%\blockmind-mod.jar" (
        echo   [✓] BlockMind Mod 已下载
    ) else (
        echo   [!] Mod 下载失败（可选，不影响启动）
        echo   [!] 手动下载: https://github.com/bmbxwbh/BlockMind/releases
    )
) else (
    echo   [✓] BlockMind Mod 已存在
)

:: ══════════════════════════════════════
:: 第四步：接受 EULA + 启动
:: ══════════════════════════════════════
echo.
echo   [4/4] 准备启动...

:: 接受 EULA
if not exist "%MC_DIR%\eula.txt" (
    echo eula=true > "%MC_DIR%\eula.txt"
    echo   [✓] 已接受 Minecraft EULA
)

:: 内存配置（自动检测系统内存）
set MAX_RAM=2G
for /f "tokens=2 delims==" %%m in ('wmic computersystem get TotalPhysicalMemory /value 2^>nul') do set TOTAL_MEM_BYTES=%%m
:: 简单判断：大于 8GB 用 4G，否则用 2G
if defined TOTAL_MEM_BYTES (
    if %TOTAL_MEM_BYTES% GTR 8000000000 set MAX_RAM=4G
)

cd /d "%MC_DIR%"

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   🎮 启动 Minecraft 服务端             ║
echo   ╠══════════════════════════════════════╣
echo   ║   版本: MC %MC_VERSION% + Fabric %FABRIC_VERSION%
echo   ║   内存: %MAX_RAM%
echo   ║   目录: %MC_DIR%
echo   ╚══════════════════════════════════════╝
echo.
echo   启动中...（首次约 1-2 分钟）
echo   按 Ctrl+C 停止服务器
echo.

java -Xms512M -Xmx%MAX_RAM% -jar fabric-server-launch.jar nogui

echo.
echo   👋 Minecraft 服务端已停止
pause
