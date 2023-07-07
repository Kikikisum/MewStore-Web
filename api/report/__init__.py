from flask import Blueprint
from flask_restful import Api
from report_cancel import cancel_Order
from report_ini import ini_report
from report_status import status_report
from report_my import my_report
from report_type import type_report

report = Blueprint('report', __name__)
api = Api(report)


api.add_resource(ini_report, '/report/ini')
api.add_resource(my_report, '/my/report')
api.add_resource(status_report, '/report/status')
api.add_resource(cancel_Order, '/cancel/order')
api.add_resource(type_report, '/report/type')
