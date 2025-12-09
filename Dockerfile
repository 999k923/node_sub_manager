FROM python:3.11-slim

WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置 Flask 使用 0.0.0.0
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5786

# 确保 token 文件存在（如果是挂载卷则会覆盖）
RUN if [ ! -f access_token.txt ]; then touch access_token.txt; fi

EXPOSE 5786

# 启动服务
CMD ["python3", "app.py"]
