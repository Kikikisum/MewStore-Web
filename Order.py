from flask import request, jsonify
from mysql import User, Good, Report, session, Order
from flask import Flask

app = Flask(__name__)


@app.route('/good/order/ini/', methods=['POST'])
def ini():
    try:
        id = request.form.get('id')  # 买方的id
        good_id = request.form.get('good_id')   # 商品的id
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
                            user_money -= money
                            sid = good.sell_id
                            order = Order(status=1, buyer_id=id, seller_id=sid, buyer_status=1,
                                          seller_status=1, good_id=good.id, money=money)
                            session.query(User).filter(User.id == id).update({'money': user_money})
                            session.add(order)
                            session.flush()
                            session.commit()
                            data = {'id': order.id, 'status': order.status, 'good_id ': good.id, 'buyer_id':
                                    order.buyer_id, 'sell_id': order.seller_id, 'buyer_status': 1,
                                    'seller_status': 0, 'money': money
                                    }
                            return jsonify(dict(code=201, message='出价成功', data=data))
                        else:
                            return jsonify(code=403, message='出价失败', data='钱包余额不足')
    except Exception as e:
        print(e)


@app.route('/good/order/agree/', methods=['POST'])
def agree():
    try:
        order_id = request.form.get('order_id')
        status = request.form.get('status')
        good_id = session.query(Order).filter(Order.id == order_id).first().good_id
        if status == '1':
            session.query(Order).filter(Order.good_id == good_id).update({'seller_status': -1})
            session.query(Order).filter(Order.id == order_id).update({'seller_status': 1})
            session.query(Good).filter(Good.id == good_id).update({'status': 3})
            session.commit()
            return jsonify(dict(code=201, message='订单确认成功'))
        else:
            session.query(Order).filter(Order.id == order_id).update({'seller_status': -1, 'status': 0})
            session.commit()
            return jsonify(dict(code=201, message='订单拒绝成功'))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run()
