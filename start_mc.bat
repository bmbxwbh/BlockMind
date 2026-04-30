@echo off
chcp 65001 >nul 2>&1

:: ── Language Selection ──
echo.
echo   Select language / 选择语言
echo.
echo     1^) 中文
echo     2^) English
echo.
set /p BM_LANG="  [1/2]: "
if "%BM_LANG%"=="2" goto :lang_en
if "%BM_LANG%"=="en" goto :lang_en
if "%BM_LANG%"=="EN" goto :lang_en
goto :lang_zh

:lang_zh
set "T_TITLE=🎮 Minecraft 服务端安装+启动"
set "T_NO_JAVA=[✗] 未找到 Java 17+！"
set "T_DL_JAVA=下载: https://adoptium.net/"
set "T_SCAN=扫描已有服务端..."
set "T_FABRIC=Fabric"
set "T_VANILLA=Vanilla"
set "T_PORT_WARN=[!] 端口 25565 已被占用（可能有其他 MC 服务端在运行）"
set "T_CONTINUE=继续启动？[y/N]"
set "T_DETECT=检测到已有服务端："
set "T_INSTALL_NEW=安装新的服务端"
set "T_CHOOSE=选择"
set "T_VERSIONS=可选版本："
set "T_VER_LATEST=最新"
set "T_VER_RECOMMEND=推荐"
set "T_VER_CUSTOM=自定义版本号"
set "T_CHOSEN_VER=[✓] 选择版本"
set "T_DL_INSTALLER=[1/2] 下载 Fabric 安装器..."
set "T_DL_DONE=[✓] 下载完成"
set "T_INSTALL_FABRIC=[2/2] 安装 Fabric 服务端"
set "T_INSTALL_DONE=[✓] 安装完成"
set "T_DL_MOD=下载 BlockMind Mod..."
set "T_MOD_DONE=[✓] Mod 已下载"
set "T_MOD_FAIL=[!] Mod 下载失败（可选）"
set "T_MOD_EXIST=[✓] BlockMind Mod 已存在"
set "T_LAUNCH_TITLE=🎮 启动 Minecraft 服务端"
set "T_DIR=目录"
set "T_JAR=JAR"
set "T_MEMORY=内存"
set "T_PRESS_STOP=按 Ctrl+C 停止"
set "T_STOPPED=👋 服务端已停止"
set "T_NO_JAR=[✗] 未找到可启动的 JAR 文件"
goto :start_init

:lang_en
set "T_TITLE=🎮 Minecraft Server Install + Start"
set "T_NO_JAVA=[✗] Java 17+ not found!"
set "T_DL_JAVA=Download: https://adoptium.net/"
set "T_SCAN=Scanning existing servers..."
set "T_FABRIC=Fabric"
set "T_VANILLA=Vanilla"
set "T_PORT_WARN=[!] Port 25565 already in use (another MC server may be running)"
set "T_CONTINUE=Continue? [y/N]"
set "T_DETECT=Detected existing servers:"
set "T_INSTALL_NEW=Install new server"
set "T_CHOOSE=Choose"
set "T_VERSIONS=Available versions:"
set "T_VER_LATEST=latest"
set "T_VER_RECOMMEND=recommended"
set "T_VER_CUSTOM=Custom version"
set "T_CHOSEN_VER=[✓] Selected version"
set "T_DL_INSTALLER=[1/2] Downloading Fabric installer..."
set "T_DL_DONE=[✓] Download complete"
set "T_INSTALL_FABRIC=[2/2] Installing Fabric server"
set "T_INSTALL_DONE=[✓] Installation complete"
set "T_DL_MOD=Downloading BlockMind Mod..."
set "T_MOD_DONE=[✓] Mod downloaded"
set "T_MOD_FAIL=[!] Mod download failed (optional)"
set "T_MOD_EXIST=[✓] BlockMind Mod already exists"
set "T_LAUNCH_TITLE=🎮 Starting Minecraft Server"
set "T_DIR=Directory"
set "T_JAR=JAR"
set "T_MEMORY=Memory"
set "T_PRESS_STOP=Press Ctrl+C to stop"
set "T_STOPPED=👋 Server stopped"
set "T_NO_JAR=[✗] No launchable JAR found"
goto :start_init

:start_init
title %T_TITLE%
cd /d "%~dp0"

set DEFAULT_MC_VERSION=1.20.4
set FABRIC_VERSION=0.15.3

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   %T_TITLE%
echo   ╚══════════════════════════════════════╝
echo.

:: ── 检查 Java ──
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo   %T_NO_JAVA%
    echo   %T_DL_JAVA%
    pause
    exit /b 1
)
for /f "tokens=3" %%v in ('java -version 2^>^&1 ^| findstr "version"') do echo   [✓] Java %%v

:: ══════════════════════════════════════
:: 第一步：检测已有服务端
:: ══════════════════════════════════════
echo.
echo   %T_SCAN%

set DETECTED=0
set DETECTED_1=
set DETECTED_2=
set DETECTED_3=
set DETECTED_4=
set DETECTED_5=

if exist "%~dp0mc-server\fabric-server-launch.jar" (
    set /a DETECTED+=1
    set DETECTED_1=%~dp0mc-server
    echo     ✓ %~dp0mc-server (%T_FABRIC%)
)
if exist "%~dp0mc-server\server.jar" (
    set /a DETECTED+=1
    set DETECTED_1=%~dp0mc-server
    echo     ✓ %~dp0mc-server (%T_VANILLA%)
)
if exist "%~dp0server\fabric-server-launch.jar" (
    set /a DETECTED+=1
    set DETECTED_2=%~dp0server
    echo     ✓ %~dp0server (%T_FABRIC%)
)
if exist "%~dp0minecraft-server\fabric-server-launch.jar" (
    set /a DETECTED+=1
    set DETECTED_3=%~dp0minecraft-server
    echo     ✓ %~dp0minecraft-server (%T_FABRIC%)
)

:: 检查端口 25565
netstat -ano | findstr ":25565 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo   %T_PORT_WARN%
    set /p yn="  %T_CONTINUE% "
    if /i not "%yn%"=="y" exit /b 0
)

echo.

:: ══════════════════════════════════════
:: 第二步：选择服务端
:: ══════════════════════════════════════
set MC_DIR=
set USE_EXISTING=0

if %DETECTED% GTR 0 (
    echo   %T_DETECT%
    echo.
    if defined DETECTED_1 echo     1^) %DETECTED_1%
    if defined DETECTED_2 echo     2^) %DETECTED_2%
    if defined DETECTED_3 echo     3^) %DETECTED_3%
    echo     0^) %T_INSTALL_NEW%
    echo.
    set /p choice="  %T_CHOOSE% [0-%DETECTED%]: "

    if "%choice%"=="1" if defined DETECTED_1 (set MC_DIR=%DETECTED_1%& set USE_EXISTING=1)
    if "%choice%"=="2" if defined DETECTED_2 (set MC_DIR=%DETECTED_2%& set USE_EXISTING=1)
    if "%choice%"=="3" if defined DETECTED_3 (set MC_DIR=%DETECTED_3%& set USE_EXISTING=1)

    if %USE_EXISTING%==1 echo   [✓] %T_USE_EXISTING%: %MC_DIR%
)

:: ══════════════════════════════════════
:: 第三步：选择版本（仅新安装）
:: ══════════════════════════════════════
set MC_VERSION=%DEFAULT_MC_VERSION%

if %USE_EXISTING%==0 (
    echo.
    echo   %T_VERSIONS%
    echo     1^) 1.21.4  (%T_VER_LATEST%)
    echo     2^) 1.21.3
    echo     3^) 1.21.1
    echo     4^) 1.20.6
    echo     5^) 1.20.4  (%T_VER_RECOMMEND%)
    echo     6^) 1.20.1
    echo     7^) 1.19.4
    echo     8^) %T_VER_CUSTOM%
    echo.
    set /p ver_choice="  %T_CHOOSE% [1-8] (默认5): "

    if "%ver_choice%"=="1" set MC_VERSION=1.21.4
    if "%ver_choice%"=="2" set MC_VERSION=1.21.3
    if "%ver_choice%"=="3" set MC_VERSION=1.21.1
    if "%ver_choice%"=="4" set MC_VERSION=1.20.6
    if "%ver_choice%"=="5" set MC_VERSION=1.20.4
    if "%ver_choice%"=="6" set MC_VERSION=1.20.1
    if "%ver_choice%"=="7" set MC_VERSION=1.19.4
    if "%ver_choice%"=="8" (
        set /p MC_VERSION="  %T_VER_CUSTOM% (e.g. 1.20.4): "
    )
    if "%ver_choice%"=="" set MC_VERSION=1.20.4

    echo.
    echo   %T_CHOSEN_VER%: MC %MC_VERSION%

    :: 安装目录
    set MC_DIR=%~dp0mc-server
    set /p custom_dir="  %T_DIR% (默认: %MC_DIR%): "
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
        echo   %T_DL_INSTALLER%
        set INSTALLER_URL=https://maven.fabricmc.net/net/fabricmc/fabric-installer/%FABRIC_VERSION%/fabric-installer-%FABRIC_VERSION%.jar
        curl --version >nul 2>&1
        if %errorlevel% equ 0 (
            curl -L -o "%MC_DIR%\fabric-installer.jar" "!INSTALLER_URL!"
        ) else (
            powershell -Command "Invoke-WebRequest -Uri '%INSTALLER_URL%' -OutFile '%MC_DIR%\fabric-installer.jar'"
        )
        echo   %T_DL_DONE%
    )

    :: 安装 Fabric 服务端
    if not exist "%MC_DIR%\fabric-server-launch.jar" (
        echo.
        echo   %T_INSTALL_FABRIC% (MC %MC_VERSION%)...
        java -jar "%MC_DIR%\fabric-installer.jar" server -dir "%MC_DIR%" -mcversion %MC_VERSION% -loader %FABRIC_VERSION% -downloadMinecraft
        echo   %T_INSTALL_DONE%
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
    echo   %T_DL_MOD%
    curl --version >nul 2>&1
    if %errorlevel% equ 0 (
        curl -sL "https://api.github.com/repos/bmbxwbh/BlockMind/releases/latest" | findstr "browser_download_url" | findstr "blockmind-mod" > "%TEMP%\bm_url.txt"
        for /f "tokens=2 delims=\"%%u" in ('type "%TEMP%\bm_url.txt"') do (
            curl -L -o "%MODS_DIR%\blockmind-mod.jar" "%%u"
        )
        del "%TEMP%\bm_url.txt" >nul 2>&1
    ) else (
        powershell -Command "$r=Invoke-RestMethod -Uri 'https://api.github.com/repos/bmbxwbh/BlockMind/releases/latest'; $a=$r.assets|Where-Object{$_.name -like 'blockmind-mod*'}|Select -First 1; if($a){Invoke-WebRequest -Uri $a.browser_download_url -OutFile '%MODS_DIR%\blockmind-mod.jar'}"
    )
    if exist "%MODS_DIR%\blockmind-mod.jar" (
        echo   %T_MOD_DONE%
    ) else (
        echo   %T_MOD_FAIL%
    )
) else (
    echo   %T_MOD_EXIST%
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
    echo   %T_NO_JAR%
    pause
    exit /b 1
)

cd /d "%MC_DIR%"

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   %T_LAUNCH_TITLE%
echo   ╠══════════════════════════════════════╣
echo   ║   %T_DIR%: %MC_DIR%
echo   ║   %T_JAR%:  %LAUNCH_JAR%
echo   ║   %T_MEMORY%: %MAX_RAM%
echo   ╚══════════════════════════════════════╝
echo.
echo   %T_PRESS_STOP%
echo.

java -Xms512M -Xmx%MAX_RAM% -jar %LAUNCH_JAR% nogui

echo.
echo   %T_STOPPED%
pause
