import logging
from flask import request, jsonify, Blueprint, make_response
from mysql import User, Good, db, Order, app,Favorite
from Token import get_expiration, get_id
from flask_restful import reqparse, Api, Resource
from snowflake import id_generate

fav = Blueprint('fav', __name__)
api = Api(fav)
logger = logging.getLogger(__name__)


#   添加一个收藏，id为商品id
class add_fav(Resource):
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
                        favorite = Favorite(user_id=uid, good_id=id)
                        db.session.add(favorite)
                        db.session.commit()
                        return make_response(jsonify(code=200, message="收藏成功"))
                    else:
                        return make_response(jsonify(code=401, message="请勿重复收藏"))
            else:
                return make_response(jsonify(code=401, message="登录时间过期"), 401)


#  获取自身收藏的商品
class my_fav(Resource):
    def get(self):
        with app.app_context():
            token = request.headers.get("Authorization")
            page = request.args.get('page', type=int, default=1)
            size = request.args.get('size', type=int, default=4)
            if get_expiration(token):
                uid = get_id(token)
                with app.app_context():
                    sql_order = db.session.query(Favorite).filter(Favorite.user_id == uid).order_by(Favorite.user_id.desc())
                    favs = sql_order.paginate(page=page, per_page=size).items
                    fav_list = []
                    if not favs:
                        return make_response(jsonify(code=200, message="获取收藏商品成功", data=fav_list), 200)
                    for fav in favs:
                        fav_dict = {"user_id": fav.user_id, "good_id": fav.good_id}
                        fav_list.append(fav_dict)
                    logger.debug('获取自身的收藏商品')
                    return make_response(jsonify(code=200, message="获取收藏商品成功", data=fav_list), 200)
            else:
                return make_response(jsonify(code=401, message="登录时间过期"), 401)


api.add_resource(add_fav, "/fav/<int:id>")
api.add_resource(my_fav, "/my/fav")
