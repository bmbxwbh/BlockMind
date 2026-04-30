@echo off
chcp 65001 >nul 2>&1
title Minecraft Server - BlockMind

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   🎮 Minecraft 服务端安装+启动         ║
echo   ╚══════════════════════════════════════╝
echo.

cd /d "%~dp0"

set DEFAULT_MC_VERSION=1.20.4
set FABRIC_VERSION=0.15.3

:: ── 检查 Java ──
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [✗] 未找到 Java 17+！
    echo   下载: https://adoptium.net/
    pause
    exit /b 1
)
for /f "tokens=3" %%v in ('java -version 2^>^&1 ^| findstr "version"') do echo   [✓] Java %%v

:: ══════════════════════════════════════
:: 第一步：检测已有服务端
:: ══════════════════════════════════════
echo.
echo   扫描已有服务端...

set DETECTED=0
set DETECTED_1=
set DETECTED_2=
set DETECTED_3=
set DETECTED_4=
set DETECTED_5=

if exist "%~dp0mc-server\fabric-server-launch.jar" (
    set /a DETECTED+=1
    set DETECTED_1=%~dp0mc-server
    echo     ✓ %~dp0mc-server (Fabric)
)
if exist "%~dp0mc-server\server.jar" (
    set /a DETECTED+=1
    set DETECTED_1=%~dp0mc-server
    echo     ✓ %~dp0mc-server (Vanilla)
)
if exist "%~dp0server\fabric-server-launch.jar" (
    set /a DETECTED+=1
    set DETECTED_2=%~dp0server
    echo     ✓ %~dp0server (Fabric)
)
if exist "%~dp0minecraft-server\fabric-server-launch.jar" (
    set /a DETECTED+=1
    set DETECTED_3=%~dp0minecraft-server
    echo     ✓ %~dp0minecraft-server (Fabric)
)

:: 检查端口 25565
netstat -ano | findstr ":25565 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo   [!] 端口 25565 已被占用（可能有其他 MC 服务端在运行）
    set /p yn="  继续启动？[y/N]: "
    if /i not "%yn%"=="y" exit /b 0
)

echo.

:: ══════════════════════════════════════
:: 第二步：选择服务端
:: ══════════════════════════════════════
set MC_DIR=
set USE_EXISTING=0

if %DETECTED% GTR 0 (
    echo   检测到已有服务端：
    echo.
    if defined DETECTED_1 echo     1^) %DETECTED_1%
    if defined DETECTED_2 echo     2^) %DETECTED_2%
    if defined DETECTED_3 echo     3^) %DETECTED_3%
    echo     0^) 安装新的服务端
    echo.
    set /p choice="  选择 [0-%DETECTED%]: "

    if "%choice%"=="1" if defined DETECTED_1 (set MC_DIR=%DETECTED_1%& set USE_EXISTING=1)
    if "%choice%"=="2" if defined DETECTED_2 (set MC_DIR=%DETECTED_2%& set USE_EXISTING=1)
    if "%choice%"=="3" if defined DETECTED_3 (set MC_DIR=%DETECTED_3%& set USE_EXISTING=1)

    if %USE_EXISTING%==1 echo   [✓] 使用已有服务端: %MC_DIR%
)

:: ══════════════════════════════════════
:: 第三步：选择版本（仅新安装）
:: ══════════════════════════════════════
set MC_VERSION=%DEFAULT_MC_VERSION%

if %USE_EXISTING%==0 (
    echo.
    echo   可选版本：
    echo     1^) 1.21.4  (最新)
    echo     2^) 1.21.3
    echo     3^) 1.21.1
    echo     4^) 1.20.6
    echo     5^) 1.20.4  (推荐)
    echo     6^) 1.20.1
    echo     7^) 1.19.4
    echo     8^) 自定义版本号
    echo.
    set /p ver_choice="  选择 [1-8] (默认5): "

    if "%ver_choice%"=="1" set MC_VERSION=1.21.4
    if "%ver_choice%"=="2" set MC_VERSION=1.21.3
    if "%ver_choice%"=="3" set MC_VERSION=1.21.1
    if "%ver_choice%"=="4" set MC_VERSION=1.20.6
    if "%ver_choice%"=="5" set MC_VERSION=1.20.4
    if "%ver_choice%"=="6" set MC_VERSION=1.20.1
    if "%ver_choice%"=="7" set MC_VERSION=1.19.4
    if "%ver_choice%"=="8" (
        set /p MC_VERSION="  输入版本号 (如 1.20.4): "
    )
    if "%ver_choice%"=="" set MC_VERSION=1.20.4

    echo.
    echo   [✓] 选择版本: MC %MC_VERSION%

    :: 安装目录
    set MC_DIR=%~dp0mc-server
    set /p custom_dir="  安装目录 (默认: %MC_DIR%): "
    if defined custom_dir set MC_DIR=%custom_dir%

    if not exist "%MC_DIR%" mkdir "%MC_DIR%"
)

:: ══════════════════════════════════════
:: 第四步：下载+安装（仅新安装）
:: ══════════════════════════════════════
if %USE_EXISTING%==0 (
    :: 下载 Fabric 安装器
    if not exist "%MC_DIR%\fabric-installer.jar" (
        echo.
        echo   [1/2] 下载 Fabric 安装器...
        set INSTALLER_URL=https://maven.fabricmc.net/net/fabricmc/fabric-installer/%FABRIC_VERSION%/fabric-installer-%FABRIC_VERSION%.jar
        curl --version >nul 2>&1
        if %errorlevel% equ 0 (
            curl -L -o "%MC_DIR%\fabric-installer.jar" "!INSTALLER_URL!"
        ) else (
            powershell -Command "Invoke-WebRequest -Uri '%INSTALLER_URL%' -OutFile '%MC_DIR%\fabric-installer.jar'"
        )
        echo   [✓] 下载完成
    )

    :: 安装 Fabric 服务端
    if not exist "%MC_DIR%\fabric-server-launch.jar" (
        echo.
        echo   [2/2] 安装 Fabric 服务端 (MC %MC_VERSION%)...
        java -jar "%MC_DIR%\fabric-installer.jar" server -dir "%MC_DIR%" -mcversion %MC_VERSION% -loader %FABRIC_VERSION% -downloadMinecraft
        echo   [✓] 安装完成
    )
)

:: ══════════════════════════════════════
:: 第五步：下载 BlockMind Mod
:: ══════════════════════════════════════
set MODS_DIR=%MC_DIR%\mods
if not exist "%MODS_DIR%" mkdir "%MODS_DIR%"

dir /b "%MODS_DIR%\blockmind-mod-*.jar" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo   下载 BlockMind Mod...
    curl --version >nul 2>&1
    if %errorlevel% equ 0 (
        curl -sL "https://api.github.com/repos/bmbxwbh/BlockMind/releases/latest" | findstr "browser_download_url" | findstr "blockmind-mod" > "%TEMP%\bm_url.txt"
        for /f "tokens=2 delims=\"" %%u in ('type "%TEMP%\bm_url.txt"') do (
            curl -L -o "%MODS_DIR%\blockmind-mod.jar" "%%u"
        )
        del "%TEMP%\bm_url.txt" >nul 2>&1
    ) else (
        powershell -Command "$r=Invoke-RestMethod -Uri 'https://api.github.com/repos/bmbxwbh/BlockMind/releases/latest'; $a=$r.assets|Where-Object{$_.name -like 'blockmind-mod*'}|Select -First 1; if($a){Invoke-WebRequest -Uri $a.browser_download_url -OutFile '%MODS_DIR%\blockmind-mod.jar'}"
    )
    if exist "%MODS_DIR%\blockmind-mod.jar" (
        echo   [✓] Mod 已下载
    ) else (
        echo   [!] Mod 下载失败（可选）
    )
) else (
    echo   [✓] BlockMind Mod 已存在
)

:: ══════════════════════════════════════
:: 第六步：启动
:: ══════════════════════════════════════
if not exist "%MC_DIR%\eula.txt" echo eula=true > "%MC_DIR%\eula.txt"

:: 内存配置
set MAX_RAM=2G
for /f "tokens=2 delims==" %%m in ('wmic computersystem get TotalPhysicalMemory /value 2^>nul') do set TOTAL_MEM=%%m
if defined TOTAL_MEM if %TOTAL_MEM% GTR 8000000000 set MAX_RAM=4G

:: 确定启动 JAR
set LAUNCH_JAR=
if exist "%MC_DIR%\fabric-server-launch.jar" set LAUNCH_JAR=fabric-server-launch.jar
if exist "%MC_DIR%\server.jar" if not defined LAUNCH_JAR set LAUNCH_JAR=server.jar
if not defined LAUNCH_JAR (
    echo   [✗] 未找到可启动的 JAR 文件
    pause
    exit /b 1
)

cd /d "%MC_DIR%"

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   🎮 启动 Minecraft 服务端             ║
echo   ╠══════════════════════════════════════╣
echo   ║   目录: %MC_DIR%
echo   ║   JAR:  %LAUNCH_JAR%
echo   ║   内存: %MAX_RAM%
echo   ╚══════════════════════════════════════╝
echo.
echo   按 Ctrl+C 停止
echo.

java -Xms512M -Xmx%MAX_RAM% -jar %LAUNCH_JAR% nogui

echo.
echo   👋 服务端已停止
pause
