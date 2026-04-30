#!/usr/bin/env bash
# ═══════════════════════════════════════
# BlockMind — 一键部署脚本
# ═══════════════════════════════════════
set -euo pipefail

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── 检查依赖 ──
check_deps() {
    local missing=()
    command -v python3 >/dev/null || missing+=("python3")
    command -v pip3 >/dev/null || command -v pip >/dev/null || missing+=("pip3")
    if [ ${#missing[@]} -gt 0 ]; then
        error "缺少依赖: ${missing[*]}\n请先安装 Python 3.10+"
    fi
    info "Python $(python3 --version 2>&1 | cut -d' ' -f2)"
}

# ── 安装 Python 依赖 ──
install_deps() {
    info "安装 Python 依赖..."
    pip3 install -r requirements.txt --quiet 2>/dev/null || pip install -r requirements.txt --quiet
    info "依赖安装完成"
}

# ── 初始化配置 ──
init_config() {
    if [ ! -f config.yaml ]; then
        info "初始化配置文件..."
        cp config.example.yaml config.yaml
        warn "请编辑 config.yaml 配置 AI 模型和密码"
    else
        info "config.yaml 已存在，跳过"
    fi
}

# ── 创建数据目录 ──
init_data() {
    mkdir -p data/{skills,logs,memory,backups}
    info "数据目录已创建"
}

# ── 启动服务 ──
start_service() {
    local port=${BLOCKMIND_PORT:-19951}
    info "启动 BlockMind (端口 $port)..."
    BLOCKMIND_PORT=$port python3 -m src.main &
    sleep 2
    if ss -tlnp | grep -q ":$port"; then
        info "✅ BlockMind 已启动"
        info "   WebUI: http://localhost:$port"
        info "   密码:  见 config.yaml"
    else
        error "启动失败，请检查日志"
    fi
}

# ── Docker 部署 ──
deploy_docker() {
    if ! command -v docker >/dev/null; then
        error "未安装 Docker"
    fi
    info "Docker 部署..."
    docker compose up -d --build
    info "✅ BlockMind Docker 容器已启动"
    info "   WebUI: http://localhost:19951"
}

# ── 主流程 ──
main() {
    echo ""
    echo "  🧠 BlockMind 安装向导"
    echo "  ════════════════════"
    echo ""
    echo "  1) 本地部署（Python 直接运行）"
    echo "  2) Docker 部署"
    echo ""
    read -rp "  选择 [1/2]: " choice

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
            error "无效选择"
            ;;
    esac
}

main "$@"
