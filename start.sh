#!/usr/bin/env bash
# ═══════════════════════════════════════
# BlockMind — One-click Start (MC + WebUI)
# ═══════════════════════════════════════
set -euo pipefail

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
NC="\033[0m"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ── Language Selection ──
select_lang() {
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

load_strings() {
    if [ "$BM_LANG" = "zh" ]; then
        T_TITLE="🧠 BlockMind 一键启动"
        T_PY_NOT_FOUND="未找到 Python 3.10+"
        T_JAVA_NOT="未找到 Java — MC 服务端将不会启动"
        T_INSTALL_DEPS="安装 Python 依赖..."
        T_CONFIG_CREATED="已创建 config.yaml，请编辑配置"
        T_MC_START="启动 Minecraft 服务端..."
        T_MC_STARTED="MC 服务端已启动"
        T_MC_SKIP_NOJAVA="跳过 MC 服务端（无 Java）"
        T_MC_SKIP_NOJAR="跳过 MC 服务端（未找到 JAR 文件）"
        T_MC_HINT="运行 start_mc.sh 自动下载安装"
        T_BLOCKMIND_START="启动 BlockMind 后端 + WebUI..."
        T_STOP="正在停止..."
        T_MC_STOPPED="MC 服务端已停止"
        T_EXITED="BlockMind 已退出"
        T_PRESS_CTRL="按 Ctrl+C 停止全部"
        T_MEMORY="内存"
        T_PID="PID"
    else
        T_TITLE="🧠 BlockMind One-click Start"
        T_PY_NOT_FOUND="Python 3.10+ not found"
        T_JAVA_NOT="Java not found — MC server will not start"
        T_INSTALL_DEPS="Installing Python dependencies..."
        T_CONFIG_CREATED="config.yaml created, please edit config"
        T_MC_START="Starting Minecraft server..."
        T_MC_STARTED="MC server started"
        T_MC_SKIP_NOJAVA="Skipping MC server (no Java)"
        T_MC_SKIP_NOJAR="Skipping MC server (JAR not found)"
        T_MC_HINT="Run start_mc.sh to auto-install"
        T_BLOCKMIND_START="Starting BlockMind backend + WebUI..."
        T_STOP="Stopping..."
        T_MC_STOPPED="MC server stopped"
        T_EXITED="BlockMind exited"
        T_PRESS_CTRL="Press Ctrl+C to stop all"
        T_MEMORY="Memory"
        T_PID="PID"
    fi
}

info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

# ── Main ──
select_lang
load_strings

MC_DIR="$SCRIPT_DIR/mc-server"

echo ""
echo -e "${CYAN}  ╔══════════════════════════════════════╗${NC}"
echo -e "${CYAN}  ║   ${T_TITLE}          ║${NC}"
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
[ -z "$PYTHON" ] && error "${T_PY_NOT_FOUND}"
info "Python $($PYTHON --version 2>&1 | cut -d' ' -f2)"

# ── 检查 Java ──
HAS_JAVA=false
if command -v java >/dev/null 2>&1; then
    HAS_JAVA=true
    JAVA_VER=$(java -version 2>&1 | head -1 | cut -d'"' -f2)
    info "Java $JAVA_VER"
else
    warn "${T_JAVA_NOT}"
fi

# ── 安装依赖（如果需要） ──
if ! $PYTHON -c "import fastapi" 2>/dev/null; then
    info "${T_INSTALL_DEPS}"
    $PYTHON -m pip install -r requirements.txt -q
fi

# ── 初始化配置 ──
if [ ! -f config.yaml ]; then
    cp config.example.yaml config.yaml
    warn "${T_CONFIG_CREATED}"
fi

# ── 创建数据目录 ──
mkdir -p data/{skills,logs,memory,backups}

# ══════════════════════════════════════
# 启动 MC 服务端（后台）
# ══════════════════════════════════════
MC_PID=""
if $HAS_JAVA && [ -f "$MC_DIR/fabric-server-launch.jar" ]; then
    info "${T_MC_START}"
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
    info "${T_MC_STARTED} (${T_PID}: $MC_PID, ${T_MEMORY}: $MAX_RAM)"
    sleep 3
else
    if ! $HAS_JAVA; then
        warn "${T_MC_SKIP_NOJAVA}"
    else
        warn "${T_MC_SKIP_NOJAR}"
        warn "${T_MC_HINT}"
    fi
fi

# ══════════════════════════════════════
# 启动 BlockMind（前台）
# ══════════════════════════════════════
echo ""
info "${T_BLOCKMIND_START}"
info "WebUI: http://localhost:19951"
info "${T_PRESS_CTRL}"
echo ""

# 优雅退出
cleanup() {
    echo ""
    warn "${T_STOP}"
    [ -n "$MC_PID" ] && kill "$MC_PID" 2>/dev/null && info "${T_MC_STOPPED}"
    info "${T_EXITED}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# 启动 BlockMind
$PYTHON -m src.main

# 如果 BlockMind 退出，也停止 MC
cleanup
