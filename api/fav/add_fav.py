from mysql import db, app, User, Favorite, Good
from flask import request, jsonify, make_response
from utils.Token import get_expiration, get_id
from flask_restful import Resource


#   添加一个收藏，id为商品id
class Fav_add(Resource):
    def post(self, id):
        with app.app_context():
            token = request.headers.get("Authorization")
            if get_expiration(token):
                uid = get_id(token)
                user = db.session.query(User).filter(User.id == uid).first()
                user_status = user.status
                if user_status == 1 or user_status == 2:
                    return make_response(jsonify(code=401, message="用户为黑户或被冻结，无法收藏商品"), 401)
                else:
                    favs = db.session.query(Favorite).filter(Favorite.user_id == uid, Favorite.good_id == id).first()
                    if not favs:
                        good = db.session.query(Good).filter(Good.id == id).first()
                        good_view = good.view
                        good_view += 1
                        db.session.query(Good).filter(Good.id == id).update({'view': good_view})
                        db.session.commit()
                        favorite = Favorite(user_id=uid, good_id=id)
                        db.session.add(favorite)
                        db.session.commit()
                        return make_response(jsonify(code=200, message="收藏成功"))
                    else:
                        return make_response(jsonify(code=401, message="请勿重复收藏"))
            else:
                return make_response(jsonify(code=401, message="登录时间过期"), 401)

