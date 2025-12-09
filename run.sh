#!/bin/bash
# run_venv.sh - 自动创建虚拟环境 + systemd 启动 Node Subscription Manager

APP_DIR="/root/node_name"
VENV_DIR="$APP_DIR/venv"
SERVICE_FILE="/etc/systemd/system/node_sub.service"

echo "=== 更新系统 & 安装 Python3 ==="
apt update -y
apt install -y python3 python3-venv python3-pip

# ---------------------------
# 创建虚拟环境
# ---------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
else
    echo "虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# ---------------------------
# 安装依赖
# ---------------------------
echo "安装 Python 依赖..."
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
pip install requests --upgrade

# ---------------------------
# 检测 gunicorn
# ---------------------------
GUNICORN_PATH="$VENV_DIR/bin/gunicorn"
if [ ! -x "$GUNICORN_PATH" ]; then
    echo "安装 gunicorn..."
    pip install gunicorn
fi

echo "gunicorn 路径: $GUNICORN_PATH"

# ---------------------------
# 创建或覆盖 systemd 服务文件
# ---------------------------
echo "创建 systemd 服务文件..."
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Node Subscription Manager
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/python $APP_DIR/app.py
Restart=always
RestartSec=3
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

# ---------------------------
# 重载 systemd & 启动服务
# ---------------------------
echo "重载 systemd 配置..."
sudo systemctl daemon-reload

echo "设置开机自启..."
sudo systemctl enable node_sub

echo "启动服务..."
sudo systemctl restart node_sub

echo "查看服务状态..."
sleep 1
sudo systemctl status node_sub --no-pager -n 20

# ---------------------------
# 显示订阅 token
# ---------------------------
TOKEN_FILE="$APP_DIR/access_token.txt"
if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE")
    echo "部署完成！"
    echo "访问后台: http://服务器IP:5786/"
    echo "订阅地址: http://服务器IP:5786/sub?token=$TOKEN"
    echo "访问订阅时请使用 token: $TOKEN"
else
    echo "⚠️ token 文件生成失败，请手动运行 app.py 生成 token"
fi

# ---------------------------
# 完成
# ---------------------------
deactivate
