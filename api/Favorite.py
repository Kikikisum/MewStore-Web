import logging
from mysql import db, app, User, Favorite, Good
from flask import request, jsonify, Blueprint, make_response
from utils.Token import get_expiration, get_id
from flask_restful import Api, Resource
from random import shuffle
from utils.time import time_transform

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


class guess(Resource):  # 猜你喜欢
    def get(self):
        # 查询
        token = request.headers.get("Authorization")
        if get_expiration(token):
            uid = get_id(token)
            user = db.session.query(User).filter_by(id=uid).first()
            favorites = db.session.query(Favorite).filter_by(user_id=uid).all()
            fav_count = len(favorites)
            game_type = game_num = {'王者荣耀': 0, '英雄联盟': 0, '原神': 0, '绝地求生': 0, '和平精英': 0, '第五人格': 0}
            for favorite in favorites:  # 统计用户喜欢的游戏
                good = db.session.query(Good).filter_by(id=favorite.good_id).first()
                if good and good.game in game_type:
                    game_type[good.game] += 1
            fav_total = 0
            for game in game_type:
                game_rate = game_type[game] / fav_count  # 计算用户喜欢的游戏的比例
                game_num[game] = int(15 * game_rate)  # 计算推荐中用户喜欢的游戏的数量
                fav_total += game_num[game]  # 计算推荐中用户喜欢的游戏的总数
            remain = 20 - fav_total  # 计算推荐中剩余商品数量
            recommended_items = []
            for game, count in game_num.items():
                items = Good.query.filter_by(game=game, status=1).all()  # 查询用户喜欢的游戏的商品
                shuffle(items)  # 打乱喜欢的商品顺序
                items = items[:count]  # 根据数量取出用户喜欢的游戏的商品
                recommended_items.extend(items)
            remaining_items = Good.query.filter(~Good.id.in_([item.id for item in recommended_items]),
                                                Good.status == 1).all()  # 查询剩余商品
            shuffle(remaining_items)  # 打乱剩余商品顺序
            remaining_items = remaining_items[:remain]
            all_items = recommended_items + remaining_items  # 合并推荐的商品
            shuffle(all_items)  # 打乱所有推荐的商品顺序
            good_list = []
            for good in all_items:
                seller = db.session.query(User).get(good.seller_id)
                good_dict = {"id": str(good.id), "view": good.view, "content": good.content, "game": good.game,
                             "title": good.title, "picture_url": good.picture, "status": good.status,
                             'add_time': time_transform(good.add_time), "seller_id": str(good.seller_id),
                             "price": good.price, 'seller_nickname': seller.nickname,
                             'seller_profile_photo': seller.profile_photo}
                good_list.append(good_dict)
            if not good_list:
                return make_response(jsonify(code=404, message='找不到在售的商品'), 404)
            logger.debug(f'用户{user.id}获取猜你喜欢商品成功')
            # 返回结果
            return make_response(jsonify(code=200, message='获取猜你喜欢商品成功', data=good_list), 200)
        else:
            return make_response(jsonify(code=401, message="登录时间过期"), 401)


api.add_resource(add_fav, "/fav/<int:id>")
api.add_resource(my_favorite, "/my/fav")
api.add_resource(guess, '/guess')
