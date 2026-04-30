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
set "T_TITLE=BlockMind - 全部启动"
set "T_LAUNCH_TITLE=🧠 BlockMind 一键启动"
set "T_MC_START=[1/2] 启动 Minecraft 服务端..."
set "T_MC_WINDOW=(将在新窗口中打开)"
set "T_MC_OK=[✓] MC 服务端窗口已打开"
set "T_MC_SKIP=[!] 未找到 MC 服务端，跳过"
set "T_MC_HINT=运行 start_mc.bat 安装服务端"
set "T_BM_START=[2/2] 启动 BlockMind + WebUI..."
set "T_WEBUI=WebUI 地址"
set "T_PRESS_STOP=按 Ctrl+C 停止"
set "T_EXITED=👋 BlockMind 已退出"
goto :start_run

:lang_en
set "T_TITLE=BlockMind - Start All"
set "T_LAUNCH_TITLE=🧠 BlockMind One-click Start"
set "T_MC_START=[1/2] Starting Minecraft server..."
set "T_MC_WINDOW=(will open in new window)"
set "T_MC_OK=[✓] MC server window opened"
set "T_MC_SKIP=[!] MC server not found, skipping"
set "T_MC_HINT=Run start_mc.bat to install server"
set "T_BM_START=[2/2] Starting BlockMind + WebUI..."
set "T_WEBUI=WebUI URL"
set "T_PRESS_STOP=Press Ctrl+C to stop"
set "T_EXITED=👋 BlockMind exited"
goto :start_run

:start_run
title %T_TITLE%

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   %T_LAUNCH_TITLE%
echo   ╚══════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo   %T_MC_START%
echo   %T_MC_WINDOW%
echo.

:: 在新窗口启动 MC 服务端
if exist "mc-server\fabric-server-launch.jar" (
    start "Minecraft Server" cmd /c "cd /d "%~dp0" && call start_mc.bat"
    echo   %T_MC_OK%
    timeout /t 3 /nobreak >nul
) else if exist "mc-server\server.jar" (
    start "Minecraft Server" cmd /c "cd /d "%~dp0" && call start_mc.bat"
    echo   %T_MC_OK%
    timeout /t 3 /nobreak >nul
) else (
    echo   %T_MC_SKIP%
    echo   %T_MC_HINT%
)

echo.
echo   %T_BM_START%
echo   %T_WEBUI%: http://localhost:19951
echo   %T_PRESS_STOP%
echo.

python -m src.main

echo.
echo   %T_EXITED%
pause
