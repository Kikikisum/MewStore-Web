from flask import Flask
from flask_cors import CORS
from api.Order import orders
from api.Favorite import fav
from api.User import user
from api.Verify import verify
from api.Report import report
from flask_socketio import SocketIO
from chat.chat import Message
from mysql import db

import logging

app = Flask(__name__)
#  注册蓝图
app.register_blueprint(orders)
app.register_blueprint(fav)
app.register_blueprint(user)
app.register_blueprint(verify)
app.register_blueprint(report)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mew_store:114514@106.14.35.23:3306/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

logger = logging.getLogger()
logger.setLevel(level=logging.DEBUG)  # 设置日志级别为DEBUG
# 添加文件处理器
file_handler = logging.FileHandler(filename="app.log", encoding='utf-8')  # 创建日志处理器，用文件存放日志
file_handler = logging.StreamHandler()  # 创建日志处理器，用控制台输出日志
file_handler.setLevel(logging.DEBUG)  # 设置日志处理器的日志级别为DEBUG
formatter = logging.Formatter("[%(asctime)s]-[%(levelname)s]-[%(filename)s]-[Line:%(lineno)d]-[Msg:%(message)s]")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 跨域实现
cors = CORS()
cors.init_app(app)
# socketio注册
socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins='*')
socketio.on_namespace(Message('/system/message'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')  # 内网可用
    socketio.run(app, async_mode='threading')

