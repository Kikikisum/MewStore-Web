from mysql import db, app, Good
from flask import request, jsonify
from utils.Token import get_expiration
from flask_restful import Resource


class good_status(Resource):
    def get(self):
        with app.app_context():
            token = request.headers.get("Authorization")
            status = request.args.get('status', type=int, default=1)
            if get_expiration(token):
                good = db.session.query(Good).filter(Good.status == status).all()
                if not good:
                    return jsonify(code=401, message="没有该状态的商品")
                else:
                    List = []
                    for i in good:
                        data = {
                            'id': i.id, 'view': i.view, 'content': i.content, 'game': i.game,
                            'title': i.title, 'status': i.status, 'sell_id': i.sell_id
                        }
                        List.append(data)
                    return jsonify(dict(code=200, message="查询成功", data=List))
            else:
                return jsonify(dict(code=401, message="登录时间过期"))
