from flask import Blueprint
from flask_restful import Api
from .good_get import good_get
from .good_status import good_status


good = Blueprint('fav', __name__)
api = Api(good)


api.add_resource(good_status, "good/<int:id>")
api.add_resource(good_get, "/good/status")
