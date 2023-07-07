from flask import request, jsonify
from mysql import Good, db
from flask import Flask
from utils.Token import get_expiration

app = Flask(__name__)


#   获取各个商品的情况
@app.route('/good/view/<int:id>/', methods=['GET'])
def view():
    try:
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

    except Exception as e:
        print(e)


@app.route('/good/view/<int:good_status>/', methods=['GET'])
def view_status():
    try:
        token = request.headers.get("Authorization")
        status = request.form.get("status")
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
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run()