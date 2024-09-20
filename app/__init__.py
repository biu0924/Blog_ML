'''
这段代码的目的是
初始化 Flask 应用程序，并集成数据库、用户登录管理和数据库迁移功能。
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy# 一个 ORM(对象关系映射)库，用于数据库操作
from flask_login import LoginManager# 管理用户登陆状态，提供登陆回话处理
from flask_migrate import Migrate# 用于数据库迁移，管理数据库模式的变化
from config import Config

# 全局变量
db = SQLAlchemy()# 用于初始化并管理数据库连接
login_manager = LoginManager()# 处理用户登陆和认证
migrate = Migrate()# 管理数据库迁移

def create_app():
    '''
    一个 Flask 工厂函数，
    '''
    app = Flask(__name__)
    app.config.from_object(Config)# 加载配置

    # 初始化
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # 注册蓝图
    from app.routes import auth, blog
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    return app