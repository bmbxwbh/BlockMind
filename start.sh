#!/usr/bin/env bash
# ═══════════════════════════════════════
# BlockMind — 一键启动 (MC 服务端 + BlockMind + WebUI)
# ═══════════════════════════════════════
set -euo pipefail

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
NC="\033[0m"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

MC_DIR="$SCRIPT_DIR/mc-server"
MC_VERSION="1.20.4"
FABRIC_VERSION="0.15.3"

info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

echo ""
echo -e "${CYAN}  ╔══════════════════════════════════════╗${NC}"
echo -e "${CYAN}  ║   🧠 BlockMind 一键启动               ║${NC}"
echo -e "${CYAN}  ╚══════════════════════════════════════╝${NC}"
echo ""

# ── 检查 Python ──
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        PYTHON="$cmd"
        break
    fi
done
[ -z "$PYTHON" ] && error "未找到 Python 3.10+"
info "Python $($PYTHON --version 2>&1 | cut -d' ' -f2)"

# ── 检查 Java ──
HAS_JAVA=false
if command -v java >/dev/null 2>&1; then
    HAS_JAVA=true
    JAVA_VER=$(java -version 2>&1 | head -1 | cut -d'"' -f2)
    info "Java $JAVA_VER"
else
    warn "未找到 Java — MC 服务端将不会启动"
fi

# ── 安装依赖（如果需要） ──
if ! $PYTHON -c "import fastapi" 2>/dev/null; then
    info "安装 Python 依赖..."
    $PYTHON -m pip install -r requirements.txt -q
fi

# ── 初始化配置 ──
if [ ! -f config.yaml ]; then
    cp config.example.yaml config.yaml
    warn "已创建 config.yaml，请编辑配置"
fi

# ── 创建数据目录 ──
mkdir -p data/{skills,logs,memory,backups}

# ══════════════════════════════════════
# 启动 MC 服务端（后台）
# ══════════════════════════════════════
MC_PID=""
if $HAS_JAVA && [ -f "$MC_DIR/fabric-server-launch.jar" ]; then
    info "启动 Minecraft 服务端..."
    mkdir -p "$MC_DIR"
    [ ! -f "$MC_DIR/eula.txt" ] && echo "eula=true" > "$MC_DIR/eula.txt"

    # 自动检测内存
    TOTAL_MEM_KB=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}')
    if [ -n "$TOTAL_MEM_KB" ] && [ "$TOTAL_MEM_KB" -gt 8000000 ]; then
        MAX_RAM="4G"
    else
        MAX_RAM="2G"
    fi

    cd "$MC_DIR"
    java -Xms512M -Xmx"$MAX_RAM" -jar fabric-server-launch.jar nogui &
    MC_PID=$!
    cd "$SCRIPT_DIR"
    info "MC 服务端已启动 (PID: $MC_PID, 内存: $MAX_RAM)"
    sleep 3
else
    if ! $HAS_JAVA; then
        warn "跳过 MC 服务端（无 Java）"
    else
        warn "跳过 MC 服务端（未找到 $MC_DIR/fabric-server-launch.jar）"
        warn "运行 start_mc.sh 自动下载安装"
    fi
fi

# ══════════════════════════════════════
# 启动 BlockMind（前台）
# ══════════════════════════════════════
echo ""
info "启动 BlockMind 后端 + WebUI..."
info "WebUI: http://localhost:19951"
info "按 Ctrl+C 停止全部"
echo ""

# 优雅退出
cleanup() {
    echo ""
    warn "正在停止..."
    [ -n "$MC_PID" ] && kill "$MC_PID" 2>/dev/null && info "MC 服务端已停止"
    info "BlockMind 已退出"
    exit 0
}
trap cleanup SIGINT SIGTERM

# 启动 BlockMind
$PYTHON -m src.main

# 如果 BlockMind 退出，也停止 MC
cleanup
