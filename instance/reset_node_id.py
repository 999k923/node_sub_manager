#!/usr/bin/env python3
# reset_id_only_safe.py
import os
import sqlite3

DB_FILE = "nodes.db"
OFFSET = 100000  # 临时偏移量，保证不冲突

if not os.path.exists(DB_FILE):
    print(f"⚠️ 数据库文件 {DB_FILE} 不存在！")
    exit(1)

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# ---------------------------
# 获取所有节点的当前 ID，按 sort_order 或原顺序排序
# ---------------------------
cursor.execute("SELECT id FROM node ORDER BY sort_order, id;")
rows = cursor.fetchall()

# ---------------------------
# 第一步：先加上偏移量，避免 UNIQUE 冲突
# ---------------------------
for old_id, in rows:
    cursor.execute("UPDATE node SET id = id + ? WHERE id = ?;", (OFFSET, old_id))

# ---------------------------
# 第二步：重新生成连续 ID
# ---------------------------
for new_id, (old_id,) in enumerate(rows, start=1):
    cursor.execute("UPDATE node SET id = ? WHERE id = ?;", (new_id, old_id + OFFSET))

conn.commit()
conn.close()

print("✅ 节点 ID 已重新生成连续序号，节点顺序保持不变！")
