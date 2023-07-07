from flask import request, jsonify, make_response
from mysql import User, db, Order, app, Report
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Resource
from utils.snowflake import id_generate
from api.chat.chat import Message


# 对订单举报
class ini_report(Resource):
    def post(self):
        with app.app_context():
            parser = reqparse.RequestParser()
            parser.add_argument('order_id', type=int, required=True, location=['form'])
            parser.add_argument('content', type=str, required=True, location=['form'])
            parser.add_argument('type', type=int, required=True, location=['form'])
            token = request.headers.get("Authorization")
            args = parser.parse_args()
            if get_expiration(token):
                uid = get_id(token)  # 用户的id
                user = db.session.query(User).filter(User.id == uid).first()
                if user.status == 1 or user.status == 2:
                    return make_response(jsonify(code=401, message="用户是黑名单或处于冻结状态"), 401)
                else:
                    order = db.session.query(Order).filter(Order.id == args['order_id']).first()
                    report = Report(id=id_generate('report'), reported_id=order.seller_id, report_order=args['order_id'],
                                    reporter_id=uid, status=0, content=args['content'], type=args['type'])
                    db.session.add(report)
                    db.session.commit()
                    if args['type'] == 3:
                        report_dict = {"msg": "您的订单被买家申请取消交易!", "id": report.id, "reported_id": report.reported_id,
                                       "report_order": report.report_order,
                                       "reporter_id": report.reporter_id, "status": report.status, "type": type}
                        # Message.on_message(Message, report.reported_id, jsonify(report_dict))
                    return make_response(jsonify(code=200, message="举报成功"), 200)
            else:
                return make_response(jsonify(code=401, message="登录过期"), 401)
            