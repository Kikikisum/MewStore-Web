import logging
from flask import request, jsonify, make_response
from mysql import User, Good, db, Order, app
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Resource
from api.chat.chat import Message

logger = logging.getLogger(__name__)


# 卖家接受订单,id是订单id
class order_agree(Resource):
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
                        # Message.on_message(Message, order.buyer_id, jsonify(message=order_dict))
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
                        # Message.on_message(Message, order.buyer_id, jsonify(message=order_dict))
                        return jsonify(dict(code=201, message='订单确认成功', data="成功拒绝订单"))
                else:
                    return jsonify(dict(code=401, message='请勿重复确认订单'))
        else:
            return jsonify(dict(code=401, message="登录时间过期"))
