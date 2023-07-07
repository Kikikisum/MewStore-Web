import logging
from mysql import db, User, Favorite, Good
from flask import request, jsonify, make_response
from utils.Token import get_expiration, get_id
from flask_restful import Resource
from random import shuffle
from utils.time import time_transform

logger = logging.getLogger(__name__)


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
