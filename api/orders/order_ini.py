import logging
from flask import request, jsonify, make_response
from mysql import User, Good, db, Order, app
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Resource
from utils.snowflake import id_generate
import datetime
from api.chat.chat import Message

logger = logging.getLogger(__name__)


#  用户对商品出价
class order_ini(Resource):
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
                                order = Order(id=id_generate('order'), status=0, buyer_id=uid, seller_id=good.seller_id,
                                              generate_time=datetime.datetime.utcnow(),
                                              buyer_status=0, seller_status=0, good_id=good.id, price=args['price'])
                                db.session.add(order)
                                db.session.commit()
                                logger.debug("创建订单成功")
                                # order_dict = {"msg": "商品有新的订单", "id": order.id, "status": order.status,
                                #                "buyer_id": order.buyer_id, "seller_id": order.seller_id,
                                #              "good_id": order.good_id,
                                #              "buyer_status": order.buyer_status,
                                #              "generate_time": datetime.datetime.utcnow(),
                                #              "seller_status": order.seller_status, "price": order.price}
                                # Message.on_message(Message, order.seller_id, jsonify(message=order_dict))
                                # logger.debug("向卖家发送新的订单信息")
                                return make_response(jsonify(code=201, message='出价成功'), 201)
        else:
            return make_response(jsonify(code=401, message="登录过期"), 401)
