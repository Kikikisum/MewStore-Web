from flask import Blueprint
from flask_restful import Api
from .guess import guess
from .add_fav import Fav_add
from .my_fav import my_favorite

fav = Blueprint('fav', __name__)
api = Api(fav)


api.add_resource(Fav_add, "/fav/<int:id>")
api.add_resource(my_favorite, "/my/fav")
api.add_resource(guess, '/guess')
