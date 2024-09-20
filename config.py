import os
from dotenv import load_dotenv

load_dotenv()
'''
	调用了 load_dotenv()，它会查找 .env 文件并将其中定义的变量加载为环境变量。
	这通常用于将敏感信息（如密钥、数据库连接字符串等）保存在 .env 文件中，
	而不是直接在代码中暴露。
'''
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    '''
    SECRET_KEY:
        读取环境变量 SECRET_KEY，这是应用的密钥，通常用于加密 cookie 或其他敏感数据。
        如果 SECRET_KEY 没有在环境变量中设置，程序会使用默认值 'you-will-never-guess'。在实际部署时，最好使用一个强随机生成的密钥并通过 .env 文件或系统环境变量设置它。
    SQLALCHEMY_DATABASE_URI:
        读取环境变量 DATABASE_URL，这是数据库的连接字符串，通常用于指定应用要连接的数据库类型（例如 PostgreSQL、MySQL 等）。
        如果 DATABASE_URL 未设置，程序会回退到使用 SQLite 数据库，并将数据库文件存储在当前项目目录下的 app.db 文件中。
    SQLALCHEMY_TRACK_MODIFICATIONS:
        设置为 False，禁用 SQLAlchemy 对对象修改的事件通知系统，节省内存和计算资源。这是 Flask-SQLAlchemy 的一个常见设置，推荐将其设为 False。
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://root:123456@localhost:5432/blog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB ma
