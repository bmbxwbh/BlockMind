@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

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
set "T_TITLE=BlockMind - 一体化启动脚本"
set "T_ENV_CHECK=🔍 环境检查"
set "T_PY_OK=[✓] Python 已就绪"
set "T_PY_NO=[✗] 未找到 Python！"
set "T_PY_HINT=请从 https://python.org 下载 Python 3.10+"
set "T_PIP_OK=[✓] pip 已就绪"
set "T_PIP_NO=[✗] 未找到 pip！"
set "T_JAVA_OK=[✓] Java 已就绪"
set "T_JAVA_NO=[✗] 未找到 Java 17+"
set "T_JAVA_HINT=MC 服务端需要 Java，下载: https://adoptium.net/"
set "T_DEPS=📦 依赖安装"
set "T_DEPS_VENV=创建虚拟环境..."
set "T_DEPS_INSTALL=安装 Python 依赖..."
set "T_DEPS_OK=[✓] 依赖安装完成"
set "T_DEPS_FAIL=[✗] 依赖安装失败！"
set "T_CONFIG=⚙️ 配置初始化"
set "T_CONFIG_CREATED=[✓] 已创建 config.yaml，请编辑配置"
set "T_CONFIG_EXISTS=[✓] config.yaml 已存在"
set "T_MC_SETUP=🎮 Minecraft 服务端"
set "T_MC_INSTALL=安装 MC 服务端？[y/N]"
set "T_MC_INSTALLING=安装 Fabric 服务端..."
set "T_MC_DONE=[✓] MC 服务端安装完成"
set "T_MC_SKIP=跳过 MC 服务端安装"
set "T_MC_DETECTED=检测到 MC 服务端"
set "T_LAUNCH=🚀 启动服务"
set "T_MC_WINDOW=MC 服务端将启动在新窗口"
set "T_BM_START=启动 BlockMind..."
set "T_WEBUI=WebUI 地址: http://localhost:19951"
set "T_PRESS_STOP=按 Ctrl+C 停止"
set "T_EXITED=👋 BlockMind 已退出"
set "T_SUMMARY=📋 启动摘要"
goto :start_run

:lang_en
set "T_TITLE=BlockMind - Unified Launcher"
set "T_ENV_CHECK=🔍 Environment Check"
set "T_PY_OK=[✓] Python ready"
set "T_PY_NO=[✗] Python not found!"
set "T_PY_HINT=Please download Python 3.10+ from https://python.org"
set "T_PIP_OK=[✓] pip ready"
set "T_PIP_NO=[✗] pip not found!"
set "T_JAVA_OK=[✓] Java ready"
set "T_JAVA_NO=[✗] Java 17+ not found"
set "T_JAVA_HINT=Java needed for MC server, download: https://adoptium.net/"
set "T_DEPS=📦 Dependency Installation"
set "T_DEPS_VENV=Creating virtual environment..."
set "T_DEPS_INSTALL=Installing Python dependencies..."
set "T_DEPS_OK=[✓] Dependencies installed"
set "T_DEPS_FAIL=[✗] Dependency installation failed!"
set "T_CONFIG=⚙️ Config Initialization"
set "T_CONFIG_CREATED=[✓] config.yaml created, please edit config"
set "T_CONFIG_EXISTS=[✓] config.yaml already exists"
set "T_MC_SETUP=🎮 Minecraft Server"
set "T_MC_INSTALL=Install MC server? [y/N]"
set "T_MC_INSTALLING=Installing Fabric server..."
set "T_MC_DONE=[✓] MC server installed"
set "T_MC_SKIP=Skipping MC server install"
set "T_MC_DETECTED=MC server detected"
set "T_LAUNCH=🚀 Starting Services"
set "T_MC_WINDOW=MC server will start in new window"
set "T_BM_START=Starting BlockMind..."
set "T_WEBUI=WebUI URL: http://localhost:19951"
set "T_PRESS_STOP=Press Ctrl+C to stop"
set "T_EXITED=👋 BlockMind exited"
set "T_SUMMARY=📋 Startup Summary"
goto :start_run

:start_run
title %T_TITLE%
cd /d "%~dp0"

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   %T_TITLE%
echo   ╚══════════════════════════════════════╝
echo.

:: ── Environment Check ──
echo   %T_ENV_CHECK%
echo   ──────────────────────────────────────

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   %T_PY_NO%
    echo   %T_PY_HINT%
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo   %T_PY_OK% %%v

:: Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   %T_PIP_NO%
    pause
    exit /b 1
)
echo   %T_PIP_OK%

:: Check Java (optional for MC server)
java -version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%v in ('java -version 2^>^&1 ^| findstr "version"') do echo   %T_JAVA_OK% %%v
) else (
    echo   %T_JAVA_NO%
    echo   %T_JAVA_HINT%
)

echo.

:: ── Dependency Installation ──
echo   %T_DEPS%
echo   ──────────────────────────────────────

:: Create virtual environment if not exists
if not exist .venv (
    echo   %T_DEPS_VENV%
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo   [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate venv and install dependencies
call .venv\Scripts\activate.bat

echo   %T_DEPS_INSTALL%
curl -s --connect-timeout 3 "https://mirrors.aliyun.com/pypi/simple/" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Using China mirror (Aliyun)
    pip install --upgrade pip -q
    pip install -r requirements.txt -q --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
) else (
    echo   Using default PyPI
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
)

if %errorlevel% neq 0 (
    echo   %T_DEPS_FAIL%
    pause
    exit /b 1
)
echo   %T_DEPS_OK%

echo.

:: ── Config Initialization ──
echo   %T_CONFIG%
echo   ──────────────────────────────────────

if not exist config.yaml (
    copy config.example.yaml config.yaml >nul
    echo   %T_CONFIG_CREATED%
) else (
    echo   %T_CONFIG_EXISTS%
)

:: Create data directories
if not exist data\skills mkdir data\skills
if not exist data\logs mkdir data\logs
if not exist data\memory mkdir data\memory
if not exist data\backups mkdir data\backups

echo.

:: ── Minecraft Server Setup ──
echo   %T_MC_SETUP%
echo   ──────────────────────────────────────

set MC_DIR=
set MC_JAR=
set JAVA_OK=0

:: Check if Java is available
java -version >nul 2>&1
if %errorlevel% equ 0 set JAVA_OK=1

:: Detect existing MC server
if exist "%~dp0mc-server\fabric-server-launch.jar" (
    set MC_DIR=%~dp0mc-server
    set MC_JAR=fabric-server-launch.jar
    echo   %T_MC_DETECTED%: %MC_DIR%
) else if exist "%~dp0mc-server\server.jar" (
    set MC_DIR=%~dp0mc-server
    set MC_JAR=server.jar
    echo   %T_MC_DETECTED%: %MC_DIR%
) else if exist "%~dp0server\fabric-server-launch.jar" (
    set MC_DIR=%~dp0server
    set MC_JAR=fabric-server-launch.jar
    echo   %T_MC_DETECTED%: %MC_DIR%
) else if exist "%~dp0minecraft-server\fabric-server-launch.jar" (
    set MC_DIR=%~dp0minecraft-server
    set MC_JAR=fabric-server-launch.jar
    echo   %T_MC_DETECTED%: %MC_DIR%
)

:: If no MC server found and Java is available, offer to install
if not defined MC_DIR (
    if %JAVA_OK%==1 (
        echo.
        set /p INSTALL_MC="  %T_MC_INSTALL% "
        if /i "!INSTALL_MC!"=="y" (
            echo   %T_MC_INSTALLING%
            set MC_DIR=%~dp0mc-server
            if not exist "%MC_DIR%" mkdir "%MC_DIR%"
            
            :: Download Fabric installer
            if not exist "%MC_DIR%\fabric-installer.jar" (
                set FABRIC_VERSION=0.15.3
                set INSTALLER_URL=https://maven.fabricmc.net/net/fabricmc/fabric-installer/!FABRIC_VERSION!/fabric-installer-!FABRIC_VERSION!.jar
                curl --version >nul 2>&1
                if %errorlevel% equ 0 (
                    curl -L -o "%MC_DIR%\fabric-installer.jar" "!INSTALLER_URL!"
                ) else (
                    powershell -Command "Invoke-WebRequest -Uri '!INSTALLER_URL!' -OutFile '%MC_DIR%\fabric-installer.jar'"
                )
            )
            
            :: Install Fabric server
            if not exist "%MC_DIR%\fabric-server-launch.jar" (
                java -jar "%MC_DIR%\fabric-installer.jar" server -dir "%MC_DIR%" -mcversion 1.20.4 -loader 0.15.3 -downloadMinecraft
            )
            
            :: Download BlockMind mod
            set MODS_DIR=%MC_DIR%\mods
            if not exist "%MODS_DIR%" mkdir "%MODS_DIR%"
            dir /b "%MODS_DIR%\blockmind-mod-*.jar" >nul 2>&1
            if %errorlevel% neq 0 (
                curl --version >nul 2>&1
                if %errorlevel% equ 0 (
                    curl -sL "https://api.github.com/repos/bmbxwbh/BlockMind/releases/latest" | findstr "browser_download_url" | findstr "blockmind-mod" > "%TEMP%\bm_url.txt"
                    for /f "tokens=2 delims=\" %%u" in ('type "%TEMP%\bm_url.txt"') do (
                        curl -L -o "%MODS_DIR%\blockmind-mod.jar" "%%u"
                    )
                    del "%TEMP%\bm_url.txt" >nul 2>&1
                )
            )
            
            set MC_JAR=fabric-server-launch.jar
            echo   %T_MC_DONE%
        ) else (
            echo   %T_MC_SKIP%
        )
    ) else (
        echo   %T_MC_SKIP% (Java not available)
    )
)

echo.

:: ── Launch Summary ──
echo   %T_SUMMARY%
echo   ──────────────────────────────────────

if defined MC_DIR (
    echo   • MC Server: %MC_DIR% (%MC_JAR%)
    echo   • MC Server will start in new window
) else (
    echo   • MC Server: Not configured
)
echo   • BlockMind: Current window
echo   • WebUI: http://localhost:19951
echo   • %T_PRESS_STOP%
echo.

:: ── Start MC Server in New Window ──
if defined MC_DIR (
    echo   %T_MC_WINDOW%
    start "Minecraft Server" cmd /c "cd /d \"%MC_DIR%\" && java -Xms512M -Xmx2G -jar %MC_JAR% nogui"
    timeout /t 3 /nobreak >nul
)

:: ── Start BlockMind in Current Window ──
echo   %T_BM_START%
echo.
python -m src.main

echo.
echo   %T_EXITED%
pause