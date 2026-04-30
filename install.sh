#!/usr/bin/env bash
# ═══════════════════════════════════════
# BlockMind — One-click Install Script
# ═══════════════════════════════════════
set -euo pipefail

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
NC="\033[0m"

info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

# ── Language Selection ──
select_lang() {
    # Allow env override: LANG=zh or LANG=en
    case "${LANG:-}" in
        zh|ZH) BM_LANG=zh ;;
        en|EN) BM_LANG=en ;;
        *)
            echo ""
            echo -e "${CYAN}  Select language / 选择语言${NC}"
            echo ""
            echo "    1) 中文"
            echo "    2) English"
            echo ""
            read -rp "  [1/2]: " lang_choice
            case "${lang_choice:-1}" in
                2) BM_LANG=en ;;
                *) BM_LANG=zh ;;
            esac
            ;;
    esac
}

# ── Localized Strings ──
load_strings() {
    if [ "$BM_LANG" = "zh" ]; then
        T_TITLE="🧠 BlockMind 安装向导"
        T_OPT_LOCAL="本地部署（Python 直接运行）"
        T_OPT_DOCKER="Docker 部署"
        T_CHOOSE="选择 [1/2]"
        T_INVALID="无效选择"
        T_DEPS_MISSING="缺少依赖"
        T_DEPS_INSTALL="请先安装 Python 3.10+"
        T_PYTHON_VER="Python 版本"
        T_INSTALL_DEPS="安装 Python 依赖..."
        T_DEPS_DONE="依赖安装完成"
        T_INIT_CONFIG="初始化配置文件..."
        T_CONFIG_EXISTS="config.yaml 已存在，跳过"
        T_EDIT_CONFIG="请编辑 config.yaml 配置 AI 模型和密码"
        T_DATA_DIR="数据目录已创建"
        T_STARTING="启动 BlockMind"
        T_WEBUI="WebUI 地址"
        T_PASSWORD="密码"
        T_STARTED="BlockMind 已启动"
        T_START_FAIL="启动失败，请检查日志"
        T_DOCKER_NOT="未安装 Docker"
        T_DOCKER_DEPLOY="Docker 部署中..."
        T_DOCKER_DONE="BlockMind Docker 容器已启动"
        T_PORT="端口"
    else
        T_TITLE="🧠 BlockMind Install Wizard"
        T_OPT_LOCAL="Local deploy (Python direct run)"
        T_OPT_DOCKER="Docker deploy"
        T_CHOOSE="Choose [1/2]"
        T_INVALID="Invalid choice"
        T_DEPS_MISSING="Missing dependencies"
        T_DEPS_INSTALL="Please install Python 3.10+ first"
        T_PYTHON_VER="Python version"
        T_INSTALL_DEPS="Installing Python dependencies..."
        T_DEPS_DONE="Dependencies installed"
        T_INIT_CONFIG="Initializing config file..."
        T_CONFIG_EXISTS="config.yaml already exists, skipping"
        T_EDIT_CONFIG="Please edit config.yaml to configure AI model and password"
        T_DATA_DIR="Data directories created"
        T_STARTING="Starting BlockMind"
        T_WEBUI="WebUI URL"
        T_PASSWORD="Password"
        T_STARTED="BlockMind started"
        T_START_FAIL="Start failed, please check logs"
        T_DOCKER_NOT="Docker not installed"
        T_DOCKER_DEPLOY="Deploying with Docker..."
        T_DOCKER_DONE="BlockMind Docker container started"
        T_PORT="Port"
    fi
}

# ── 检查依赖 ──
check_deps() {
    local missing=()
    command -v python3 >/dev/null || missing+=("python3")
    command -v pip3 >/dev/null || command -v pip >/dev/null || missing+=("pip3")
    if [ ${#missing[@]} -gt 0 ]; then
        error "${T_DEPS_MISSING}: ${missing[*]}\n${T_DEPS_INSTALL}"
    fi
    info "${T_PYTHON_VER}: $(python3 --version 2>&1 | cut -d' ' -f2)"
}

# ── 安装 Python 依赖 ──
install_deps() {
    info "${T_INSTALL_DEPS}"
    pip3 install -r requirements.txt --quiet 2>/dev/null || pip install -r requirements.txt --quiet
    info "${T_DEPS_DONE}"
}

# ── 初始化配置 ──
init_config() {
    if [ ! -f config.yaml ]; then
        info "${T_INIT_CONFIG}"
        cp config.example.yaml config.yaml
        warn "${T_EDIT_CONFIG}"
    else
        info "${T_CONFIG_EXISTS}"
    fi
}

# ── 创建数据目录 ──
init_data() {
    mkdir -p data/{skills,logs,memory,backups}
    info "${T_DATA_DIR}"
}

# ── 启动服务 ──
start_service() {
    local port=${BLOCKMIND_PORT:-19951}
    info "${T_STARTING} (${T_PORT} $port)..."
    BLOCKMIND_PORT=$port python3 -m src.main &
    sleep 2
    if ss -tlnp | grep -q ":$port"; then
        info "${T_STARTED}"
        info "  ${T_WEBUI}: http://localhost:$port"
        info "  ${T_PASSWORD}: $(grep 'password:' config.yaml 2>/dev/null | head -1 | awk '{print $2}' || echo 'see config.yaml')"
    else
        error "${T_START_FAIL}"
    fi
}

# ── Docker 部署 ──
deploy_docker() {
    if ! command -v docker >/dev/null; then
        error "${T_DOCKER_NOT}"
    fi
    info "${T_DOCKER_DEPLOY}"
    docker compose up -d --build
    info "${T_DOCKER_DONE}"
    info "  ${T_WEBUI}: http://localhost:19951"
}

# ── 主流程 ──
main() {
    select_lang
    load_strings

    echo ""
    echo "  ${T_TITLE}"
    echo "  ════════════════════"
    echo ""
    echo "  1) ${T_OPT_LOCAL}"
    echo "  2) ${T_OPT_DOCKER}"
    echo ""
    read -rp "  ${T_CHOOSE}: " choice

    case "$choice" in
        1)
            check_deps
            install_deps
            init_config
            init_data
            start_service
            ;;
        2)
            deploy_docker
            ;;
        *)
            error "${T_INVALID}"
            ;;
    esac
}

main "$@"
