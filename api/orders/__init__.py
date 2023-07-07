from flask import Blueprint
from flask_restful import Api
from .order_agree import order_agree
from .order_ini import order_ini
from .order_my import search_My_Order
from .order_pay import pay_order
from .order_search import search_sell
from .order_status import get_Status


orders = Blueprint('order', __name__)
api = Api(orders)


api.add_resource(order_ini, '/order/<int:id>')
api.add_resource(order_agree, '/order/agree/<int:id>')
api.add_resource(pay_order, '/order/pay/<int:id>')
api.add_resource(search_sell, '/order/sell')
api.add_resource(search_My_Order, '/my/order')
api.add_resource(get_Status, '/order/<int:status>')
