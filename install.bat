@echo off
chcp 65001 >nul 2>&1
title BlockMind - Windows 安装向导

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   🧠 BlockMind Windows 安装向导      ║
echo   ╚══════════════════════════════════════╝
echo.

:: ── 检查 Python ──
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [错误] 未找到 Python！
    echo   请从 https://python.org 下载安装 Python 3.10+
    echo   安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo   [✓] Python %%v

:: ── 检查 pip ──
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [错误] 未找到 pip！请重新安装 Python
    pause
    exit /b 1
)
echo   [✓] pip 可用

:: ── 安装 Python 依赖 ──
echo.
echo   [1/4] 安装 Python 依赖...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo   [错误] 依赖安装失败！
    pause
    exit /b 1
)
echo   [✓] 依赖安装完成

:: ── 初始化配置 ──
echo.
echo   [2/4] 初始化配置...
if not exist config.yaml (
    copy config.example.yaml config.yaml >nul
    echo   [✓] 已创建 config.yaml，请编辑配置 AI 模型和密码
) else (
    echo   [✓] config.yaml 已存在，跳过
)

:: ── 创建数据目录 ──
echo.
echo   [3/4] 创建数据目录...
if not exist data\skills mkdir data\skills
if not exist data\logs mkdir data\logs
if not exist data\memory mkdir data\memory
if not exist data\backups mkdir data\backups
echo   [✓] 数据目录已创建

:: ── 完成 ──
echo.
echo   [4/4] 安装完成！
echo.
echo   ╔══════════════════════════════════════╗
echo   ║   ✅ BlockMind 安装成功！              ║
echo   ╠══════════════════════════════════════╣
echo   ║   启动方式：                          ║
echo   ║     双击 start.bat 启动 BlockMind    ║
echo   ║     双击 start_mc.bat 启动 MC 服务端  ║
echo   ║     双击 start_all.bat 全部启动       ║
echo   ╚══════════════════════════════════════╝
echo.
pause
