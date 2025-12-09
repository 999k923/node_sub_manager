#!/bin/bash
# run.sh - 自动检测 gunicorn 路径 + systemd 启动 Node Subscription Manager

APP_DIR="/root/node_sub_manager"
SERVICE_FILE="/etc/systemd/system/node_sub.service"

echo "=== 安装依赖 ==="
apt update -y
apt install -y python3-pip
# 安装系统 gunicorn，如果已经存在不会重复安装
apt install -y python3-gunicorn || true
pip install --no-cache-dir flask || true

# 检测 gunicorn 路径
GUNICORN_PATH=$(which gunicorn)
if [ -z "$GUNICORN_PATH" ]; then
    echo "❌ 没找到 gunicorn，安装 pip 版本..."
    pip install --no-cache-dir gunicorn
    GUNICORN_PATH=$(which gunicorn)
fi

echo "gunicorn 路径: $GUNICORN_PATH"

echo "=== 创建或覆盖 systemd 服务文件 ==="
cat <<EOF > $SERVICE_FILE
[Unit]
Description=Node Subscription Manager
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=$GUNICORN_PATH -b 0.0.0.0:5786 app:app
Restart=always
RestartSec=3
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "=== 重新加载 systemd 配置 ==="
systemctl daemon-reload

echo "=== 设置开机自启 ==="
systemctl enable node_sub

echo "=== 重启并启动服务 ==="
systemctl restart node_sub

echo "=== 查看服务状态 ==="
sleep 1
systemctl status node_sub --no-pager -n 20
