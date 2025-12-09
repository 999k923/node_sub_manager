# 基于官方 Python 3.12 slim 镜像
FROM python:3.12-slim

# 安装 cron
RUN apt update && apt install -y cron

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir requests gunicorn

# 复制项目文件
COPY . .

# 给 reset_id_only_safe.py 添加执行权限
RUN chmod +x reset_id_only_safe.py

# 创建 Cron 计划：每小时执行一次 reset_id_only_safe.py
RUN echo "0 * * * * python3 /app/reset_id_only_safe.py >> /app/cron.log 2>&1" > /etc/cron.d/reset-cron

# 给 Cron 文件加权限并注册
RUN chmod 0644 /etc/cron.d/reset-cron \
    && crontab /etc/cron.d/reset-cron

# 初始化数据库（如果不存在）
RUN python db_init.py || true

# 暴露 Flask 端口
EXPOSE 5786

# 启动：先跑 cron，再跑 gunicorn
CMD cron && gunicorn -b 0.0.0.0:5786 app:app
