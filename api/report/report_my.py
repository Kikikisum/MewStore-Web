from flask import request, jsonify, make_response
from mysql import User, db, app, Report
from utils.Token import get_expiration, get_id
from flask_restful import Resource


# 查看自身所发出的举报
class my_report(Resource):
    def get(self):
        with app.app_context():
            token = request.headers.get("Authorization")
            if get_expiration(token):
                uid = get_id(token)  # 用户的id
                user = db.session.query(User).filter(User.id == uid).first()
                reports = db.session.query(Report).filter(Report.reporter_id == uid).all()
                report_list = []
                if user.status == 0 or user.status == 3:
                    for report in reports:
                        report_dict = {"id": report.id, "reported_id": report.reported_id,
                                       "report_order": report.report_order,
                                       "reporter_id": report.reporter_id, "status": report.status, "type": report.type}
                        report_list.append(report_dict)
                    return make_response(jsonify(code=201, message="查询成功", data=report_list), 201)
                else:
                    return make_response(jsonify(code=402, message="黑户或冻结用户无法查询"))
            else:
                return make_response(jsonify(code=401, message="登录过期"), 401)