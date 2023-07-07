import logging
from flask import request, jsonify, make_response
from mysql import User, Good, db, app
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Resource

logger = logging.getLogger(__name__)


# 管理员审核商品
class verify_good(Resource):
    def put(self, id):
        with app.app_context():
            token = request.headers.get("Authorization")
            parser = reqparse.RequestParser()
            parser.add_argument('status', type=int, required=True, location=['form'])
            args = parser.parse_args()
            if get_expiration(token):
                uid = get_id(token)  # 用户id
                user = db.session().query(User).filter(User.id == uid).first()
                status = user.status
                if status == 3:
                    good = db.session.query(Good).filter(Good.id == id).first()
                    if not good:
                        return make_response(jsonify(code=404, message="无该商品可审核"), 404)
                    db.session.query(Good).filter(Good.id == id).update({'status': args['status']})
                    db.session.commit()
                    dic_good = {
                        'msg': "您的商品审核完毕",
                        'id': good.id, 'view': good.view, 'content': good.content, 'game': good.game,
                        'title': good.title, 'status': good.status, 'sell_id': good.sell_id
                    }
                    # Message.on_message(Message, good.seller_id, jsonify(message=dic_good))
                    logger.debug("商品审核系统消息发放")
                    return make_response(jsonify(code=201, message='审核成功'), 201)
                else:
                    return make_response(jsonify(code=403, message="没有权限审核"), 403)
            else:
                return make_response(jsonify(code=401, message="登录时间过期"), 401)