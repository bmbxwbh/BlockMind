@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: ============================================================
:: BlockMind - Windows Unified Launcher
:: ============================================================

:: -- Language Selection --
echo.
echo   Select language / 选择语言
echo.
echo     1) 中文
echo     2) English
echo.
set /p BM_LANG="  [1/2]: "
if "%BM_LANG%"=="2" goto :lang_en
if "%BM_LANG%"=="en" goto :lang_en
if "%BM_LANG%"=="EN" goto :lang_en
goto :lang_zh

:lang_zh
set "T_TITLE=BlockMind - 一体化启动脚本"
set "T_PY_NO=[X] 未找到 Python!"
set "T_PY_HINT=请从 https://python.org 下载 Python 3.10+"
set "T_PIP_NO=[X] 未找到 pip!"
set "T_JAVA_NO=[!] 未找到 Java 17+"
set "T_JAVA_HINT=MC 服务端需要 Java，下载: https://adoptium.net/"
set "T_DEPS_INSTALL=安装 Python 依赖..."
set "T_DEPS_OK=[OK] 依赖安装完成"
set "T_DEPS_FAIL=[X] 依赖安装失败!"
set "T_CONFIG_CREATED=[OK] 已创建 config.yaml，请编辑配置"
set "T_CONFIG_EXISTS=[OK] config.yaml 已存在"
set "T_MC_INSTALL=安装 MC 服务端？[y/N]"
set "T_MC_INSTALLING=安装 Fabric 服务端..."
set "T_MC_DONE=[OK] MC 服务端安装完成"
set "T_MC_SKIP=跳过 MC 服务端安装"
set "T_MC_DETECTED=检测到 MC 服务端"
set "T_BM_START=启动 BlockMind..."
set "T_WEBUI=WebUI: http://localhost:19951"
set "T_PRESS_STOP=按 Ctrl+C 停止"
set "T_EXITED=BlockMind 已退出"
set "T_INSTALLED=BlockMind 已安装"
set "T_MENU_START=启动"
set "T_MENU_REPAIR=修复 (重新安装依赖)"
set "T_MENU_REMOVE=卸载 (删除所有数据)"
set "T_MENU_REINSTALL=重新安装"
set "T_CONFIRM_DELETE=确认删除所有数据？(y/N):"
set "T_UNINSTALLED=已卸载"
set "T_CANCEL_DELETE=取消卸载"
set "T_SELECT_MODE=选择运行模式"
set "T_MODE_SERVER=服务端模式 -- 自动下载安装 MC 服务端"
set "T_MODE_CLIENT=客户端模式 -- 使用本地 Minecraft 客户端"
set "T_CLIENT_HINT=请先从 PCL2 或官方启动器安装 Minecraft"
set "T_CLIENT_HINT2=安装 BlockMind Mod 后放入 mods/ 目录"
set "T_CLIENT_WEBUI=启动后访问 http://localhost:19951 控制"
set "T_PCL2_URL=PCL2 下载: https://github.com/TCM-Corp/PCL/releases"
set "T_SKIP_DEPS=跳过依赖安装 (启动模式)"
set "T_FORCE_REINSTALL=强制重新安装依赖..."
set "T_REINSTALL_READY=已卸载，准备重新安装..."
goto :start_run

:lang_en
set "T_TITLE=BlockMind - Unified Launcher"
set "T_PY_NO=[X] Python not found!"
set "T_PY_HINT=Please download Python 3.10+ from https://python.org"
set "T_PIP_NO=[X] pip not found!"
set "T_JAVA_NO=[!] Java 17+ not found"
set "T_JAVA_HINT=Java needed for MC server, download: https://adoptium.net/"
set "T_DEPS_INSTALL=Installing Python dependencies..."
set "T_DEPS_OK=[OK] Dependencies installed"
set "T_DEPS_FAIL=[X] Dependency installation failed!"
set "T_CONFIG_CREATED=[OK] config.yaml created, please edit config"
set "T_CONFIG_EXISTS=[OK] config.yaml already exists"
set "T_MC_INSTALL=Install MC server? [y/N]"
set "T_MC_INSTALLING=Installing Fabric server..."
set "T_MC_DONE=[OK] MC server installed"
set "T_MC_SKIP=Skipping MC server install"
set "T_MC_DETECTED=MC server detected"
set "T_BM_START=Starting BlockMind..."
set "T_WEBUI=WebUI: http://localhost:19951"
set "T_PRESS_STOP=Press Ctrl+C to stop"
set "T_EXITED=BlockMind exited"
set "T_INSTALLED=BlockMind is installed"
set "T_MENU_START=Start"
set "T_MENU_REPAIR=Repair (reinstall dependencies)"
set "T_MENU_REMOVE=Uninstall (delete all data)"
set "T_MENU_REINSTALL=Reinstall"
set "T_CONFIRM_DELETE=Confirm delete all data? (y/N):"
set "T_UNINSTALLED=Uninstalled"
set "T_CANCEL_DELETE=Cancel uninstall"
set "T_SELECT_MODE=Select run mode"
set "T_MODE_SERVER=Server mode -- auto-download MC server"
set "T_MODE_CLIENT=Client mode -- use local Minecraft client"
set "T_CLIENT_HINT=Install Minecraft via PCL2 or official launcher first"
set "T_CLIENT_HINT2=Put BlockMind Mod into mods/ directory"
set "T_CLIENT_WEBUI=Access http://localhost:19951 to control"
set "T_PCL2_URL=PCL2 download: https://github.com/TCM-Corp/PCL/releases"
set "T_SKIP_DEPS=Skipping dependency installation (Start mode)"
set "T_FORCE_REINSTALL=Force reinstalling dependencies..."
set "T_REINSTALL_READY=Uninstalled, ready to reinstall..."
goto :start_run

:start_run
title %T_TITLE%
cd /d "%~dp0"

echo.
echo   ========================================
echo     %T_TITLE%
echo   ========================================
echo.

:: -- Installation Detection --
set INSTALLED=0
if exist .venv set INSTALLED=1
if exist config.yaml set INSTALLED=1
if exist data\memory set INSTALLED=1
if exist mc-server set INSTALLED=1
set MODE=fresh

if %INSTALLED%==1 (
    echo   %T_INSTALLED%
    echo.
    echo     1^) %T_MENU_START%
    echo     2^) %T_MENU_REPAIR%
    echo     3^) %T_MENU_REMOVE%
    echo     4^) %T_MENU_REINSTALL%
    echo.
    set /p INSTALL_CHOICE="  [1/2/3/4]: "
    if "!INSTALL_CHOICE!"=="1" set MODE=start
    if "!INSTALL_CHOICE!"=="2" set MODE=repair
    if "!INSTALL_CHOICE!"=="3" goto :do_remove
    if "!INSTALL_CHOICE!"=="4" goto :do_reinstall
    echo   [!] Invalid choice, default to start
    set MODE=start
    goto :after_install_menu
)

:do_remove
echo.
set /p CONFIRM="  %T_CONFIRM_DELETE% "
if /i "!CONFIRM!"=="y" (
    if exist .venv rmdir /s /q .venv
    if exist config.yaml del config.yaml
    if exist data rmdir /s /q data
    if exist mc-server rmdir /s /q mc-server
    echo   %T_UNINSTALLED%
    pause
    exit /b 0
) else (
    echo   %T_CANCEL_DELETE%
    goto :start_run
)

:do_reinstall
echo.
set /p CONFIRM="  %T_CONFIRM_DELETE% "
if /i "!CONFIRM!"=="y" (
    if exist .venv rmdir /s /q .venv
    if exist config.yaml del config.yaml
    if exist data rmdir /s /q data
    if exist mc-server rmdir /s /q mc-server
    echo   %T_REINSTALL_READY%
    set MODE=reinstall
) else (
    echo   %T_CANCEL_DELETE%
    goto :start_run
)

:after_install_menu

:: -- Mode Selection --
set RUN_MODE=server
if "%MODE%"=="start" if exist mc-server (
    set RUN_MODE=server
    goto :skip_mode_select
)

echo.
echo   ========================================
echo     %T_SELECT_MODE%
echo   ========================================
echo.
echo     1^) %T_MODE_SERVER%
echo     2^) %T_MODE_CLIENT%
echo.
set /p MODE_CHOICE="  [1/2]: "
if "%MODE_CHOICE%"=="2" goto :client_mode
if "%MODE_CHOICE%"=="client" goto :client_mode
if "%MODE_CHOICE%"=="Client" goto :client_mode
goto :skip_mode_select

:client_mode
set RUN_MODE=client
echo.
echo   %T_CLIENT_HINT%
echo   %T_CLIENT_HINT2%
echo   %T_PCL2_URL%
echo   %T_CLIENT_WEBUI%
echo.
pause

:skip_mode_select

:: -- Environment Check --
echo.
echo   Environment Check
echo   -----------------------------------------

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   %T_PY_NO%
    echo   %T_PY_HINT%
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo   [OK] Python %%v

:: Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   %T_PIP_NO%
    pause
    exit /b 1
)
echo   [OK] pip

:: Check Java
java -version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%v in ('java -version 2^>^&1 ^| findstr "version"') do echo   [OK] Java %%v
) else (
    echo   %T_JAVA_NO%
    echo   %T_JAVA_HINT%
)

:: -- Dependency Installation --
echo.
echo   Dependencies
echo   -----------------------------------------

if "%MODE%"=="start" (
    echo   %T_SKIP_DEPS%
    if exist .venv call .venv\Scripts\activate.bat
    goto :deps_done
)

if "%MODE%"=="repair" (
    echo   %T_FORCE_REINSTALL%
    if exist .venv rmdir /s /q .venv
)

:: Create venv
if not exist .venv (
    echo   Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo   [X] Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate and install
call .venv\Scripts\activate.bat

echo   %T_DEPS_INSTALL%

:: Detect China mirror
curl -s --connect-timeout 3 "https://mirrors.aliyun.com/pypi/simple/" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Using China mirror (Aliyun)
    pip install --upgrade pip -q 2>nul
    pip install -r requirements.txt -q --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
) else (
    echo   Using default PyPI
    pip install --upgrade pip -q 2>nul
    pip install -r requirements.txt -q
)

if %errorlevel% neq 0 (
    echo   %T_DEPS_FAIL%
    pause
    exit /b 1
)
echo   %T_DEPS_OK%

:deps_done

:: -- Config Initialization --
echo.
echo   Config
echo   -----------------------------------------

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

:: -- Minecraft Server Setup --
if "%RUN_MODE%"=="server" (
    echo.
    echo   Minecraft Server
    echo   -----------------------------------------

    set MC_DIR=
    set MC_JAR=
    set JAVA_OK=0

    java -version >nul 2>&1
    if %errorlevel% equ 0 set JAVA_OK=1

    :: Detect existing server
    if exist "%~dp0mc-server\fabric-server-launch.jar" (
        set "MC_DIR=%~dp0mc-server"
        set MC_JAR=fabric-server-launch.jar
        echo   %T_MC_DETECTED%
    ) else if exist "%~dp0mc-server\server.jar" (
        set "MC_DIR=%~dp0mc-server"
        set MC_JAR=server.jar
        echo   %T_MC_DETECTED%
    )

    :: Offer to install if no server found
    if not defined MC_DIR (
        if !JAVA_OK!==1 (
            echo.
            set /p INSTALL_MC="  %T_MC_INSTALL% "
            if /i "!INSTALL_MC!"=="y" (
                echo   %T_MC_INSTALLING%
                set "MC_DIR=%~dp0mc-server"
                if not exist "!MC_DIR!" mkdir "!MC_DIR!"

                :: Download Fabric installer
                set "FABRIC_VER=0.15.3"
                set "INSTALLER_URL=https://maven.fabricmc.net/net/fabricmc/fabric-installer/!FABRIC_VER!/fabric-installer-!FABRIC_VER!.jar"
                if not exist "!MC_DIR!\fabric-installer.jar" (
                    curl -L -o "!MC_DIR!\fabric-installer.jar" "!INSTALLER_URL!" 2>nul
                    if %errorlevel% neq 0 (
                        powershell -Command "Invoke-WebRequest -Uri '!INSTALLER_URL!' -OutFile '!MC_DIR!\fabric-installer.jar'" 2>nul
                    )
                )

                :: Install Fabric
                if not exist "!MC_DIR!\fabric-server-launch.jar" (
                    java -jar "!MC_DIR!\fabric-installer.jar" server -dir "!MC_DIR!" -mcversion 1.20.4 -loader 0.15.3 -downloadMinecraft
                )

                :: Download BlockMind mod
                set "MODS_DIR=!MC_DIR!\mods"
                if not exist "!MODS_DIR!" mkdir "!MODS_DIR!"

                echo   %T_MC_DONE%
            ) else (
                echo   %T_MC_SKIP%
            )
        ) else (
            echo   %T_MC_SKIP% (Java not available)
        )
    )
)

:: -- Launch Summary --
echo.
echo   ========================================
echo     Startup Summary
echo   ========================================

if "%RUN_MODE%"=="server" (
    echo   Mode: Server
) else (
    echo   Mode: Client
)

if defined MC_DIR (
    echo   MC Server: !MC_DIR!
) else (
    if "%RUN_MODE%"=="server" echo   MC Server: Not configured
)
echo   BlockMind: Current window
echo   WebUI: http://localhost:19951
echo   %T_PRESS_STOP%
echo.

:: -- Start MC Server --
if "%RUN_MODE%"=="server" (
    if defined MC_DIR (
        start "Minecraft Server" cmd /k "cd /d "!MC_DIR!" && java -Xms512M -Xmx2G -jar !MC_JAR! nogui"
        timeout /t 3 /nobreak >nul
    )
)

:: -- Start BlockMind --
echo   %T_BM_START%
echo.
python -m src.main

echo.
echo   %T_EXITED%
pause
