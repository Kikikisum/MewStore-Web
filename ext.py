from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO

db = SQLAlchemy()
cors = CORS()
socketio = SocketIO()

DEBUG = True  # 开启调试模式
SECRET_KEY = 'mewstore'  # flask的app密钥

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://mew_store:114514@106.14.35.23:3306/test'  # 数据库连接