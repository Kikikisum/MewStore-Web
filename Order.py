from flask import request, jsonify
from mysql import User, Good, Report, session, Order
from token import get_status, get_expiration, get_id
from flask import Flask

app = Flask(__name__)


@app.route('/good/order/', methods=['POST'])
def ini():
    try:
        token = request.headers.get("Authorization")
        if get_expiration(token):
            id = get_id(token)  # 买方的id
            good_id = request.form.get('good_id')  # 商品的id
            money = request.form.get('money')
            money = int(money)
            user = session.query(User).filter(User.id == id).first()
            status = user.status
            user_money = user.money
            good = session.query(Good).filter(Good.id == good_id).first()
            good_status = good.status
            if good_status == 2:
                return jsonify(dict(code=403, message='出价失败', data="商品已被下架"))
            else:
                if good_status == 3:
                    return jsonify(dict(code=403, message='出价失败', data="商品已出售"))
                else:
                    if status == 1:
                        return jsonify(code=403, message='出价失败', data='黑户没有权限出价')
                    else:
                        if status == 2:
                            return jsonify(code=403, message='出价失败', data='用户处于被冻结状态，无法出价')
                        else:
                            if user_money >= money:
                                sid = good.sell_id
                                order = Order(status=1, buyer_id=id, seller_id=sid, buyer_status=1,
                                              seller_status=1, good_id=good.id, money=money)
                                session.add(order)
                                session.flush()
                                session.commit()
                                data = {'id': order.id, 'status': order.status, 'good_id ': good.id, 'buyer_id':
                                    order.buyer_id, 'sell_id': order.seller_id, 'buyer_status': 0,
                                        'seller_status': 0, 'money': money
                                        }
                                return jsonify(dict(code=201, message='出价成功', data=data))
                            else:
                                return jsonify(code=403, message='出价失败', data='钱包余额不足')
        else:
            return jsonify(dict(code=401, message="登录时间过期"))

    except Exception as e:
        print(e)


# 卖家接受订单
@app.route('/good/order/agree/', methods=['POST'])
def agree():
    try:
        token = request.headers.get("Authorization")
        if get_expiration(token):
            user_status = get_status(token)
            if user_status == 2 or user_status == 1:
                return jsonify(dict(code=403, message="订单确认失败", data="用户处于冻结或黑户状态"))
            order_id = request.form.get('order_id')
            status = request.form.get('status')
            good_id = session.query(Order).filter(Order.id == order_id).first().good_id
            if status == '1':
                session.query(Order).filter(Order.good_id == good_id).update({'seller_status': -1})
                session.query(Order).filter(Order.id == order_id).update({'seller_status': 1})
                session.query(Good).filter(Good.id == good_id).update({'status': 3})
                session.commit()
                return jsonify(dict(code=201, message='订单确认成功', data="成功接收订单"))
            else:
                session.query(Order).filter(Order.id == order_id).update({'seller_status': -1, 'status': 0})
                session.commit()
                return jsonify(dict(code=201, message='订单确认成功', data="成功拒绝订单"))
        else:
            return jsonify(dict(code=401, message="登录时间过期"))

    except Exception as e:
        print(e)


# 收藏订单
@app.route('/user/order/fav/<int:id>', methods=['POST'])
def fav():
    try:
        token = request.headers.get("Authorization")
        if get_expiration(token):
            oid = id  # 订单号
            fav = 2
            order = session.query(Order).filter(Order.id == oid).first()
            if not order:
                return jsonify(dict(code=404, message="收藏失败", data="该订单不存在"))
            else:
                session.query(Order).filter(Order.id == oid).update({"status": fav})
                session.commit()
                order = session.query(Order).filter(Order.id == oid).first()
                data = {'id': order.id, 'status': order.status, 'buyer_id': order.buyer_id,
                        'seller_id': order.seller_id, 'good_id': order.good_id, 'buyer_status'
                        : order.buyer_status, 'seller_status': order.seller_id, 'money':
                            order.money
                        }
                return jsonify(dict(code=201, message="收藏成功", data="收藏订单成功"))
        else:
            return jsonify(dict(code=401, message="登录时间过期"))

    except Exception as e:
        print(e)


@app.route('/user/order/pay/<int:id>',methos=['POST'])
def pay():
    try:
        token = request.headers.get("Authorization")
        if get_expiration(token):
            order_id = id
            uid = get_id(token)
            order=session.query(Order).filter(Order.id == order_id).first()
            status = get_status(token)
            if status==2 or status==1:
                return jsonify(dict(code=403, message="订单确认失败", data="用户处于冻结或黑户状态"))
            else:
                order_money=order.money
                user = session.query(User).filter(User.id == uid).first()
                money=user.money-order_money
                session.query(Order).filter(Order.id == order_id).update({'money':money})
                session.commit()
                return jsonify(dict(code=201, message='订单确认成功', data='买家确认成功'))
        else:
            return jsonify(dict(code=401, message="登录时间过期"))
    except Exception as e:
        print(e)

#  查找用户作为卖家的订单
@app.route('/user/order/sell/<int:id>',methods=['GET'])
def search_seller():
    pass

if __name__ == '__main__':
    app.run()
