from flask import Blueprint
from flask_restful import Api
from freeze_verify import verfy_freeze
from good_verify import verify_good
from report_verify import verify_report

verify = Blueprint('verify', __name__)
api = Api(verify)


api.add_resource(verify_good, '/verify/good/<int:id>')
api.add_resource(verify_report, '/verify/report/<int:id>')
api.add_resource(verfy_freeze, '/verify/freeze/<int:id>')
