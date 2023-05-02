from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mew_store:114514@106.14.35.23:3306/test'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.BigInteger, primary_key=True)
    nickname = db.Column(db.String(50))
    username = db.Column(db.String(50))
    profile_photo = db.Column(db.String(50))
    password = db.Column(db.String(102))
    phone_number = db.Column(db.String(11))
    money = db.Column(db.Numeric(20, 2))
    status = db.Column(db.Integer)  # 0为正常用户，1为黑户，2为被冻结状态，3为管理员
    name = db.Column(db.String(50))
    id_card = db.Column(db.String(18))


class Good(db.Model):
    __tablename__ = "good"
    id = db.Column(db.BigInteger, primary_key=True)
    view = db.Column(db.Integer)  # 点击量
    game = db.Column(db.String(50))  # 游戏
    title = db.Column(db.String(50))  # 账号标题
    content = db.Column(db.Text)  # 账号简介
    picture = db.Column(db.Text)  # 商品图片
    account = db.Column(db.String(50))  # 账号
    password = db.Column(db.String(50))  # 账号密码
    status = db.Column(db.Integer)  # 商品状态未审核为0，审核通过为1，审核不通过为-1,被下架为2，已售出为3
    seller_id = db.Column(db.BigInteger)  # 卖家id
    price = db.Column(db.Numeric(10, 2))  # 价格


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.BigInteger, primary_key=True)
    status = db.Column(db.Integer)  # 订单存在为1，不存在为0
    buyer_id = db.Column(db.BigInteger)  # 买方id
    seller_id = db.Column(db.BigInteger)  # 卖方id
    good_id = db.Column(db.BigInteger)  # 商品id
    buyer_status = db.Column(db.Integer)  # 买方付款为1，未付款为0
    seller_status = db.Column(db.Integer)  # 卖方确认订单为1，未确认为0,拒绝为-1
    price = db.Column(db.Numeric(10, 2))  # 价格


class Report(db.Model):
    __tablename__ = "report"
    id = db.Column(db.BigInteger, primary_key=True)  # 举报信息的id
    reported_id = db.Column(db.BigInteger)  # 被举报者的id
    report_order = db.Column(db.Integer)  # 被举报的订单
    reporter_id = db.Column(db.BigInteger)  # 举报者的id
    status = db.Column(db.Integer)  # 举报信息的处理情况，-1为未通过，0为未处理，1为通过举报
    content = db.Column(db.Text)  # 举报的原因和描述


class Favorite(db.Model):
    __tablename__ = "favorite"
    user_id = db.Column(db.BigInteger, primary_key=True)
    good_id = db.Column(db.BigInteger, primary_key=True)


class Freeze(db.Model):
    __tablename__ = "freeze"
    user_id = db.Column(db.BigInteger)
    order_id = db.Column(db.BigInteger)
    reason = db.Column(db.Text)
    status = db.Column(db.Integer)


with app.app_context():
    # db.drop_all()  # 初始化表格，需要时再用
    db.create_all()
