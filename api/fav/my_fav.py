import logging
from mysql import db, app, Favorite
from flask import request, jsonify, make_response
from utils.Token import get_expiration, get_id
from flask_restful import Resource

logger = logging.getLogger(__name__)


#  获取自身收藏的商品
class my_favorite(Resource):
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
