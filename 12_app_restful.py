from flask import Flask
from flask_restful import Api, Resource
from restful_blueprint import user_bp



app = Flask(__name__)


api = Api(app)   # Api对象相当于收集类视图、url并建立关联后，传给Flask app

class UseFlaskRestfulView(Resource):
    def get(self):
        return {'code': 0, 'msg': 'success'}

    def post(self):
        return {'code': 0, 'msg': 'success'}

# 建立类视图与url的关联
api.add_resource(UseFlaskRestfulView, '/demo', endpoint='restful-demo')



# 注册蓝图(蓝图中也采用restful)
app.register_blueprint(user_bp, url_prefix='/user')



def decorator1(func):
    print('decorator1 is decorating--------')

    def wrapper(*args, **kwargs):
        print('decorator1 wrapper is called----------')
        return func(*args, **kwargs)
    return wrapper

def decorator2(func):
    print('decorator2 is decorating--------')

    def wrapper(*args, **kwargs):
        print('decorator2 wrapper is called----------')
        return func(*args, **kwargs)
    return wrapper


class AddDecoratorResource(Resource):
    """
    添加装饰器的类视图
    """
    # 1. 为类视图中的所有方法添加装饰器
    # a. 列表式添加：不区分请求方式，所有的都被装饰，decorator1先被装饰(装饰过程仅返回wrapper函数)，decorator2先被执行(实际是内部的wrapper函数先被执行)
    # method_decorators = [decorator1, decorator2]
    # 装饰机制：
    # for dec in method_decorators:
    #     get = decorator1(get)
    #     get = decorator2(get)
    #     即 get = decorator2(decorator1(get))
    # 相当于：
    #     @decorator2
    #     @decorator1
    #     def get():

    # b. 字典式添加：指定具体请求方式，加指定的装饰器
    # method_decorators = {
    #     'get': [decorator1, decorator2],
    #     'post': [decorator2],
    # }


    # 2. 为类视图中不同的方法添加不同的装饰器
    # 使用了装饰器decorator1、decorator2
    @decorator2
    @decorator1
    def get(self):
        return {'code': 0, 'msg': 'success'}

    # 使用了装饰器decorator2
    @decorator2
    def post(self):
        return {'code': 0, 'msg': 'success'}

    # 未使用装饰器
    def put(self):
        return {'code': 0, 'msg': 'success'}

api.add_resource(AddDecoratorResource, '/class_decorator')




