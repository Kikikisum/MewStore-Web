from mysql import db, app, Good
from flask import request, jsonify
from utils.Token import get_expiration
from flask_restful import Resource


class good_get(Resource):
    def get(self, id):
        with app.app_context():
            token = request.headers.get("Authorization")
            if get_expiration(token):
                gid = id
                good = db.session.query(Good).filter(Good.id == gid).first()
                if not good:
                    return jsonify(dict(code=404, messsage="获取商品失败", date="商品不存在"))
                else:
                    data = {
                        'id': good.id, 'view': good.view, 'content': good.content, 'game': good.game,
                        'title': good.title, 'status': good.status, 'sell_id': good.sell_id
                    }
                    return jsonify(dict(code=201, message="获取商品情况成功", data=data))
            else:
                return jsonify(dict(code=401, message="登录时间过期"))