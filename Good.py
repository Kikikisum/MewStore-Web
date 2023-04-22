from flask import request, jsonify
from mysql import User, Good, Report, session, Order
from flask import Flask

app = Flask(__name__)


#   获取各个商品的情况
@app.route('/good/view/{id}/', methods=['GET'])
def view():
    try:
        id = request.form.get('id')
        good = session.query(Good).filter(Good.id == id).first()
        if not good:
            return jsonify(dict(code=404, messsage="商品不存在"))
        else:
            data = {
                'id': good.id, 'view': good.view, 'content': good.content, 'game': good.game,
                'title': good.title, 'status': good.status, 'sell_id': good.sell_id
            }
            return jsonify(dict(code=201, message="获取商品情况成功", data=data))
    except Exception as e:
        print(e)


@app.route('/good/view/{status}', methods=['GET'])
def view_status():
    try:
        status = request.form.get('status')
        good = session.query(Good).filter(Good.status == status).all()
        if not good:
            return jsonify(code=401, message="没有该状态的商品")
        else:
            list = []
            for i in good:
                data = {
                    'id': i.id, 'view': i.view, 'content': i.content, 'game': i.game,
                    'title': i.title, 'status': i.status, 'sell_id': i.sell_id
                }
                list.append(data)
            return jsonify(dict(code=200, message="查询成功", data=list))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run()