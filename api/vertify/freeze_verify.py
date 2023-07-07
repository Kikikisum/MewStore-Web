from flask import request, jsonify, make_response
from mysql import User, db, Order, app, Report
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Resource


#  审核找回账号(举报的类型1),id为举报id
class verfy_freeze(Resource):
    def put(self, id):
        with app.app_context():
            token = request.headers.get("Authorization")
            parser = reqparse.RequestParser()
            parser.add_argument('status', type=int, required=True, location=['form'])
            args = parser.parse_args()
            if get_expiration(token):
                uid = get_id(token)  # 用户id
                report = db.session().query(Report).filter(Report.id == id).first()
                user = db.session().query(User).filter(User.id == uid).first()
                buyer = db.session().query(User).filter(User.id == report.reporter_id).first()
                seller = db.session().query(User).filter(User.id == report.reported_id).first()
                status = user.status
                order = db.session().query(Order).filter(Order.id == report.report_order).first()
                if status == 3:
                    db.session.query(Report).filter(report.id == id).update({'status': args['status']})
                    db.session.commit()
                    dic_report = {
                        "msg": "您的举报通过,进行退款处理!",
                        "id": report.id, "reported_id": report.reported_id,
                        "report_order": report.report_order,
                        "reporter_id": report.reporter_id, "status": report.status, "type": report.type
                    }
                    # Message.on_message(self, report.reporter_id, jsonify(dic_report))
                    # 先对举报的审核状态进行更新
                    if parser['status'] == 1:
                        last = seller.money-order.price
                        money = buyer.money+order.price
                        if last >= 0:
                            dic_report = {
                                "msg": "对您尝试找回账户的举报通过，对买家进行退款处理!",
                                "id": report.id, "reported_id": report.reported_id,
                                "report_order": report.report_order,
                                "reporter_id": report.reported_id, "status": report.status, "type": report.type
                            }
                            # Message.on_message(self, report.reported_id, jsonify(dic_report))
                            db.session.query(User).filter(User.id == report.reported_id).update({'money': last})
                            db.session.query(User).filter(User.id == report.reported_id).update({'money': money})
                            db.session.commit()
                            dic_report.update("msg", "退款成功")
                            # Message.on_message(self, report.reporter_id, jsonify(dic_report))
                        else:
                            dic_report.update("msg", "对您尝试找回账户的举报通过，但您的余额不足，您将会被拉入黑名单")
                            # Message.on_message(self, report.reported_id, jsonify(dic_report))
                        return make_response(jsonify(code=201, message="通过账户找回举报成功!"))
                    else:
                        dic_report = {
                            "msg": "您的举报不通过",
                            "id": report.id, "reported_id": report.reported_id,
                            "report_order": report.report_order,
                            "reporter_id": report.reporter_id, "status": report.status, "type": report.type
                        }
                        # Message.on_message(self, report.reporter_id, jsonify(dic_report))
                        # 找回账户不通过，给举报者发送信息
                        return make_response(jsonify(code=201, message="拒绝举报成功!"), 201)

                else:
                    return make_response(jsonify(code=403, message="没有权限审核"), 401)
            else:
                return make_response(jsonify(code=401, message=""))
