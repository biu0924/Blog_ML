echo "Waiting for database..."

# 使用 netcat 循环检测数据库端口 5432 是否可用，直到成功为止
while ! nc -z db 5432; do
  # 每 0.1 秒检测一次
  sleep 0.1
done

echo "Database started"

# 运行 Flask 数据库迁移命令，应用数据库更新
flask db upgrade

# 使用 Gunicorn 启动 Flask 应用，监听 8000 端口
exec gunicorn --bind 0.0.0.0:8000 run:app

