import logging
from flask import request, jsonify, Blueprint, make_response
from mysql import User, Good, db, Order, app,Messages
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Api, Resource
from utils.snowflake import id_generate
from chat.chat import Message

orders = Blueprint('order', __name__)
api = Api(orders)
logger = logging.getLogger(__name__)


#  用户对商品出价
class Order_ini(Resource):
    #   id为商品id
    def post(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('price', type=float, required=True, location=['form'])
        token = request.headers.get("Authorization")
        args = parser.parse_args()
        if get_expiration(token):
            uid = get_id(token)  # 买方的id
            with app.app_context():
                user = db.session.query(User).filter(User.id == uid).first()
                if not user:
                    print("sss")
                status = user.status
                good = db.session.query(Good).filter(Good.id == id).first()
                good_status = good.status
                if good_status == 2:
                    return jsonify(dict(code=403, message='出价失败', data="商品已被下架"))
                else:
                    if good_status == 3:
                        return jsonify(dict(code=403, message='出价失败', data="商品已出售"))
                    else:
                        if status == 1:
                            return jsonify(code=403, message='出价失败', data='黑户没有权限出价')
                        else:
                            if status == 2:
                                return jsonify(code=403, message='出价失败', data='用户处于被冻结状态，无法出价')
                            else:
                                order = Order(id=id_generate(1, 3), status=0, buyer_id=uid, seller_id=good.seller_id,
                                              buyer_status=0, seller_status=0, good_id=good.id, price=args['price'])
                                db.session.add(order)
                                db.session.commit()
                                logger.debug("创建订单成功")
                                order_dict = {"msg": "商品有新的订单", "id": order.id, "status": order.status, "buyer_id":
                                    order.buyer_id, "seller_id": order.seller_id, "good_id": order.good_id,
                                              "buyer_status": order.buyer_status,
                                              "seller_status": order.seller_status, "price": order.price}
                                Message.on_message(Message, order.seller_id, jsonify(message=order_dict))
                                logger.debug("向卖家发送新的订单信息")
                                return make_response(jsonify(code=201, message='出价成功'), 201)
        else:
            return make_response(jsonify(code=401, message="登录过期"), 401)


# 卖家接受订单,id是订单id
class agree_order(Resource):
    @staticmethod
    def put(id):
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=int, required=True, location=['form'])
        args = parser.parse_args()
        token = request.headers.get("Authorization")
        if get_expiration(token):
            uid = get_id(token)
            with app.app_context():
                user = db.session.query(User).filter(User.id == uid).first()
                user_status = user.status
                if user_status == 2 or user_status == 1:
                    return make_response(jsonify(code=403, message="订单确认失败", data="用户处于冻结或黑户状态"), 403)
                good_id = db.session.query(Order).filter(Order.id == id).first().good_id
                order = db.session.query(Order).filter(Order.id == id).first()
                if order.seller_status == 0:
                    if args['status'] == 1:
                        db.session.query(Order).filter(Order.good_id == good_id).update({'seller_status': -1})
                        db.session.query(Order).filter(Order.id == id).update({'seller_status': 1, 'status': 1})
                        db.session.query(Good).filter(Good.id == good_id).update({'status': 3})
                        db.session.commit()
                        if order.seller_status == 1:
                            db.session.query(Order).filter(Order.id == id).update({'status': 1})
                            db.session.commit()
                        order_dict = {"msg": "卖家确认订单成功!", "id": order.id, "status": order.status,
                                      "buyer_id": order.buyer_id,
                                      "seller_id": order.seller_id, "good_id": order.good_id,
                                      "buyer_status": order.buyer_status,
                                      "seller_status": order.seller_status, "price": order.price}
                        logger.debug("向买家发送卖家确认订单的消息")
                        Message.on_message(Message, order.buyer_id, jsonify(message=order_dict))
                        return make_response(jsonify(code=201, message='订单确认成功', data="成功接收订单"), 201)
                    else:
                        db.session.query(Order).filter(Order.id == id).update({'seller_status': -1})
                        db.session.commit()
                        order_dict = {"msg": "卖家拒绝订单!", "id": order.id, "status": order.status,
                                      "buyer_id": order.buyer_id,
                                      "seller_id": order.seller_id, "good_id": order.good_id,
                                      "buyer_status": order.buyer_status,
                                      "seller_status": order.seller_status, "price": order.price}
                        logger.debug("向买家发送卖家拒绝订单的消息")
                        Message.on_message(Message, order.buyer_id, jsonify(message=order_dict))
                        return jsonify(dict(code=201, message='订单确认成功', data="成功拒绝订单"))
                else:
                    return jsonify(dict(code=401, message='请勿重复确认订单'))
        else:
            return jsonify(dict(code=401, message="登录时间过期"))


#   id是订单id
class pay_order(Resource):
    def put(self, id):
        token = request.headers.get("Authorization")
        if get_expiration(token):
            uid = get_id(token)
            with app.app_context():
                user = db.session.query(User).filter(User.id == uid).first()
                status = user.status
                order = db.session.query(Order).filter(Order.id == id).first()
                if status == 2 or status == 1:
                    return make_response(jsonify(code=403, message="订单支付失败", data="用户处于冻结或黑户状态"), 403)
                else:
                    order_money = order.price
                    user = db.session.query(User).filter(User.id == uid).first()
                    money = user.money-order_money
                    if money >= 0:
                        db.session.query(User).filter(User.id == uid).update({'money': money})
                        db.session.commit()
                        if order.buyer_status == 1:
                            db.session.query(Order).filter(Order.id == id).update({'status': 1})
                            db.session.commit()
                        order_dict = {"msg": "买家支付成功!", "id": order.id, "status": order.status,
                                      "buyer_id": order.buyer_id,
                                      "seller_id": order.seller_id, "good_id": order.good_id,
                                      "buyer_status": order.buyer_status,
                                      "seller_status": order.seller_status, "price": order.price}
                        logger.debug("向卖家发送买家支付成功的消息!")
                        Message.on_message(Message, order.seller_id, jsonify(message=order_dict))
                        return make_response(jsonify(code=201, message='订单支付成功', data='买家确认成功'), 201)
                    else:
                        return make_response(jsonify(code=400, message='订单支付失败', data='余额不足'), 400)
        else:
            return make_response(jsonify(code=401, message="登录时间过期"), 401)


#  查找用户作为卖家的订单
class search_sell(Resource):
    def get(self):
        with app.app_context():
            token = request.headers.get("Authorization")
            page = request.args.get('page', type=int, default=1)
            size = request.args.get('size', type=int, default=4)
            if get_expiration(token):
                uid = get_id(token)
                sql_order = db.session.query(Order).filter(Order.seller_id == uid).order_by(Order.id.desc())
                orders = sql_order.paginate(page=page, per_page=size).items
                order_list = []
                if not orders:
                    return make_response(jsonify(code=200, message="获取订单成功", data=order_list), 200)
                for order in orders:
                    order_dict = {"id": order.id, "status": order.status, "buyer_id": order.buyer_id,
                            "seller_id": order.seller_id, "good_id": order.good_id, "buyer_status": order.buyer_status,
                            "seller_status": order.seller_status, "price": order.price}
                    order_list.append(order_dict)
                logger.debug('获取作为卖家的订单')
                return make_response(jsonify(code=200, message="获取订单成功", data=order_list), 200)
            else:
                return make_response(jsonify(code=401, message="登录时间过期"), 401)


#   查看自身出价的订单
class search_My_Order(Resource):
    def get(self):
        token = request.headers.get("Authorization")
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        if get_expiration(token):
            uid = get_id(token)
            with app.app_context():
                sql_order = db.session.query(Order).filter(Order.buyer_id == uid).order_by(Order.id.desc())
                orders = sql_order.paginate(page=page, per_page=size).items
                order_list = []
                if not orders:
                    return make_response(jsonify(code=200, message="获取订单成功", data=order_list), 200)
                for order in orders:
                    order_dict = {"id": order.id, "status": order.status, "buyer_id": order.buyer_id,
                                  "seller_id": order.seller_id, "good_id": order.good_id,
                                  "buyer_status": order.buyer_status,
                                  "seller_status": order.seller_status, "price": order.price
                                  }
                    order_list.append(order_dict)
                logger.debug('获取作为卖家的订单')
                return make_response(jsonify(code=200, message="获取订单成功", data=order_list), 200)
        else:
            return make_response(jsonify(code=401, message="登录时间过期"), 401)


#   查询不同状态的订单(管理员)
class get_Status(Resource):
    def get(self, status):
        with app.app_context():
            token = request.headers.get("Authorization")
            page = request.args.get('page', type=int, default=1)
            size = request.args.get('size', type=int, default=4)
            if get_expiration(token):
                uid = get_id(token)
                user = db.session.query(User).filter(User.id == uid).first()
                user_status = user.status
                if user_status == 3:
                    sql_order = db.session.query(Order).filter(Order.status == status).order_by(Order.id.desc())
                    orders = sql_order.paginate(page=page, per_page=size).items
                    order_list = []
                    if not orders:
                        return make_response(jsonify(code=200, message="获取订单成功", data=order_list), 200)
                    for order in orders:
                        order_dict = {"id": order.id, "status": order.status, "buyer_id": order.buyer_id,
                                      "seller_id": order.seller_id, "good_id": order.good_id,
                                      "buyer_status": order.buyer_status, "seller_status": order.seller_status,
                                      "price": order.price}
                        order_list.append(order_dict)
                    logger.debug('获取作为卖家的订单')
                    return make_response(jsonify(code=200, message="获取订单成功", data=order_list), 200)
                else:
                    return make_response(jsonify(code=401, message="没有权限查询"), 401)
            else:
                return make_response(jsonify(code=401, message="登录时间过期"), 401)


api.add_resource(Order_ini, '/order/<int:id>')
api.add_resource(agree_order, '/order/agree/<int:id>')
api.add_resource(pay_order, '/order/pay/<int:id>')
api.add_resource(search_sell, '/order/sell')
api.add_resource(search_My_Order, '/my/order')
api.add_resource(get_Status, '/order/<int:status>')
