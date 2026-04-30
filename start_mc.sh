#!/usr/bin/env bash
# ═══════════════════════════════════════
# BlockMind — MC 服务端自动安装+启动 (Linux)
# ═══════════════════════════════════════
set -euo pipefail

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
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
echo "  🎮 Minecraft 服务端自动安装+启动"
echo ""

# ── 检查 Java ──
command -v java >/dev/null 2>&1 || error "未找到 Java 17+，请先安装: https://adoptium.net/"
info "Java $(java -version 2>&1 | head -1 | cut -d'"' -f2)"

# ── 创建目录 ──
mkdir -p "$MC_DIR"

# ── 下载 Fabric 安装器 ──
INSTALLER="$MC_DIR/fabric-installer.jar"
if [ ! -f "$INSTALLER" ]; then
    info "下载 Fabric 安装器..."
    URL="https://maven.fabricmc.net/net/fabricmc/fabric-installer/${FABRIC_VERSION}/fabric-installer-${FABRIC_VERSION}.jar"
    curl -L -o "$INSTALLER" "$URL" || error "下载失败: $URL"
    info "下载完成"
else
    info "Fabric 安装器已存在"
fi

# ── 安装 Fabric 服务端 ──
if [ ! -f "$MC_DIR/fabric-server-launch.jar" ]; then
    info "安装 Fabric 服务端 (MC $MC_VERSION)..."
    java -jar "$INSTALLER" server -dir "$MC_DIR" -mcversion "$MC_VERSION" -loader "$FABRIC_VERSION" -downloadMinecraft
    info "安装完成"
else
    info "Fabric 服务端已存在"
fi

# ── 下载 BlockMind Mod ──
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

# ── 接受 EULA ──
[ ! -f "$MC_DIR/eula.txt" ] && echo "eula=true" > "$MC_DIR/eula.txt"

# ── 内存配置 ──
TOTAL_MEM_KB=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}')
if [ -n "$TOTAL_MEM_KB" ] && [ "$TOTAL_MEM_KB" -gt 8000000 ]; then
    MAX_RAM="4G"
else
    MAX_RAM="2G"
fi

# ── 启动 ──
cd "$MC_DIR"
echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   🎮 启动 Minecraft 服务端             ║"
echo "  ╠══════════════════════════════════════╣"
echo "  ║   版本: MC $MC_VERSION + Fabric $FABRIC_VERSION"
echo "  ║   内存: $MAX_RAM"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  按 Ctrl+C 停止"
echo ""

exec java -Xms512M -Xmx"$MAX_RAM" -jar fabric-server-launch.jar nogui
