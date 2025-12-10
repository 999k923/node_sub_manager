#!/bin/bash
# run_cron.sh - 每小时执行一次 reset_node_id.py

while true; do
    DB_FILE="/app/instance/nodes.db"

    # 如果数据库不存在，初始化
    if [ ! -f "$DB_FILE" ]; then
        python3 /app/db_init.py
    fi

    # 执行 ID 重置脚本
    python3 /app/instance/reset_node_id.py >> /app/cron.log 2>&1

    # 等待一小时
    sleep 3600
done
