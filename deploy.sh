#!/bin/bash
echo "更新系统..."
sudo apt update && sudo apt upgrade -y

echo "安装 Python3 & pip..."
sudo apt install python3 python3-pip -y

echo "安装依赖..."
pip3 install -r requirements.txt

echo "初始化数据库..."
python3 db_init.py

# ---------------------------
# 生成 token 文件（如果不存在）
# ---------------------------
echo "生成订阅 token..."
python3 - <<EOF
from app import get_token
get_token()
EOF

# ---------------------------
# 创建 systemd 服务
# ---------------------------
SERVICE_FILE="/etc/systemd/system/node_sub.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Node Subscription Manager
After=network.target

[Service]
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/app.py
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

echo "启动服务并设置开机自启..."
sudo systemctl daemon-reload
sudo systemctl start node_sub
sudo systemctl enable node_sub

# ---------------------------
# 显示 token
# ---------------------------
TOKEN_FILE="access_token.txt"
if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE")
    echo "部署完成！"
    echo "访问后台: http://服务器IP:5786/"
    echo "订阅地址: http://服务器IP:5786/sub?token=$TOKEN"
    echo "访问订阅时请使用 token: $TOKEN"
else
    echo "⚠️ token 文件生成失败，请手动运行 app.py 生成 token"
fi
