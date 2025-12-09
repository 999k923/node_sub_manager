#!/bin/bash
# stop.sh - 停止 Node Subscription Manager 服务，并取消开机自启

SERVICE_NAME="node_sub"

echo "=== 停止 systemd 服务 ==="
systemctl stop $SERVICE_NAME

echo "=== 取消开机自启 ==="
systemctl disable $SERVICE_NAME

echo "=== 强制杀掉残留 gunicorn 进程 ==="
PIDS=$(ps aux | grep gunicorn | grep -v grep | awk '{print $2}')
if [ -n "$PIDS" ]; then
    echo "杀掉进程: $PIDS"
    kill -9 $PIDS
else
    echo "没有找到运行中的 gunicorn 进程"
fi

echo "=== 删除 systemd 文件（可选） ==="
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
if [ -f "$SERVICE_FILE" ]; then
    rm -f $SERVICE_FILE
    systemctl daemon-reload
    echo "已删除 systemd 文件: $SERVICE_FILE"
fi

echo "=== Node Subscription Manager 已完全停止 ==="
