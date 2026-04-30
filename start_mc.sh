#!/usr/bin/env bash
# ═══════════════════════════════════════
# BlockMind — MC 服务端自动安装+启动 (Linux)
# 支持自选版本 + 自动检测已有服务端
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

# ── 检查 Java ──
command -v java >/dev/null 2>&1 || error "未找到 Java 17+，请先安装: https://adoptium.net/"
info "Java $(java -version 2>&1 | head -1 | cut -d'"' -f2)"

# ══════════════════════════════════════
# 第一步：检测已有 MC 服务端
# ══════════════════════════════════════
echo ""
echo -e "${CYAN}  ╔══════════════════════════════════════╗${NC}"
echo -e "${CYAN}  ║   🎮 Minecraft 服务端配置              ║${NC}"
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

echo "  扫描已有服务端..."
for dir in "${SCAN_DIRS[@]}"; do
    if [ -f "$dir/fabric-server-launch.jar" ]; then
        DETECTED_SERVERS+=("$dir")
        echo -e "    ${GREEN}✓${NC} $dir (Fabric)"
    elif [ -f "$dir/server.jar" ]; then
        DETECTED_SERVERS+=("$dir")
        echo -e "    ${GREEN}✓${NC} $dir (Vanilla)"
    fi
done

# 也检查当前目录下所有子目录
for dir in "$SCRIPT_DIR"/*/; do
    dir="${dir%/}"
    [ -f "$dir/fabric-server-launch.jar" ] && [[ ! " ${DETECTED_SERVERS[*]} " =~ " $dir " ]] && DETECTED_SERVERS+=("$dir") && echo -e "    ${GREEN}✓${NC} $dir (Fabric)"
    [ -f "$dir/server.jar" ] && [[ ! " ${DETECTED_SERVERS[*]} " =~ " $dir " ]] && DETECTED_SERVERS+=("$dir") && echo -e "    ${GREEN}✓${NC} $dir (Vanilla)"
done

# 检查端口 25565 是否已被占用
if ss -tlnp 2>/dev/null | grep -q ":25565 " || netstat -tlnp 2>/dev/null | grep -q ":25565 "; then
    echo ""
    warn "端口 25565 已被占用（可能有其他 MC 服务端在运行）"
    warn "占用的进程:"
    ss -tlnp 2>/dev/null | grep ":25565 " || netstat -tlnp 2>/dev/null | grep ":25565 " || true
    echo ""
    read -rp "  继续启动？可能会端口冲突 [y/N]: " yn
    [[ ! "$yn" =~ ^[Yy] ]] && exit 0
fi

echo ""

# ══════════════════════════════════════
# 第二步：选择服务端
# ══════════════════════════════════════
MC_DIR=""
USE_EXISTING=false

if [ ${#DETECTED_SERVERS[@]} -gt 0 ]; then
    echo "  检测到已有服务端："
    echo ""
    for i in "${!DETECTED_SERVERS[@]}"; do
        dir="${DETECTED_SERVERS[$i]}"
        # 检测版本
        ver="未知"
        [ -f "$dir/fabric-server-launch.jar" ] && ver="Fabric"
        [ -f "$dir/server.jar" ] && ver="Vanilla"
        # 检测 mods 目录
        mod_count=0
        [ -d "$dir/mods" ] && mod_count=$(ls "$dir/mods"/*.jar 2>/dev/null | wc -l)
        echo "    $((i+1))) $dir  ($ver, ${mod_count}个mod)"
    done
    echo "    0) 安装新的服务端"
    echo ""
    read -rp "  选择 [0-${#DETECTED_SERVERS[@]}]: " choice

    if [ "$choice" -gt 0 ] 2>/dev/null && [ "$choice" -le "${#DETECTED_SERVERS[@]}" ] 2>/dev/null; then
        MC_DIR="${DETECTED_SERVERS[$((choice-1))]}"
        USE_EXISTING=true
        info "使用已有服务端: $MC_DIR"
    fi
fi

# ══════════════════════════════════════
# 第三步：选择版本（仅新安装时）
# ══════════════════════════════════════
MC_VERSION="$DEFAULT_MC_VERSION"

if [ "$USE_EXISTING" = false ]; then
    echo ""
    echo "  可选版本："
    echo "    1) 1.21.4  (最新)"
    echo "    2) 1.21.3"
    echo "    3) 1.21.1"
    echo "    4) 1.20.6"
    echo "    5) 1.20.4  (推荐，BlockMind 默认)"
    echo "    6) 1.20.1"
    echo "    7) 1.19.4"
    echo "    8) 自定义版本号"
    echo ""
    read -rp "  选择 [1-8] (默认5): " ver_choice

    case "${ver_choice:-5}" in
        1) MC_VERSION="1.21.4" ;;
        2) MC_VERSION="1.21.3" ;;
        3) MC_VERSION="1.21.1" ;;
        4) MC_VERSION="1.20.6" ;;
        5) MC_VERSION="1.20.4" ;;
        6) MC_VERSION="1.20.1" ;;
        7) MC_VERSION="1.19.4" ;;
        8) read -rp "  输入版本号 (如 1.20.4): " MC_VERSION ;;
        *) MC_VERSION="$DEFAULT_MC_VERSION" ;;
    esac

    echo ""
    info "选择版本: MC $MC_VERSION"

    # 服务端目录
    MC_DIR="$SCRIPT_DIR/mc-server"
    echo ""
    read -rp "  安装目录 (默认: $MC_DIR): " custom_dir
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
        info "下载 Fabric 安装器..."
        URL="https://maven.fabricmc.net/net/fabricmc/fabric-installer/${FABRIC_VERSION}/fabric-installer-${FABRIC_VERSION}.jar"
        curl -L -o "$INSTALLER" "$URL" || error "下载失败: $URL"
        info "下载完成"
    fi

    # 安装 Fabric 服务端
    if [ ! -f "$MC_DIR/fabric-server-launch.jar" ]; then
        info "安装 Fabric 服务端 (MC $MC_VERSION)..."
        java -jar "$INSTALLER" server -dir "$MC_DIR" -mcversion "$MC_VERSION" -loader "$FABRIC_VERSION" -downloadMinecraft
        info "安装完成"
    fi
fi

# ══════════════════════════════════════
# 第五步：下载 BlockMind Mod
# ══════════════════════════════════════
MODS_DIR="$MC_DIR/mods"
mkdir -p "$MODS_DIR"

if ! ls "$MODS_DIR"/blockmind-mod-*.jar >/dev/null 2>&1; then
    info "下载 BlockMind Mod..."
    RELEASE_JSON=$(curl -sL "https://api.github.com/repos/bmbxwbh/BlockMind/releases/latest")
    MOD_URL=$(echo "$RELEASE_JSON" | grep -o '"browser_download_url": "[^"]*blockmind-mod[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$MOD_URL" ]; then
        curl -L -o "$MODS_DIR/blockmind-mod.jar" "$MOD_URL"
        info "Mod 已下载"
    else
        warn "Mod 下载失败（可选），手动下载: https://github.com/bmbxwbh/BlockMind/releases"
    fi
else
    info "BlockMind Mod 已存在"
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
    error "未找到可启动的 JAR 文件"
fi

cd "$MC_DIR"
echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   🎮 启动 Minecraft 服务端             ║"
echo "  ╠══════════════════════════════════════╣"
echo "  ║   目录: $MC_DIR"
echo "  ║   JAR:  $LAUNCH_JAR"
echo "  ║   内存: $MAX_RAM"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  按 Ctrl+C 停止"
echo ""

exec java -Xms512M -Xmx"$MAX_RAM" -jar "$LAUNCH_JAR" nogui
