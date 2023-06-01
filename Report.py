import logging
from flask import request, jsonify, Blueprint, make_response
from mysql import User, db, Order, app, Report
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Api, Resource
from utils.snowflake import id_generate

report = Blueprint('report', __name__)
api = Api(report)
logger = logging.getLogger(__name__)


# 对订单举报
class ini_report(Resource):
    def post(self):
        with app.app_context():
            parser = reqparse.RequestParser()
            parser.add_argument('order_id', type=int, required=True, location=['form'])
            parser.add_argument('content', type=str, required=True, location=['form'])
            token = request.headers.get("Authorization")
            args = parser.parse_args()
            if get_expiration(token):
                uid = get_id(token)  # 用户的id
                user = db.session.query(User).filter(User.id == uid).first()
                if user.status == 1 or user.status == 2:
                    return make_response(jsonify(code=401, message="用户是黑名单或处于冻结状态"), 401)
                else:
                    order = db.session.query(Order).filter(Order.id == args['order_id']).first()
                    report = Report(id=id_generate(1, 4), reported_id=order.seller_id, report_order=args['order_id'],
                                    reporter_id=uid, status=0, content=args['content'])
                    db.session.add(report)
                    db.session.commit()
                    return make_response(jsonify(code=200, message="举报成功"), 200)
            else:
                return make_response(jsonify(code=401, message="登录过期"), 401)


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
                for report in reports:
                    report_dict = {"id": report.id, "reported_id": report.reported_id, "report_order": report.report_order,
                                   "reporter_id": report.reporter_id, "status":report.status}
                    report_list.append(report_dict)
                return make_response(jsonify(code=201, message="查询成功", data=report_list), 201)
            else:
                return make_response(jsonify(code=401, message="登录过期"), 401)


# 查询不同状态的举报
class status_report(Resource):
    def get(self):
        with app.app_context():
            parser = reqparse.RequestParser()
            parser.add_argument('status', type=int, required=True, location=['form'])
            args = parser.parse_args()
            token = request.headers.get("Authorization")
            if get_expiration(token):
                uid = get_id(token)  # 用户的id
                user = db.session.query(User).filter(User.id == uid).first()
                if user.status == 3:
                    reports = db.session.query(Report).filter(Report.status == args['status']).all()
                    report_list = []
                    for report in reports:
                        report_dict = {"id": report.id, "reported_id": report.reported_id,
                                       "report_order": report.report_order,
                                       "reporter_id": report.reporter_id, "status": report.status}
                        report_list.append(report_dict)
                    return make_response(jsonify(code=201, message="查询成功", data=report_list), 201)
                else:
                    return make_response(jsonify(code=401, message="没有权限查询"), 201)
            else:
                return make_response(jsonify(code=401, message="登录过期"), 401)


api.add_resource(ini_report, '/report/ini')
api.add_resource(my_report, '/my/report')
api.add_resource(status_report, '/report/status')
