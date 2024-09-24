# 基础镜像为官方的 python 3.11-slim
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 更新包管理器并安装 netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd

# 复制当前目录下的所有文件到容器的工作目录
COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 设置 Flask 环境变量，指定应用入口文件为 run.py
ENV FLASK_APP=run.py

# 设置 Flask 运行模式为生产环境
ENV FLASK_ENV=production

# 暴露容器的 8000 端口
EXPOSE 8000

# 使用 Gunicorn 作为 WSGI 服务器，监听 8000 端口并运行 Flask 应用
CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app"]
