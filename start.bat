@echo off
chcp 65001 >nul 2>&1
title BlockMind - AI 玩伴系统

echo.
echo   🧠 BlockMind 启动中...
echo   按 Ctrl+C 停止
echo.

cd /d "%~dp0"
python -m src.main

echo.
echo   👋 BlockMind 已退出
pause
