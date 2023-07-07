import logging
from flask import request, jsonify, make_response
from mysql import db, Order, app
from utils.Token import get_expiration, get_id
from flask_restful import Resource

logger = logging.getLogger(__name__)


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
