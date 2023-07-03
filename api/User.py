import logging
from flask import request, jsonify, Blueprint, make_response
from mysql import User, db, Order, app
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Api, Resource


user = Blueprint('user', __name__)
api = Api(user)
logger = logging.getLogger(__name__)


# 卖家发出找回账号请求,id为订单id
class return_account(Resource):
    def post(self, id):
        token = request.headers.get("Authorization")
        parser = reqparse.RequestParser()
        parser.add_argument('reason', type=str, required=True, location=['form'])
        args = parser.parse_args()
        with app.app_context():
            if get_expiration(token):
                uid = get_id(token)  # 用户id
                user = db.session.query(User).filter(User.id == uid).first()
                user_status = user.status
                order = db.session.query(Order).filter(Order.id == id).first()
                if order.status == 1:
                    if user_status == 1:
                        return make_response(jsonify(code=401, message='黑户没有权限申请'), 401)
                    else:
                        if user_status == 0 or user_status == 3:
                            db.session.query(User).filter(User.id == uid).update({'status': 2})
                            db.session.commit()
                            freeze = Freeze(user_id=uid, order_id=id, reason=args['reason'], status=0)
                            db.session.add(freeze)
                            db.session.commit()
                            return make_response(jsonify(code=201, message='账号找回申请成功'), 201)
                        else:
                            return make_response(jsonify(code=401, message='被冻结状态没有权限申请'), 401)
                else:
                    return make_response(jsonify(code=401, message='订单还未完成，不可找回账号'), 401)
            else:
                return make_response(jsonify(code=401, message="登录时间过期"), 401)


api.add_resource(return_account, '/return/<int:id>')
