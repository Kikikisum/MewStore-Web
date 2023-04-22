from flask import request, jsonify
from mysql import User, Good, Report, session, Order
from flask import Flask

app = Flask(__name__)


@app.route('/manage/verify/good/', methods=['POST'])
def verify_good():
    try:
        gid = request.form.get('gid')
        good_status = request.form.get('good_status')
        session.query(Good).filter(Good.id == gid).update({'status': good_status})
        session.commit()
        good = session.query(Good).filter(Good.id == gid).all()
        return jsonify(dict(code=201, message='审核成功'))
    except Exception as e:
        print(e)


#  管理员审核举报信息
@app.route('/manage/verify/report/', methods=['POST'])
def verify_report():
    try:
        pid = request.form.get('pid')     # 举报信息的id
        report_status = request.form.get('report_status')   # 举报信息是否通过
        session.query(Report).filter(Report.id == pid).update({'status': report_status})
        session.commit()
        report = session.query(Report).filter(Report.id == pid).first()
        report_id = report.report_id
        #  通过举报时，将用户拉入黑名单
        if report_status == "1":
            user_status = 1
            good_status = 2
            session.query(User).filter(User.id == report_id).update({'status': user_status})
            session.query(Good).filter(Good.sell_id == report_id).update({'status': good_status})
            return jsonify(dict(code=201, message='审核成功'))
        else:
            return jsonify(dict(code=201, message="审核成功"))
    except Exception as e:
        print(e)


@app.route('/manage/verify/money/', methods=['POST'])
def verify_money():
    try:
        order_id = request.form.get('order_id')
        uid = request.form.get('uid')
        order = session.query(Order).filter(Order.id == order_id).first()
        good_id = order.id
        buyer_id = order.buyer_id
        user_money = session.query(User).filter(User.id == uid).first().money
        good_money = order.money
        buyer_money = session.query(User).filter(User.id == buyer_id).first().money
        session.commit()
        if user_money >= good_money:
            user_status = 0
            user_money -= good_money
            buyer_money += good_money
            session.query(User).filter(User.id == uid).update({'status': user_status, 'money': user_money})
            session.query(User).filter(User.id == buyer_id).update({'money': buyer_money})
            session.query(Good).filter(Good.id == good_id).update({'status': 2})
            session.query(User).filter(User.id == order_id).update({'status': 0})
            session.commit()
            return jsonify(dict(code=201, message='审核账号情况成功'))
        else:
            user_status = 1
            buyer_money += good_money
            session.query(User).filter(User.id == uid).update({'status': user_status, 'money': 0})
            session.query(User).filter(User.id == buyer_id).update({'money': buyer_money})
            session.commit()
            return jsonify(dict(code=201, message='审核账号情况成功'))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run()
