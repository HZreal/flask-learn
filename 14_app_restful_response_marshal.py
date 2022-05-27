from flask import Flask
from flask_restful import Api, Resource, fields, marshal_with, marshal
import re
from flask import make_response, current_app
from flask_restful.utils import PY3
import json

app = Flask(__name__)

api = Api(app)


# 用来模拟要返回的数据对象的类
class User(object):
    def __init__(self, user_id, name, age):
        self.user_id = user_id
        self.name = name
        self.age = age


# 声明需要序列化处理的字段
resoure_fields = {
    'user_id': fields.Integer,
    'name': fields.String
}


class DemoResource(Resource):

    # 采用函数的方式
    def get(self):
        user = User(1, 'huang', 22)
        # marshal函数将模型类对象序列化成字典：参数data为模型类，fields为序列化字段，envelope(信封)表示将序列化后的字典内嵌到一个key='envelope值'的字典中
        data = marshal(data=user, fields=resoure_fields, envelope=None)
        return data, 200, {}
        # return {'code': 0, 'msg': 'success', 'data': data}, 200, {}

    # 采用装饰器的方式，实际是对marshal函数的封装调用，详看源码
    @marshal_with(resoure_fields, envelope='data')   # marshal_with为实例装饰器，先初始化实例，在装饰时调用__call__，返回wrapper，对post函数返回值拦截处理后再返回
    def post(self):
        user = User(1, 'huang', 22)
        return user


api.add_resource(DemoResource, '/marshal')






# flask_restful视图函数中返回时可以直接返回字典是因为自动被转成JSON
# 转换函数output_json的源码在flask_restful.representations.json.output_json

# representation装饰器可以根据不同的Content-Type进行不同的自定义序列化返回格式
@api.representation('application/json')
def output_json(data, code, headers=None):
    """重写自定义output_json函数，补充逻辑，返回自定义的json格式"""


    # ****************************自定义格式添加*******************************
    # data = {"user_id": 1, "name": "huang"}
    if 'msg' not in data:
        data = {
            'code': 0,
            'msg': 'success',
            'data': data
        }
    # {"code": 0, "msg": "success", "data": {"user_id": 1, "name": "huang"}}
    # ***********************************************************************

    settings = current_app.config.get('RESTFUL_JSON', {})

    # If we're in debug mode, and the indent is not set, we set it to a
    # reasonable value here.  Note that this won't override any existing value
    # that was set.  We also set the "sort_keys" value.
    if current_app.debug:
        settings.setdefault('indent', 4)
        settings.setdefault('sort_keys', not PY3)

    # always end the json dumps with a new line
    # see https://github.com/mitsuhiko/flask/pull/1262
    dumped = json.dumps(data, **settings) + "\n"

    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp
