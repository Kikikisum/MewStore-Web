import logging
from flask import request, jsonify, make_response
from mysql import User, db, Order, app
from utils.Token import get_expiration, get_id
from flask_restful import Resource
from utils.snowflake import id_generate
from api.chat.chat import Message

logger = logging.getLogger(__name__)


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
                        # Message.on_message(Message, order.seller_id, jsonify(message=order_dict))
                        return make_response(jsonify(code=201, message='订单支付成功', data='买家确认成功'), 201)
                    else:
                        return make_response(jsonify(code=400, message='订单支付失败', data='余额不足'), 400)
        else:
            return make_response(jsonify(code=401, message="登录时间过期"), 401)
