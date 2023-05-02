import logging
from flask import request, jsonify, Blueprint, make_response
from mysql import User, Good, db, Order, app
from Token import get_expiration, get_id
from flask_restful import reqparse, Api, Resource
from snowflake import id_generate

order = Blueprint('order', __name__)
api = Api(order)
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
            user = db.session.query(User).filter_by(User.id == uid).first()
            status = user.status
            good = db.session.query(Good).filter_by(Good.id == id).first()
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
                            order = Order(id=id_generate(1, 4), status=0, buyer_id=uid, seller_id=good.seller_id,
                                          buyer_status=0, seller_status=0, good_id=good.id, price=args['price'])
                            db.session.add(order)
                            db.session.commit()
                            logger.debug("创建订单成功")
                            return make_response(jsonify(code=201, message='出价成功'), 201)
        else:
            return make_response(jsonify(code=401, message="登录过期"), 401)


# 卖家接受订单,id是订单id
class agree_order(Resource):
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=int, required=True, location=['form'])
        args = parser.parse_args()
        token = request.headers.get("Authorization")
        if get_expiration(token):
            uid = get_id(token)
            user = db.session.query(User).filter_by(User.id == uid).first()
            user_status = user.status
            if user_status == 2 or user_status == 1:
                return make_response(jsonify(code=403, message="订单确认失败", data="用户处于冻结或黑户状态"), 403)
            good_id = db.session.query(Order).filter_by(Order.id == id).first().good_id
            if args['status'] == '1':
                db.session.query(Order).filter_by(Order.good_id == good_id).update({'seller_status': -1})
                db.session.query(Order).filter_by(Order.id == id).update({'seller_status': 1, 'status': 1})
                db.session.query(Good).filter_by(Good.id == good_id).update({'status': 3})
                db.session.commit()
                return make_response(jsonify(code=201, message='订单确认成功', data="成功接收订单"), 201)
            else:
                db.session.query(Order).filter_by(Order.id == id).update({'seller_status': -1})
                db.session.commit()
                return jsonify(dict(code=201, message='订单确认成功', data="成功拒绝订单"))
        else:
            return jsonify(dict(code=401, message="登录时间过期"))


#   id是订单id
class pay_order(Resource):
    def put(self, id):
        token = request.headers.get("Authorization")
        if get_expiration(token):
            uid = get_id(token)
            user = db.session.query(User).filter_by(User.id == uid).first()
            status = user.status
            order = db.session.query(Order).filter_by(Order.id == id).first()
            if status == 2 or status == 1:
                return make_response(jsonify(code=403, message="订单支付失败", data="用户处于冻结或黑户状态"),403)
            else:
                order_money = order.money
                user = db.session.query(User).filter_by(User.id == uid).first()
                money = user.money-order_money
                if money >= 0:
                    db.session.query(Order).filter_by(Order.id == id).update({'money': money})
                    db.session.commit()
                    return make_response(jsonify(code=201, message='订单支付成功', data='买家确认成功'), 201)
                else:
                    return make_response(jsonify(code=400, message='订单支付失败,', data='余额不足'), 400)
        else:
            return make_response(jsonify(code=401, message="登录时间过期"), 401)


#  查找用户作为卖家的订单
class search_sell(Resource):
    def get(self):
        token = request.headers.get("Authorization")
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        if get_expiration(token):
            uid = get_id(token)
            with app.app_context():
                sql_order = db.session.query(Order).filter_by(Order.seller_id == uid).order_by(Order.id.desc())
                orders = sql_order.paginate(page=page,per_page=size).items
                order_list = []
                for order in orders:
                    order_dict = {"id": order.id, "status": order.status, "buyer_id": order.buyer_id,
                                  "seller_id": order.seller_id, "good_id": order.good_id, "buyer_status": order.buyer_status,
                                  "seller_status":order.seller_status, "price": order.price
                                  }
                    order_list.append(order_dict)
                logger.debug('获取作为卖家的订单')
                return make_response(jsonify(code=200,message="获取订单成功",data=order_list),200)
        else:
            return make_response(jsonify(code=401, message="登录时间过期"), 401)


#   查看自身出价的订单
class search_Myorder(Resource):
    def get(self):
        token = request.headers.get("Authorization")
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        if get_expiration(token):
            uid = get_id(token)
            with app.app_context():
                sql_order = db.session.query(Order).filter_by(Order.buyer_id == uid).order_by(Order.id.desc())
                orders = sql_order.paginate(page=page, per_page=size).items
                order_list = []
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
        token = request.headers.get("Authorization")
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        if get_expiration(token):
            uid = get_id(token)
            user = db.session.query(User).filter_by(User.id == uid).first()
            user_status = user.status
            if user_status == 3:
                with app.app_context():
                    sql_order = db.session.query(Order).filter_by(Order.status == status).order_by(Order.id.desc())
                    orders = sql_order.paginate(page=page, per_page=size).items
                    order_list = []
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
                return make_response(jsonify(code=401, message="没有权限查询"), 401)
        else:
            return make_response(jsonify(code=401, message="登录时间过期"), 401)


api.add_resource(Order_ini, '/order/<int:id>')
api.add_resource(agree_order, '/order/agree/<int:id>')
api.add_resource(pay_order, '/order/pay/<int:id>')
api.add_resource(search_sell, '/order/sell')
api.add_resource(search_Myorder, '/my/order')
api.add_resource(get_Status, '/order/<int:status>')
