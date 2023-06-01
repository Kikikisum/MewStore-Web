import logging
from flask import request, jsonify, Blueprint, make_response
from mysql import User, Good, db, Order, app, Report
from utils.Token import get_expiration, get_id
from flask_restful import reqparse, Api, Resource
from chat.chat import

verify = Blueprint('verify', __name__)
api = Api(verify)
logger = logging.getLogger(__name__)


# 管理员审核商品
class verify_good(Resource):
    def put(self,id):
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
                    return make_response(jsonify(code=201, message='审核成功'), 201)
                else:
                    return make_response(jsonify(code=403, message="没有权限审核"), 403)
            else:
                return make_response(jsonify(code=401, message="登录时间过期"), 401)


#  管理员审核举报信息
class verify_report(Resource):
    def put(self,id):
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
                    return make_response(jsonify(code=201, message='审核成功'), 201)
                else:
                    return make_response(jsonify(code=403, message="没有权限审核"), 401)
            else:
                return make_response(jsonify(code=401, message="登录时间过期"), 401)


#  审核找回账号,id为举报id
class verfy_freeze(Resource):
    def put(self,id):
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
                    pass
                else:
                    return make_response(jsonify(code=403, message="没有权限审核"), 401)
            else:
                 return make_response(jsonify(code=401, message="登录时间过期"), 401)


api.add_resource(verify_good, '/verify/good/<int:id>')
api.add_resource(verify_report, '/verify/report/<int:id>')
api.add_resource(verfy_freeze, '/verify/freeze/<int:id>')
