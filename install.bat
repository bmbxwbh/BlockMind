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
set "T_TITLE=🧠 BlockMind Windows 安装向导"
set "T_NO_PY=[错误] 未找到 Python！"
set "T_INSTALL_PY=请从 https://python.org 下载安装 Python 3.10+"
set "T_CHECK_PY=安装时务必勾选 \"Add Python to PATH\""
set "T_NO_PIP=[错误] 未找到 pip！请重新安装 Python"
set "T_PIP_OK=pip 可用"
set "T_STEP1=[1/4] 安装 Python 依赖..."
set "T_DEPS_FAIL=[错误] 依赖安装失败！"
set "T_DEPS_OK=[✓] 依赖安装完成"
set "T_STEP2=[2/4] 初始化配置..."
set "T_CONFIG_CREATED=[✓] 已创建 config.yaml，请编辑配置 AI 模型和密码"
set "T_CONFIG_EXISTS=[✓] config.yaml 已存在，跳过"
set "T_STEP3=[3/4] 创建数据目录..."
set "T_DATA_OK=[✓] 数据目录已创建"
set "T_STEP4=[4/4] 安装完成！"
set "T_DONE_TITLE=✅ BlockMind 安装成功！"
set "T_HINT_START=启动方式："
set "T_HINT1=双击 start.bat 启动 BlockMind"
set "T_HINT2=双击 start_mc.bat 启动 MC 服务端"
set "T_HINT3=双击 start_all.bat 全部启动"
goto :start_install

:lang_en
set "T_TITLE=🧠 BlockMind Windows Install Wizard"
set "T_NO_PY=[ERROR] Python not found!"
set "T_INSTALL_PY=Please download Python 3.10+ from https://python.org"
set "T_CHECK_PY=Be sure to check \"Add Python to PATH\" during install"
set "T_NO_PIP=[ERROR] pip not found! Please reinstall Python"
set "T_PIP_OK=pip available"
set "T_STEP1=[1/4] Installing Python dependencies..."
set "T_DEPS_FAIL=[ERROR] Dependency installation failed!"
set "T_DEPS_OK=[✓] Dependencies installed"
set "T_STEP2=[2/4] Initializing config..."
set "T_CONFIG_CREATED=[✓] config.yaml created, please edit AI model and password"
set "T_CONFIG_EXISTS=[✓] config.yaml already exists, skipping"
set "T_STEP3=[3/4] Creating data directories..."
set "T_DATA_OK=[✓] Data directories created"
set "T_STEP4=[4/4] Installation complete!"
set "T_DONE_TITLE=✅ BlockMind installed successfully!"
set "T_HINT_START=How to start:"
set "T_HINT1=Double-click start.bat to start BlockMind"
set "T_HINT2=Double-click start_mc.bat to start MC server"
set "T_HINT3=Double-click start_all.bat to start all"
goto :start_install

:start_install
title %T_TITLE%

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   %T_TITLE%
echo   ╚══════════════════════════════════════╝
echo.

:: ── 检查 Python ──
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   %T_NO_PY%
    echo   %T_INSTALL_PY%
    echo   %T_CHECK_PY%
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo   [✓] Python %%v

:: ── 检查 pip ──
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   %T_NO_PIP%
    pause
    exit /b 1
)
echo   [✓] %T_PIP_OK%

:: ── 安装 Python 依赖 ──
echo.
echo   %T_STEP1%
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo   %T_DEPS_FAIL%
    pause
    exit /b 1
)
echo   %T_DEPS_OK%

:: ── 初始化配置 ──
echo.
echo   %T_STEP2%
if not exist config.yaml (
    copy config.example.yaml config.yaml >nul
    echo   %T_CONFIG_CREATED%
) else (
    echo   %T_CONFIG_EXISTS%
)

:: ── 创建数据目录 ──
echo.
echo   %T_STEP3%
if not exist data\skills mkdir data\skills
if not exist data\logs mkdir data\logs
if not exist data\memory mkdir data\memory
if not exist data\backups mkdir data\backups
echo   %T_DATA_OK%

:: ── 完成 ──
echo.
echo   %T_STEP4%
echo.
echo   ╔══════════════════════════════════════╗
echo   ║   %T_DONE_TITLE%
echo   ╠══════════════════════════════════════╣
echo   ║   %T_HINT_START%
echo   ║   %T_HINT1%
echo   ║   %T_HINT2%
echo   ║   %T_HINT3%
echo   ╚══════════════════════════════════════╝
echo.
pause
