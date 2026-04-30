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
set "T_TITLE=BlockMind - AI 玩伴系统"
set "T_STARTING=🧠 BlockMind 启动中..."
set "T_STOP=按 Ctrl+C 停止"
set "T_EXITED=👋 BlockMind 已退出"
goto :start_run

:lang_en
set "T_TITLE=BlockMind - AI Companion System"
set "T_STARTING=🧠 BlockMind starting..."
set "T_STOP=Press Ctrl+C to stop"
set "T_EXITED=👋 BlockMind exited"
goto :start_run

:start_run
title %T_TITLE%

echo.
echo   %T_STARTING%
echo   %T_STOP%
echo.

cd /d "%~dp0"
python -m src.main

echo.
echo   %T_EXITED%
pause
