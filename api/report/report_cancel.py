from flask import request, jsonify, make_response
from mysql import User, db, Order, app, Report
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Resource
from api.chat.chat import Message


# 卖家对取消交易的处理，由管理员员执行
# 卖家对取消交易的回应，管理员进行处理,damage为-1时拒绝取消交易，damage为0时账户无受损，1为轻微受损，2为严重受损
class cancel_Order(Resource):
    def post(self, id):
        with app.app_context():
            token = request.headers.get("Authorization")
            parser = reqparse.RequestParser()
            parser.add_argument('id', type=int, required=True, location=['form'])  # 举报的id
            parser.add_argument('damage', type=int, required=True, location=['form'])
            args = parser.parse_args()
            if get_expiration(token):
                uid = get_id(token)
                user = db.session.query(User).filter(User.id == uid).first()
                report = db.session.query(Report).filter(Report.id == args['id']).first()
                order = db.session.query(Order).filter(Order.id == report.report_order).first()
                buyer = db.session.query(User).filter(User.id == report.reporter_id).first()
                seller = db.session.query(User).filter(User.id == report.reported_id).first()
                if user.status == 3:
                    report_dict = {"msg": "您的取消交易操作被卖家拒绝!","id": report.id, "reported_id": report.reported_id,
                                   "report_order": report.report_order,
                                   "reporter_id": report.reporter_id, "status": report.status, "type": report.type
                                   }
                    if args['damage'] == -1:
                        db.session.query(Report).filter(Report.id == args['id']).upadate({"status": -1})
                        db.session.commit()
                        # Message.on_message(Message, report.reporter_id, jsonify(report_dict))
                    else:
                        db.session.query(Report).filter(Report.id == args['id']).upadate({"status": 1})
                        db.session.commit()
                        if args['damage'] == 0:  # 全额返还
                            money = seller.money-order.price
                            last = buyer.money+order.price
                            if money < 0:
                                report_dict.update("msg", "您的账户余额不足，您被设置为黑户")
                                #Message.on_message(Message, report.reported_id, jsonify(report_dict))
                                db.session.query(User).filter(User.id == report.reported_id).update({'money': 0})
                            else:
                                db.session.query(User).filter(User.id == report.reported_id).update({'money': money})
                            db.session.query(User).filter(User.id == report.reporter_id).update({'money': last})
                            db.session.commit()
                            report_dict.update("msg", "您的交易金已全部退回您的钱包!")
                            # Message.on_message(Message, report.reporter_id, jsonify(report_dict))
                        if args['damage'] == 1:
                            money = seller.money - order.price*0.7
                            last = buyer.money + order.price*0.7
                            if money<0:
                                report_dict.update("msg", "您的账户余额不足，您被设置为黑户")
                                Message.on_message(Message, report.reported_id, jsonify(report_dict))
                                db.session.query(User).filter(User.id == report.reported_id).update({'money': 0})
                            else:
                                db.session.query(User).filter(User.id == report.reported_id).update({'money': money})
                            db.session.query(User).filter(User.id == report.reporter_id).update({'money': last})
                            db.session.commit()
                            report_dict.update("msg", "您的交易金的70%退回您的钱包!")
                            # Message.on_message(Message, report.reporter_id, jsonify(report_dict))
                        if args['damage'] == 2:
                            report_dict.update("msg", "您的交易金不予以返还!")
                            # Message.on_message(Message, report.reporter_id, jsonify(report_dict))
                        return make_response(jsonify(code=201, message="审核成功!"), 201)
                else:
                    return make_response(jsonify(code=401, message="没有权限审核"), 401)
            else:
                return make_response(jsonify(code=401, message="登录过期"), 401)