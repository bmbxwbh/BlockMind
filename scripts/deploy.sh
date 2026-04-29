#!/usr/bin/env bash
# BlockMind 部署脚本
# 用法: sudo bash scripts/deploy.sh

set -euo pipefail

INSTALL_DIR="/opt/blockmind"
SERVICE_NAME="blockmind"
USER="blockmind"

echo "🧠 BlockMind 部署开始..."

# 1. 创建用户
if ! id "$USER" &>/dev/null; then
    echo "创建用户: $USER"
    useradd --system --shell /bin/false "$USER"
fi

# 2. 创建目录
echo "安装到: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p /data/blockmind/skills
mkdir -p /data/blockmind/logs

# 3. 复制文件
echo "复制项目文件..."
cp -r src/ "$INSTALL_DIR/"
cp -r skills/ "$INSTALL_DIR/"
cp -r config/ "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"

# 4. Python 虚拟环境
echo "创建虚拟环境..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# 5. 配置文件
if [ ! -f "$INSTALL_DIR/config.yaml" ]; then
    echo "创建默认配置..."
    cp config/config.example.yaml "$INSTALL_DIR/config.yaml"
    echo "⚠️  请编辑 $INSTALL_DIR/config.yaml 配置 AI API Key"
fi

# 6. 设置权限
chown -R "$USER:$USER" "$INSTALL_DIR"
chown -R "$USER:$USER" /data/blockmind

# 7. 安装 systemd 服务
echo "安装 systemd 服务..."
cp scripts/blockmind.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

echo ""
echo "✅ 部署完成！"
echo ""
echo "后续操作："
echo "  编辑配置:  sudo nano $INSTALL_DIR/config.yaml"
echo "  启动服务:  sudo systemctl start $SERVICE_NAME"
echo "  查看状态:  sudo systemctl status $SERVICE_NAME"
echo "  查看日志:  journalctl -u $SERVICE_NAME -f"
echo ""
