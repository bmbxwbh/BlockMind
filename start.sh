#!/usr/bin/env bash
# ═══════════════════════════════════════
# BlockMind — Unified Start Script
# Handles: Language, Python, Java, Dependencies, MC Server, Config, Startup
# ═══════════════════════════════════════
set -euo pipefail

# ── Colors ──
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
BOLD="\033[1m"
NC="\033[0m"

# ── Script directory ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ── MC server constants ──
DEFAULT_MC_VERSION="26.1.2"
FABRIC_INSTALLER_VER="1.1.1"
FABRIC_LOADER_VER="0.19.2"

# ── Process tracking ──
MC_PID=""
BLOCKMIND_PID=""

# ── Cleanup on exit ──
cleanup() {
    echo ""
    echo -e "${YELLOW}[*] Stopping all services...${NC}"
    
    # Stop BlockMind
    if [ -n "$BLOCKMIND_PID" ] && kill -0 "$BLOCKMIND_PID" 2>/dev/null; then
        kill "$BLOCKMIND_PID" 2>/dev/null
        wait "$BLOCKMIND_PID" 2>/dev/null || true
        echo -e "${GREEN}[✓] BlockMind stopped${NC}"
    fi
    
    # Stop MC server
    if [ -n "$MC_PID" ] && kill -0 "$MC_PID" 2>/dev/null; then
        kill "$MC_PID" 2>/dev/null
        wait "$MC_PID" 2>/dev/null || true
        echo -e "${GREEN}[✓] MC server stopped${NC}"
    fi
    
    echo -e "${GREEN}[✓] All services stopped${NC}"
    exit 0
}
trap cleanup EXIT SIGINT SIGTERM

# ── Language Selection ──
select_lang() {
    case "${BLOCKMIND_LANG:-${LANG:-}}" in
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
        T_TITLE="🧠 BlockMind 一键启动"
        T_PY_NOT_FOUND="未找到 Python 3.10+"
        T_JAVA_NOT="未找到 Java — MC 服务端将不会启动"
        T_INSTALL_DEPS="安装 Python 依赖..."
        T_CONFIG_CREATED="已创建 config.yaml，请编辑配置"
        T_MC_START="启动 Minecraft 服务端..."
        T_MC_STARTED="MC 服务端已启动"
        T_MC_SKIP_NOJAVA="跳过 MC 服务端（无 Java）"
        T_MC_SKIP_NOJAR="跳过 MC 服务端（未找到 JAR 文件）"
        T_MC_HINT="将自动下载并安装 Fabric"
        T_BLOCKMIND_START="启动 BlockMind 后端 + WebUI..."
        T_STOP="正在停止..."
        T_MC_STOPPED="MC 服务端已停止"
        T_EXITED="BlockMind 已退出"
        T_PRESS_CTRL="按 Ctrl+C 停止全部"
        T_MEMORY="内存"
        T_PID="PID"
        T_JAVA_VER="Java 版本"
        T_PYTHON_VER="Python 版本"
        T_VENV_CREATED="虚拟环境已创建"
        T_DEPS_INSTALLED="依赖已安装"
        T_CONFIG_EXISTS="config.yaml 已存在，跳过"
        T_MC_SERVER_SETUP="MC 服务端设置"
        T_MC_INSTALL_FABRIC="安装 Fabric 服务端..."
        T_MC_DL_INSTALLER="下载 Fabric 安装器..."
        T_MC_DL_DONE="下载完成"
        T_MC_INSTALL_DONE="安装完成"
        T_MC_DL_MOD="下载 BlockMind Mod..."
        T_MC_MOD_DONE="Mod 已下载"
        T_MC_MOD_FAIL="Mod 下载失败（可选），手动下载"
        T_MC_MOD_EXIST="BlockMind Mod 已存在"
        T_MC_DL_FABRIC_API="下载 Fabric API..."
        T_MC_FABRIC_API_DONE="Fabric API 已下载"
        T_MC_FABRIC_API_FAIL="Fabric API 下载失败，手动安装"
        T_SUMMARY_TITLE="启动摘要"
        T_WEBUI="WebUI"
        T_MC_SERVER="MC 服务端"
        T_RUNNING="运行中"
        T_SKIPPED="已跳过"
        T_READY="就绪"
        T_INSTALLED="BlockMind 已安装"
        T_START="启动 (Start)"
        T_REPAIR="修复 (Repair — reinstall dependencies)"
        T_REMOVE="卸载 (Remove — delete all data)"
        T_REINSTALL="重新安装 (Reinstall — remove + fresh install)"
        T_CONFIRM_REMOVE="确认删除所有数据？(y/N): "
        T_UNINSTALLED="已卸载"
        T_CANCEL_REMOVE="取消卸载"
        T_INSTALLING="正在安装..."
        T_SELECT_MODE="选择运行模式"
        T_MODE_SERVER="服务端模式 — 自动下载安装 MC 服务端"
        T_MODE_CLIENT="客户端模式 — 使用本地 Minecraft 客户端"
        T_CLIENT_HINT="请先从 PCL2 或官方启动器安装 Minecraft"
        T_CLIENT_HINT2="安装 BlockMind Mod 后放入 mods/ 目录"
        T_CLIENT_WEBUI="启动后访问 http://localhost:19951 控制"
        T_PCL2_URL="PCL2 下载: https://github.com/TCM-Corp/PCL/releases"
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
        T_MC_HINT="Will auto-download and install Fabric"
        T_BLOCKMIND_START="Starting BlockMind backend + WebUI..."
        T_STOP="Stopping..."
        T_MC_STOPPED="MC server stopped"
        T_EXITED="BlockMind exited"
        T_PRESS_CTRL="Press Ctrl+C to stop all"
        T_MEMORY="Memory"
        T_PID="PID"
        T_JAVA_VER="Java version"
        T_PYTHON_VER="Python version"
        T_VENV_CREATED="Virtual environment created"
        T_DEPS_INSTALLED="Dependencies installed"
        T_CONFIG_EXISTS="config.yaml exists, skipping"
        T_MC_SERVER_SETUP="MC Server Setup"
        T_MC_INSTALL_FABRIC="Installing Fabric server..."
        T_MC_DL_INSTALLER="Downloading Fabric installer..."
        T_MC_DL_DONE="Download complete"
        T_MC_INSTALL_DONE="Installation complete"
        T_MC_DL_MOD="Downloading BlockMind Mod..."
        T_MC_MOD_DONE="Mod downloaded"
        T_MC_MOD_FAIL="Mod download failed (optional), manual download"
        T_MC_MOD_EXIST="BlockMind Mod already exists"
        T_MC_DL_FABRIC_API="Downloading Fabric API..."
        T_MC_FABRIC_API_DONE="Fabric API downloaded"
        T_MC_FABRIC_API_FAIL="Fabric API download failed, install manually"
        T_SUMMARY_TITLE="Startup Summary"
        T_WEBUI="WebUI"
        T_MC_SERVER="MC Server"
        T_RUNNING="Running"
        T_SKIPPED="Skipped"
        T_READY="Ready"
        T_INSTALLED="BlockMind is already installed"
        T_START="Start"
        T_REPAIR="Repair — reinstall dependencies"
        T_REMOVE="Remove — delete all data"
        T_REINSTALL="Reinstall — remove + fresh install"
        T_CONFIRM_REMOVE="Confirm delete all data? (y/N): "
        T_UNINSTALLED="Uninstalled"
        T_CANCEL_REMOVE="Uninstall cancelled"
        T_INSTALLING="Installing..."
        T_SELECT_MODE="Select run mode"
        T_MODE_SERVER="Server mode — auto-download MC server"
        T_MODE_CLIENT="Client mode — use local Minecraft client"
        T_CLIENT_HINT="Install Minecraft via PCL2 or official launcher first"
        T_CLIENT_HINT2="Put BlockMind Mod into mods/ directory"
        T_CLIENT_WEBUI="Access http://localhost:19951 to control"
        T_PCL2_URL="PCL2 download: https://github.com/TCM-Corp/PCL/releases"
    fi
}

# ── Installation detection ──
INSTALL_MODE=""
detect_installation() {
    INSTALLED=false
    [ -d '.venv' ] && INSTALLED=true
    [ -f 'config.yaml' ] && INSTALLED=true
    [ -d 'data/memory' ] && INSTALLED=true
    [ -d 'mc-server' ] && INSTALLED=true

    if $INSTALLED; then
        echo ""
        echo -e "${CYAN}  ╔══════════════════════════════════════╗${NC}"
        echo -e "${CYAN}  ║   $T_INSTALLED          ║${NC}"
        echo -e "${CYAN}  ╚══════════════════════════════════════╝${NC}"
        echo ""
        echo "    1) $T_START"
        echo "    2) $T_REPAIR"
        echo "    3) $T_REMOVE"
        echo "    4) $T_REINSTALL"
        echo ""
        read -rp "  [1/2/3/4]: " install_choice
        case "${install_choice:-1}" in
            1) INSTALL_MODE="start" ;;
            2) INSTALL_MODE="repair" ;;
            3)
                read -rp "  $T_CONFIRM_REMOVE" confirm
                if [[ "$confirm" =~ ^[Yy]$ ]]; then
                    rm -rf .venv config.yaml data/ mc-server/
                    info "$T_UNINSTALLED"
                    exit 0
                else
                    info "$T_CANCEL_REMOVE"
                    detect_installation
                fi
                ;;
            4)
                read -rp "  $T_CONFIRM_REMOVE" confirm
                if [[ "$confirm" =~ ^[Yy]$ ]]; then
                    rm -rf .venv config.yaml data/ mc-server/
                    info "$T_UNINSTALLED"
                    INSTALL_MODE="install"
                else
                    info "$T_CANCEL_REMOVE"
                    detect_installation
                fi
                ;;
            *) INSTALL_MODE="start" ;;
        esac
    else
        INSTALL_MODE="install"
    fi
}

# ── Mode selection ──
RUN_MODE=""  # "server" or "client"

select_mode() {
    # If already installed and chose 'start', check if mc-server exists
    if [ "$INSTALL_MODE" = "start" ] && [ -d 'mc-server' ]; then
        RUN_MODE="server"
        return
    fi
    
    echo ""
    echo -e "${CYAN}  ╔══════════════════════════════════════╗${NC}"
    echo -e "${CYAN}  ║   $T_SELECT_MODE                       ║${NC}"
    echo -e "${CYAN}  ╚══════════════════════════════════════╝${NC}"
    echo ""
    echo "    1) $T_MODE_SERVER"
    echo "    2) $T_MODE_CLIENT"
    echo ""
    read -rp "  [1/2]: " mode_choice
    
    case "${mode_choice:-1}" in
        1) RUN_MODE="server" ;;
        2) RUN_MODE="client" ;;
        *) RUN_MODE="server" ;;
    esac
    
    if [ "$RUN_MODE" = "client" ]; then
        echo ""
        echo -e "  ${YELLOW}$T_CLIENT_HINT${NC}"
        echo -e "  ${YELLOW}$T_CLIENT_HINT2${NC}"
        echo -e "  ${YELLOW}$T_PCL2_URL${NC}"
        echo -e "  ${GREEN}$T_CLIENT_WEBUI${NC}"
        echo ""
        read -rp "  按回车继续... "
    fi
}

# ── Helper functions ──
info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

# ── Environment checks ──
check_python() {
    PYTHON=""
    for cmd in python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            # Check version >= 3.10
            PY_VER=$("$cmd" --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
            PY_MAJOR=$(echo "$PY_VER" | cut -d'.' -f1)
            PY_MINOR=$(echo "$PY_VER" | cut -d'.' -f2)
            if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
                PYTHON="$cmd"
                info "$T_PYTHON_VER: $("$PYTHON" --version 2>&1 | cut -d' ' -f2)"
                return 0
            fi
        fi
    done
    error "$T_PY_NOT_FOUND"
}

check_java() {
    HAS_JAVA=false
    JAVA_VER=""
    if command -v java >/dev/null 2>&1; then
        HAS_JAVA=true
        JAVA_VER=$(java -version 2>&1 | head -1 | cut -d'"' -f2)
        info "$T_JAVA_VER: $JAVA_VER"
    else
        warn "$T_JAVA_NOT"
    fi
}

# ── Python environment setup ──
setup_python_env() {
    VENV_DIR="$SCRIPT_DIR/.venv"
    PYTHON_IN_VENV="$VENV_DIR/bin/python3"
    
    if [ ! -f "$PYTHON_IN_VENV" ]; then
        info "Creating virtual environment..."
        $PYTHON -m venv "$VENV_DIR" 2>/dev/null || error "Failed to create virtual environment"
        info "$T_VENV_CREATED"
    fi
    
    source "$VENV_DIR/bin/activate" 2>/dev/null
    PYTHON="$PYTHON_IN_VENV"
}

# ── Install dependencies ──
install_dependencies() {
    # Skip if start mode (already installed)
    if [ "$INSTALL_MODE" = "start" ]; then
        info "$T_DEPS_INSTALLED (start mode, skipping)"
        return 0
    fi

    if [ "$INSTALL_MODE" = "repair" ] || ! $PYTHON -c "import fastapi" 2>/dev/null; then
        info "$T_INSTALL_DEPS"
        
        # Upgrade pip first
        $PYTHON -m pip install --upgrade pip -q 2>/dev/null || true
        
        # Detect mirror
        detect_pip_mirror
        
        # Install with progress
        echo -e "${CYAN}  Installing packages...${NC}"
        if [ "$INSTALL_MODE" = "repair" ]; then
            $PYTHON -m pip install --force-reinstall -r requirements.txt -q $PIP_MIRROR 2>/dev/null || \
            $PYTHON -m pip install --force-reinstall -r requirements.txt -q --break-system-packages $PIP_MIRROR 2>/dev/null || \
            $PYTHON -m pip install --force-reinstall -r requirements.txt $PIP_MIRROR || {
                error "Failed to install dependencies. Check your network connection."
            }
        else
            $PYTHON -m pip install -r requirements.txt -q $PIP_MIRROR 2>/dev/null || \
            $PYTHON -m pip install -r requirements.txt -q --break-system-packages $PIP_MIRROR 2>/dev/null || \
            $PYTHON -m pip install -r requirements.txt $PIP_MIRROR || {
                error "Failed to install dependencies. Check your network connection."
            }
        fi
        info "$T_DEPS_INSTALLED"
    else
        info "$T_DEPS_INSTALLED (already installed)"
    fi
}

# ── Detect pip mirror ──
detect_pip_mirror() {
    if curl -s --connect-timeout 3 "https://mirrors.aliyun.com/pypi/simple/" >/dev/null 2>&1; then
        PIP_MIRROR="--index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com"
        info "Using China mirror (Aliyun)"
    else
        PIP_MIRROR=""
        info "Using default PyPI"
    fi
}

# ── Initialize config ──
init_config() {
    if [ ! -f config.yaml ]; then
        cp config.example.yaml config.yaml
        warn "$T_CONFIG_CREATED"
    else
        info "$T_CONFIG_EXISTS"
    fi
}

# ── Create data directories ──
init_data() {
    mkdir -p data/{skills,logs,memory,backups}
}

# ── MC Server Setup ──
setup_mc_server() {
    MC_DIR="$SCRIPT_DIR/mc-server"
    
    if ! $HAS_JAVA; then
        warn "$T_MC_SKIP_NOJAVA"
        return 1
    fi
    
    echo ""
    echo -e "${CYAN}  ╔══════════════════════════════════════╗${NC}"
    echo -e "${CYAN}  ║   $T_MC_SERVER_SETUP                   ║${NC}"
    echo -e "${CYAN}  ╚══════════════════════════════════════╝${NC}"
    echo ""
    
    # Check if Fabric is already installed
    if [ -f "$MC_DIR/fabric-server-launch.jar" ]; then
        info "Fabric server already installed at $MC_DIR"
        return 0
    fi
    
    # Check if we have a vanilla server
    if [ -f "$MC_DIR/server.jar" ]; then
        info "Vanilla server found at $MC_DIR"
        return 0
    fi
    
    # No server found, install Fabric
    info "No MC server found. Installing Fabric $DEFAULT_MC_VERSION..."
    
    mkdir -p "$MC_DIR"
    
    # Download Fabric installer
    INSTALLER="$MC_DIR/fabric-installer.jar"
    if [ ! -f "$INSTALLER" ]; then
        info "$T_MC_DL_INSTALLER"
        URL="https://maven.fabricmc.net/net/fabricmc/fabric-installer/${FABRIC_INSTALLER_VER}/fabric-installer-${FABRIC_INSTALLER_VER}.jar"
        curl -L -o "$INSTALLER" "$URL" || error "Download failed: $URL"
        info "$T_MC_DL_DONE"
    fi
    
    # Install Fabric server
    if [ ! -f "$MC_DIR/fabric-server-launch.jar" ]; then
        info "$T_MC_INSTALL_FABRIC (MC $DEFAULT_MC_VERSION)..."
        java -jar "$INSTALLER" server -dir "$MC_DIR" -mcversion "$DEFAULT_MC_VERSION" -loader "$FABRIC_LOADER_VER" -downloadMinecraft
        info "$T_MC_INSTALL_DONE"
    fi
    
    # Download BlockMind Mod
    download_blockmind_mod
    
    # Download Fabric API
    download_fabric_api
    
    return 0
}

# ── Download BlockMind Mod ──
download_blockmind_mod() {
    MODS_DIR="$MC_DIR/mods"
    mkdir -p "$MODS_DIR"
    
    if ls "$MODS_DIR"/blockmind-mod-*.jar >/dev/null 2>&1; then
        info "$T_MC_MOD_EXIST"
        return 0
    fi
    
    info "$T_MC_DL_MOD"
    
    # Try to get latest mod URL from GitHub API
    MOD_URL=""
    RELEASE_JSON=$(curl -sL --connect-timeout 10 "https://api.github.com/repos/bmbxwbh/BlockMind/releases/latest" 2>/dev/null)
    if echo "$RELEASE_JSON" | grep -q "browser_download_url"; then
        # Try to match current MC version
        MOD_URL=$(echo "$RELEASE_JSON" | grep -o '"browser_download_url": "[^"]*blockmind-mod-'"$DEFAULT_MC_VERSION"'[^"]*"' | head -1 | cut -d'"' -f4)
        # Fallback to any blockmind-mod
        if [ -z "$MOD_URL" ]; then
            MOD_URL=$(echo "$RELEASE_JSON" | grep -o '"browser_download_url": "[^"]*blockmind-mod[^"]*"' | head -1 | cut -d'"' -f4)
        fi
    fi
    
    # Fallback: construct URL from latest tag
    if [ -z "$MOD_URL" ]; then
        LATEST_TAG=$(curl -sL --connect-timeout 10 "https://api.github.com/repos/bmbxwbh/BlockMind/releases/latest" 2>/dev/null | grep -o '"tag_name": "[^"]*"' | head -1 | cut -d'"' -f4)
        if [ -n "$LATEST_TAG" ]; then
            MOD_URL="https://github.com/bmbxwbh/BlockMind/releases/download/${LATEST_TAG}/blockmind-mod-${DEFAULT_MC_VERSION}.jar"
        else
            MOD_URL="https://github.com/bmbxwbh/BlockMind/releases/latest/download/blockmind-mod-${DEFAULT_MC_VERSION}.jar"
        fi
    fi
    
    curl -sL --connect-timeout 10 -o "$MODS_DIR/blockmind-mod-${DEFAULT_MC_VERSION}.jar" "$MOD_URL" && \
    info "$T_MC_MOD_DONE" || \
    warn "$T_MC_MOD_FAIL: https://github.com/bmbxwbh/BlockMind/releases"
}

# ── Download Fabric API ──
download_fabric_api() {
    MODS_DIR="$MC_DIR/mods"
    
    if ls "$MODS_DIR"/fabric-api-*.jar >/dev/null 2>&1; then
        info "Fabric API already exists"
        return 0
    fi
    
    info "$T_MC_DL_FABRIC_API"
    
    # Get latest compatible version from Modrinth
    FABRIC_API_URL=$(curl -sL --connect-timeout 15 \
        "https://api.modrinth.com/v2/project/P7dR8mSH/version?game_versions=%5B%22${DEFAULT_MC_VERSION}%22%5D&loaders=%5B%22fabric%22%5D" 2>/dev/null | \
        python3 -c "import sys,json; print(json.load(sys.stdin)[0]['files'][0]['url'])" 2>/dev/null)
    
    if [ -n "$FABRIC_API_URL" ]; then
        FABRIC_API_FILE=$(basename "$FABRIC_API_URL" | python3 -c "import sys,urllib.parse; print(urllib.parse.unquote(sys.stdin.read().strip()))")
        curl -sL --connect-timeout 15 -o "$MODS_DIR/$FABRIC_API_FILE" "$FABRIC_API_URL" && \
            info "$T_MC_FABRIC_API_DONE" || \
            warn "$T_MC_FABRIC_API_FAIL"
    else
        warn "Could not find Fabric API for MC $DEFAULT_MC_VERSION, install manually from https://modrinth.com/mod/fabric-api"
    fi
}

# ── Start MC Server ──
start_mc_server() {
    if ! $HAS_JAVA; then
        return 1
    fi
    
    MC_DIR="$SCRIPT_DIR/mc-server"
    
    # Check for launch jar
    LAUNCH_JAR=""
    if [ -f "$MC_DIR/fabric-server-launch.jar" ]; then
        LAUNCH_JAR="fabric-server-launch.jar"
    elif [ -f "$MC_DIR/server.jar" ]; then
        LAUNCH_JAR="server.jar"
    else
        warn "$T_MC_SKIP_NOJAR"
        return 1
    fi
    
    info "$T_MC_START"
    
    # Create eula.txt if needed
    [ ! -f "$MC_DIR/eula.txt" ] && echo "eula=true" > "$MC_DIR/eula.txt"
    
    # Auto-detect memory
    TOTAL_MEM_KB=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}')
    if [ -n "$TOTAL_MEM_KB" ] && [ "$TOTAL_MEM_KB" -gt 8000000 ]; then
        MAX_RAM="4G"
    else
        MAX_RAM="2G"
    fi
    
    cd "$MC_DIR"
    java -Xms512M -Xmx"$MAX_RAM" -jar "$LAUNCH_JAR" nogui &
    MC_PID=$!
    cd "$SCRIPT_DIR"
    
    info "$T_MC_STARTED (${T_PID}: $MC_PID, ${T_MEMORY}: $MAX_RAM)"
    sleep 3
    return 0
}

# ── Show startup summary ──
show_summary() {
    echo ""
    echo -e "${CYAN}  ╔══════════════════════════════════════╗${NC}"
    echo -e "${CYAN}  ║   $T_SUMMARY_TITLE                     ║${NC}"
    echo -e "${CYAN}  ╠══════════════════════════════════════╣${NC}"
    echo -e "${CYAN}  ║   $T_WEBUI:  http://localhost:19951   ║${NC}"
    
    if [ "$RUN_MODE" = "server" ]; then
        if [ -n "$MC_PID" ] && kill -0 "$MC_PID" 2>/dev/null; then
            echo -e "${CYAN}  ║   $T_MC_SERVER: $T_RUNNING (PID: $MC_PID)    ║${NC}"
        else
            echo -e "${CYAN}  ║   $T_MC_SERVER: $T_SKIPPED               ║${NC}"
        fi
    else
        echo -e "${CYAN}  ║   模式: 客户端 (请自行启动 Minecraft)   ║${NC}"
    fi
    
    echo -e "${CYAN}  ║   $T_PRESS_CTRL               ║${NC}"
    echo -e "${CYAN}  ╚══════════════════════════════════════╝${NC}"
    echo ""
}

# ── Main ──
main() {
    select_lang
    load_strings
    
    echo ""
    echo -e "${CYAN}  ╔══════════════════════════════════════╗${NC}"
    echo -e "${CYAN}  ║   $T_TITLE                            ║${NC}"
    echo -e "${CYAN}  ╚══════════════════════════════════════╝${NC}"
    echo ""
    
    # Check if already installed
    detect_installation
    
    # Select run mode
    select_mode
    
    # Step 1: Check Python
    check_python
    
    # Step 2: Check Java
    check_java
    
    # Step 3: Setup Python environment
    setup_python_env
    
    # Step 4: Install dependencies
    install_dependencies
    
    # Step 5: Initialize config
    init_config
    
    # Step 6: Create data directories
    init_data
    
    # Step 7: Setup & Start MC server (if server mode)
    if [ "$RUN_MODE" = "server" ]; then
        setup_mc_server || true
        start_mc_server || true
    else
        warn "$T_MC_SKIP_NOJAR"
    fi
    
    # Step 9: Show summary
    show_summary
    
    # Step 10: Start BlockMind (foreground)
    info "$T_BLOCKMIND_START"
    $PYTHON -m src.main &
    BLOCKMIND_PID=$!
    
    # Wait for BlockMind to exit
    wait $BLOCKMIND_PID 2>/dev/null || true
}

main "$@"