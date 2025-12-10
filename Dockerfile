# 基于官方 Python 3.12 slim 镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# ---------------------------
# 复制依赖文件并安装
# ---------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir requests gunicorn

# ---------------------------
# 复制项目文件
# ---------------------------
COPY . .

# ---------------------------
# 给 run_cron.sh 和 reset_node_id.py 添加执行权限 （新增/改动）
# ---------------------------
RUN chmod +x /app/run_cron.sh
RUN chmod +x /app/instance/reset_node_id.py

# ---------------------------
# 初始化数据库（如果不存在）
# ---------------------------
RUN python3 /app/db_init.py || true

# ---------------------------
# 暴露 Flask 端口
# ---------------------------
EXPOSE 5786

# ---------------------------
# 启动：后台执行 run_cron.sh，每小时重置节点 ID；前台启动 Gunicorn
# ---------------------------
CMD /app/run_cron.sh & gunicorn -b 0.0.0.0:5786 app:app
