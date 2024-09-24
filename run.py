from app import create_app, db
from app.models import User, BlogPost
from flask_migrate import Migrate

app = create_app()# create_app() 调用工厂函数，返回一个 Flask 应用实例
migrate = Migrate(app, db)# 将 Flask 应用 与 SQLAlchemy 数据库绑定，以便执行数据库迁移命令


@app.shell_context_processor
def make_shell_context():
    '''
    1. 这个 @app.shell_context_processor 装饰器将 make_shell_context 注册为 shell 上下文处理器
    2. make_shell_context 返回一个字典，好汉数据库实例 db, 和两个模型类
    '''
    return {'db': db, 'User': User, 'BlogPost': BlogPost}

if __name__=='__main__':
    app.run(debug=True)