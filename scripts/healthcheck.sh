#!/usr/bin/env bash
# BlockMind 健康检查脚本
# 用法: bash scripts/healthcheck.sh

set -euo pipefail

WEBUI_PORT=${BLOCKMIND_WEBUI_PORT:-8080}
MOD_PORT=${BLOCKMIND_MOD_PORT:-25580}

echo "🧠 BlockMind 健康检查"
echo "========================"

# 检查 WebUI
echo -n "WebUI (:$WEBUI_PORT): "
if curl -sf "http://localhost:$WEBUI_PORT/api/system/health" > /dev/null 2>&1; then
    echo "✅ 正常"
else
    echo "❌ 不可达"
fi

# 检查 Mod API
echo -n "Mod API (:$MOD_PORT): "
if curl -sf "http://localhost:$MOD_PORT/health" > /dev/null 2>&1; then
    echo "✅ 正常"
    # 获取状态
    STATUS=$(curl -sf "http://localhost:$MOD_PORT/api/status" 2>/dev/null || echo '{}')
    echo "  状态: $STATUS"
else
    echo "❌ 不可达"
fi

# 检查 systemd 服务
echo -n "Systemd 服务: "
if systemctl is-active blockmind &>/dev/null; then
    echo "✅ 运行中"
else
    echo "⚠️  未运行或未安装"
fi

# 检查进程
echo -n "Python 进程: "
if pgrep -f "src.main" > /dev/null; then
    echo "✅ 存在 ($(pgrep -f 'src.main' | wc -l) 个)"
else
    echo "❌ 未找到"
fi

echo ""
echo "========================"
