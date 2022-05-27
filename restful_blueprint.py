from flask import Blueprint
from flask_restful import Api, Resource


user_bp = Blueprint('user', __name__)


# 把蓝图对象交给Api对象进行视图、url及其关联的收集
user_api = Api(user_bp)


class UseProfileView(Resource):
    def get(self):
        return {'code': 0, 'msg': 'success'}

    def post(self):
        return {'code': 0, 'msg': 'success'}





# 建立类视图与url的关联
user_api.add_resource(UseProfileView, '/profile', endpoint='profile')

