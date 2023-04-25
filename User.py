from flask import request, jsonify
from mysql import User, Good, session, Order
from token import get_status, get_expiration, get_id
from flask import Flask

app = Flask(__name__)


# 卖家发出找回账号请求
@app.route('/user/return/account/', methods=['POST'])
def return_account():
    try:
        token = request.form.get('token')
        if get_expiration(token):
            id = get_id(token)  # 用户id
            user_status = get_status(token)
            order_id = request.form.get('order_id')  # 对订单发起的账号请求的订单id
            user = session.query(User).filter(User.id == id).first()
            order = session.query(Order).filter(Order.id == order_id).first()
            good_id = order.good_id
            good_status = session.query(Good).filter(Good.id == good_id).first().status
            if good_status == 3:
                if user_status == 1:
                    return jsonify(dict(code=201, message='黑户没有权限申请'))
                else:
                    if user_status == 0 or user_status == 3:
                        session.query(User).filter(User.id == id).update({'status': 2})
                        session.commit()
                        return jsonify(dict(code=201, message='账号找回申请成功'))
                    else:
                        return jsonify(dict(code=201, message='被冻结状态没有权限申请'))
            else:
                return jsonify(dict(code=201, message='订单还未完成，不可找回账号'))
        else:
            return jsonify(dict(code=401, message="登录时间过期"))

    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run()
