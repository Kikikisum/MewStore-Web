from flask import Flask
from flask_cors import CORS
from Order import orders
from Favorite import fav
from User import user
from Verify import verify
import logging

app = Flask(__name__)
CORS(app)  # 实现跨域
#  注册蓝图
app.register_blueprint(orders)
app.register_blueprint(fav)
app.register_blueprint(user)
app.register_blueprint(verify)

logger = logging.getLogger()
logger.setLevel(level=logging.DEBUG)  # 设置日志级别为DEBUG
# 添加文件处理器
file_handler = logging.FileHandler(filename="app.log", encoding='utf-8')  # 创建日志处理器，用文件存放日志
file_handler = logging.StreamHandler()  # 创建日志处理器，用控制台输出日志
file_handler.setLevel(logging.DEBUG)  # 设置日志处理器的日志级别为DEBUG
formatter = logging.Formatter("[%(asctime)s]-[%(levelname)s]-[%(filename)s]-[Line:%(lineno)d]-[Msg:%(message)s]")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app.run(host='0.0.0.0')  # 内网可用