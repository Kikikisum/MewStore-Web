import logging
from flask import request, jsonify, Blueprint, make_response
from mysql import User, Good, db, Order, app, Report
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Api, Resource
from chat.chat import Message

verify = Blueprint('verify', __name__)
api = Api(verify)
logger = logging.getLogger(__name__)


# 管理员审核商品
class verify_good(Resource):
    def put(self, id):
        with app.app_context():
            token = request.headers.get("Authorization")
            parser = reqparse.RequestParser()
            parser.add_argument('status', type=int, required=True, location=['form'])
            args = parser.parse_args()
            if get_expiration(token):
                uid = get_id(token)  # 用户id
                user = db.session().query(User).filter(User.id == uid).first()
                status = user.status
                if status == 3:
                    good = db.session.query(Good).filter(Good.id == id).first()
                    if not good:
                        return make_response(jsonify(code=404, message="无该商品可审核"), 404)
                    db.session.query(Good).filter(Good.id == id).update({'status': args['status']})
                    db.session.commit()
                    dic_good = {
                        'msg': "您的商品审核完毕",
                        'id': good.id, 'view': good.view, 'content': good.content, 'game': good.game,
                        'title': good.title, 'status': good.status, 'sell_id': good.sell_id
                    }
                    # Message.on_message(Message, good.seller_id, jsonify(message=dic_good))
                    logger.debug("商品审核系统消息发放")
                    return make_response(jsonify(code=201, message='审核成功'), 201)
                else:
                    return make_response(jsonify(code=403, message="没有权限审核"), 403)
            else:
                return make_response(jsonify(code=401, message="登录时间过期"), 401)


#  管理员审核黑户的举报(类型3)
class verify_report(Resource):
    def put(self, id):
        with app.app_context():
            token = request.headers.get("Authorization")
            parser = reqparse.RequestParser()
            parser.add_argument('status', type=int, required=True, location=['form'])
            args = parser.parse_args()
            if get_expiration(token):
                uid = get_id(token)  # 用户id
                user = db.session().query(User).filter(User.id == uid).first()
                status = user.status
                if status == 3:
                    report = db.session.query(Report).filter(Report.id == id).first()
                    if not report:
                        return make_response(jsonify(code=404, message="无举报可审核"), 404)
                    db.session.query(Report).filter(report.id == id).update({'status': args['status']})
                    db.session.commit()
                    if args['status'] == 1:
                        user_status = 1
                        good_status = 2
                        db.session.query(User).filter(User.id == report.reported_id).update({'status': user_status})
                        db.session.query(Good).filter(Good.sell_id == report.reported_id).update({'status': good_status})
                        db.session.commit()
                        dic_report = {
                            "msg": "您被拉入黑名单",
                            "id": report.id, "reported_id": report.reported_id,
                            "report_order": report.report_order,
                            "reporter_id": report.reporter_id, "status": report.status, "type": report.type
                        }
                        logger.debug("给被举报者发送被举报成功的系统消息")
                        # Message.on_message(self, report.reported_id, jsonify(message=dic_report))
                        dic_report.update("msg", "您的举报成功!")
                        # Message.on_message(self, report.reporter_id, jsonify(message=dic_report))
                        logger.debug("给举报者发送举报成功的系统消息")
                    else:
                        dic_report = {
                            "msg": "您的举报不通过",
                            "id": report.id, "reported_id": report.reported_id,
                            "report_order": report.report_order,
                            "reporter_id": report.reporter_id, "status": report.status, "type": report.type
                        }
                        # Message.on_message(self, report.reporter_id, jsonify(message=dic_report))
                        logger.debug("给举报者发送举报失败的系统消息")
                    return make_response(jsonify(code=201, message='审核成功'), 201)
                else:
                    return make_response(jsonify(code=403, message="没有权限审核"), 401)
            else:
                return make_response(jsonify(code=401, message="登录时间过期"), 401)


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
                 return make_response(jsonify(code=401, message="登录时间过期"), 401)


api.add_resource(verify_good, '/verify/good/<int:id>')
api.add_resource(verify_report, '/verify/report/<int:id>')
api.add_resource(verfy_freeze, '/verify/freeze/<int:id>')
