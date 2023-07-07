import logging
from flask import request, jsonify, make_response
from mysql import User, Good, db, app, Report
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Resource

logger = logging.getLogger(__name__)


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
                        db.session.query(Good).filter(Good.sell_id == report.reported_id).update({'status': good_status}
                                                                                                 )
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
