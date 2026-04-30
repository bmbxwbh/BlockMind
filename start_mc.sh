#!/usr/bin/env bash
# ═══════════════════════════════════════
# BlockMind — MC Server Auto-install + Start
# Supports version selection + auto-detect existing servers
# ═══════════════════════════════════════
set -euo pipefail

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
NC="\033[0m"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

DEFAULT_MC_VERSION="1.20.4"
FABRIC_VERSION="0.15.3"

info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

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
        T_TITLE="🎮 Minecraft 服务端配置"
        T_NO_JAVA="未找到 Java 17+，请先安装"
        T_SCAN="扫描已有服务端..."
        T_FOUND_FABRIC="Fabric"
        T_FOUND_VANILLA="Vanilla"
        T_PORT_WARN="端口 25565 已被占用（可能有其他 MC 服务端在运行）"
        T_PORT_PROC="占用的进程:"
        T_CONTINUE="继续启动？可能会端口冲突 [y/N]"
        T_DETECT="检测到已有服务端："
        T_MOD_COUNT="个mod"
        T_INSTALL_NEW="安装新的服务端"
        T_CHOOSE="选择"
        T_USE_EXISTING="使用已有服务端"
        T_VERSIONS="可选版本："
        T_VER_LATEST="最新"
        T_VER_RECOMMEND="推荐"
        T_VER_CUSTOM="自定义版本号"
        T_CHOOSE_VER="选择 [1-8]"
        T_INPUT_VER="输入版本号"
        T_CHOSEN_VER="选择版本"
        T_INSTALL_DIR="安装目录"
        T_DL_INSTALLER="下载 Fabric 安装器..."
        T_DL_DONE="下载完成"
        T_INSTALL_FABRIC="安装 Fabric 服务端"
        T_INSTALL_DONE="安装完成"
        T_DL_MOD="下载 BlockMind Mod..."
        T_MOD_DONE="Mod 已下载"
        T_MOD_FAIL="Mod 下载失败（可选），手动下载"
        T_MOD_EXIST="BlockMind Mod 已存在"
        T_LAUNCH_TITLE="启动 Minecraft 服务端"
        T_DIR="目录"
        T_JAR="JAR"
        T_MEMORY="内存"
        T_PRESS_STOP="按 Ctrl+C 停止"
    else
        T_TITLE="🎮 Minecraft Server Setup"
        T_NO_JAVA="Java 17+ not found, please install"
        T_SCAN="Scanning existing servers..."
        T_FOUND_FABRIC="Fabric"
        T_FOUND_VANILLA="Vanilla"
        T_PORT_WARN="Port 25565 already in use (another MC server may be running)"
        T_PORT_PROC="Process using port:"
        T_CONTINUE="Continue? May cause port conflict [y/N]"
        T_DETECT="Detected existing servers:"
        T_MOD_COUNT="mods"
        T_INSTALL_NEW="Install new server"
        T_CHOOSE="Choose"
        T_USE_EXISTING="Using existing server"
        T_VERSIONS="Available versions:"
        T_VER_LATEST="latest"
        T_VER_RECOMMEND="recommended"
        T_VER_CUSTOM="Custom version"
        T_CHOOSE_VER="Choose [1-8]"
        T_INPUT_VER="Enter version (e.g. 1.20.4)"
        T_CHOSEN_VER="Selected version"
        T_INSTALL_DIR="Install directory"
        T_DL_INSTALLER="Downloading Fabric installer..."
        T_DL_DONE="Download complete"
        T_INSTALL_FABRIC="Installing Fabric server"
        T_INSTALL_DONE="Installation complete"
        T_DL_MOD="Downloading BlockMind Mod..."
        T_MOD_DONE="Mod downloaded"
        T_MOD_FAIL="Mod download failed (optional), manual download"
        T_MOD_EXIST="BlockMind Mod already exists"
        T_LAUNCH_TITLE="Starting Minecraft Server"
        T_DIR="Directory"
        T_JAR="JAR"
        T_MEMORY="Memory"
        T_PRESS_STOP="Press Ctrl+C to stop"
    fi
}

# ── Main Flow ──
select_lang
load_strings

# ── 检查 Java ──
command -v java >/dev/null 2>&1 || error "${T_NO_JAVA}: https://adoptium.net/"
info "Java $(java -version 2>&1 | head -1 | cut -d'"' -f2)"

# ══════════════════════════════════════
# 第一步：检测已有 MC 服务端
# ══════════════════════════════════════
echo ""
echo -e "${CYAN}  ╔══════════════════════════════════════╗${NC}"
echo -e "${CYAN}  ║   ${T_TITLE}              ║${NC}"
echo -e "${CYAN}  ╚══════════════════════════════════════╝${NC}"
echo ""

DETECTED_SERVERS=()

# 扫描常见位置
SCAN_DIRS=(
    "$SCRIPT_DIR/mc-server"
    "$SCRIPT_DIR/server"
    "$SCRIPT_DIR/minecraft-server"
    "$HOME/mc-server"
    "$HOME/minecraft-server"
    "$HOME/Desktop/mc-server"
)

echo "  ${T_SCAN}"
for dir in "${SCAN_DIRS[@]}"; do
    if [ -f "$dir/fabric-server-launch.jar" ]; then
        DETECTED_SERVERS+=("$dir")
        echo -e "    ${GREEN}✓${NC} $dir (${T_FOUND_FABRIC})"
    elif [ -f "$dir/server.jar" ]; then
        DETECTED_SERVERS+=("$dir")
        echo -e "    ${GREEN}✓${NC} $dir (${T_FOUND_VANILLA})"
    fi
done

# 也检查当前目录下所有子目录
for dir in "$SCRIPT_DIR"/*/; do
    dir="${dir%/}"
    [ -f "$dir/fabric-server-launch.jar" ] && [[ ! " ${DETECTED_SERVERS[*]} " =~ " $dir " ]] && DETECTED_SERVERS+=("$dir") && echo -e "    ${GREEN}✓${NC} $dir (${T_FOUND_FABRIC})"
    [ -f "$dir/server.jar" ] && [[ ! " ${DETECTED_SERVERS[*]} " =~ " $dir " ]] && DETECTED_SERVERS+=("$dir") && echo -e "    ${GREEN}✓${NC} $dir (${T_FOUND_VANILLA})"
done

# 检查端口 25565 是否已被占用
if ss -tlnp 2>/dev/null | grep -q ":25565 " || netstat -tlnp 2>/dev/null | grep -q ":25565 "; then
    echo ""
    warn "${T_PORT_WARN}"
    warn "${T_PORT_PROC}"
    ss -tlnp 2>/dev/null | grep ":25565 " || netstat -tlnp 2>/dev/null | grep ":25565 " || true
    echo ""
    read -rp "  ${T_CONTINUE}: " yn
    [[ ! "$yn" =~ ^[Yy] ]] && exit 0
fi

echo ""

# ══════════════════════════════════════
# 第二步：选择服务端
# ══════════════════════════════════════
MC_DIR=""
USE_EXISTING=false

if [ ${#DETECTED_SERVERS[@]} -gt 0 ]; then
    echo "  ${T_DETECT}"
    echo ""
    for i in "${!DETECTED_SERVERS[@]}"; do
        dir="${DETECTED_SERVERS[$i]}"
        # 检测版本
        ver=""
        [ -f "$dir/fabric-server-launch.jar" ] && ver="${T_FOUND_FABRIC}"
        [ -f "$dir/server.jar" ] && ver="${T_FOUND_VANILLA}"
        # 检测 mods 目录
        mod_count=0
        [ -d "$dir/mods" ] && mod_count=$(ls "$dir/mods"/*.jar 2>/dev/null | wc -l)
        echo "    $((i+1))) $dir  ($ver, ${mod_count}${T_MOD_COUNT})"
    done
    echo "    0) ${T_INSTALL_NEW}"
    echo ""
    read -rp "  ${T_CHOOSE} [0-${#DETECTED_SERVERS[@]}]: " choice

    if [ "$choice" -gt 0 ] 2>/dev/null && [ "$choice" -le "${#DETECTED_SERVERS[@]}" ] 2>/dev/null; then
        MC_DIR="${DETECTED_SERVERS[$((choice-1))]}"
        USE_EXISTING=true
        info "${T_USE_EXISTING}: $MC_DIR"
    fi
fi

# ══════════════════════════════════════
# 第三步：选择版本（仅新安装时）
# ══════════════════════════════════════
MC_VERSION="$DEFAULT_MC_VERSION"

if [ "$USE_EXISTING" = false ]; then
    echo ""
    echo "  ${T_VERSIONS}"
    echo "    1) 1.21.4  (${T_VER_LATEST})"
    echo "    2) 1.21.3"
    echo "    3) 1.21.1"
    echo "    4) 1.20.6"
    echo "    5) 1.20.4  (${T_VER_RECOMMEND})"
    echo "    6) 1.20.1"
    echo "    7) 1.19.4"
    echo "    8) ${T_VER_CUSTOM}"
    echo ""
    read -rp "  ${T_CHOOSE_VER} (默认5): " ver_choice

    case "${ver_choice:-5}" in
        1) MC_VERSION="1.21.4" ;;
        2) MC_VERSION="1.21.3" ;;
        3) MC_VERSION="1.21.1" ;;
        4) MC_VERSION="1.20.6" ;;
        5) MC_VERSION="1.20.4" ;;
        6) MC_VERSION="1.20.1" ;;
        7) MC_VERSION="1.19.4" ;;
        8) read -rp "  ${T_INPUT_VER} (如 1.20.4): " MC_VERSION ;;
        *) MC_VERSION="$DEFAULT_MC_VERSION" ;;
    esac

    echo ""
    info "${T_CHOSEN_VER}: MC $MC_VERSION"

    # 服务端目录
    MC_DIR="$SCRIPT_DIR/mc-server"
    echo ""
    read -rp "  ${T_INSTALL_DIR} (默认: $MC_DIR): " custom_dir
    [ -n "$custom_dir" ] && MC_DIR="$custom_dir"

    mkdir -p "$MC_DIR"
fi

# ══════════════════════════════════════
# 第四步：下载+安装（仅新安装时）
# ══════════════════════════════════════
if [ "$USE_EXISTING" = false ]; then
    # 下载 Fabric 安装器
    INSTALLER="$MC_DIR/fabric-installer.jar"
    if [ ! -f "$INSTALLER" ]; then
        info "${T_DL_INSTALLER}"
        URL="https://maven.fabricmc.net/net/fabricmc/fabric-installer/${FABRIC_VERSION}/fabric-installer-${FABRIC_VERSION}.jar"
        curl -L -o "$INSTALLER" "$URL" || error "Download failed: $URL"
        info "${T_DL_DONE}"
    fi

    # 安装 Fabric 服务端
    if [ ! -f "$MC_DIR/fabric-server-launch.jar" ]; then
        info "${T_INSTALL_FABRIC} (MC $MC_VERSION)..."
        java -jar "$INSTALLER" server -dir "$MC_DIR" -mcversion "$MC_VERSION" -loader "$FABRIC_VERSION" -downloadMinecraft
        info "${T_INSTALL_DONE}"
    fi
fi

# ══════════════════════════════════════
# 第五步：下载 BlockMind Mod
# ══════════════════════════════════════
MODS_DIR="$MC_DIR/mods"
mkdir -p "$MODS_DIR"

if ! ls "$MODS_DIR"/blockmind-mod-*.jar >/dev/null 2>&1; then
    info "${T_DL_MOD}"
    RELEASE_JSON=$(curl -sL "https://api.github.com/repos/bmbxwbh/BlockMind/releases/latest")
    MOD_URL=$(echo "$RELEASE_JSON" | grep -o '"browser_download_url": "[^"]*blockmind-mod[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$MOD_URL" ]; then
        curl -L -o "$MODS_DIR/blockmind-mod.jar" "$MOD_URL"
        info "${T_MOD_DONE}"
    else
        warn "${T_MOD_FAIL}: https://github.com/bmbxwbh/BlockMind/releases"
    fi
else
    info "${T_MOD_EXIST}"
fi

# ══════════════════════════════════════
# 第六步：启动
# ══════════════════════════════════════
[ ! -f "$MC_DIR/eula.txt" ] && echo "eula=true" > "$MC_DIR/eula.txt"

# 内存配置
TOTAL_MEM_KB=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}')
if [ -n "$TOTAL_MEM_KB" ] && [ "$TOTAL_MEM_KB" -gt 8000000 ]; then
    MAX_RAM="4G"
else
    MAX_RAM="2G"
fi

# 确定启动命令
LAUNCH_JAR=""
if [ -f "$MC_DIR/fabric-server-launch.jar" ]; then
    LAUNCH_JAR="fabric-server-launch.jar"
elif [ -f "$MC_DIR/server.jar" ]; then
    LAUNCH_JAR="server.jar"
else
    error "JAR not found"
fi

cd "$MC_DIR"
echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   🎮 ${T_LAUNCH_TITLE}           ║"
echo "  ╠══════════════════════════════════════╣"
echo "  ║   ${T_DIR}: $MC_DIR"
echo "  ║   ${T_JAR}:  $LAUNCH_JAR"
echo "  ║   ${T_MEMORY}: $MAX_RAM"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  ${T_PRESS_STOP}"
echo ""

exec java -Xms512M -Xmx"$MAX_RAM" -jar "$LAUNCH_JAR" nogui
