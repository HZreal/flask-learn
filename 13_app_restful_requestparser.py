import re

from flask import Flask
from flask_restful import Api, Resource, reqparse, inputs


app = Flask(__name__)

api = Api(app)


# Flask-RESTful 提供了RequestParser类，用来帮助我们检验和转换请求数据。类似于DRF序列化器的校验
parser = reqparse.RequestParser()
# add_argument添加校验的参数:
parser.add_argument('username', type=int, required=True, action='store', help='username cannot be converted', location='args')
# 函数参数:
# required  参数是否必传，默认为可传；设置为True而未传参数时返回400 bad request
# help  参数检验错误时返回的自定义错误描述信息
# action  请求参数中出现多个同名参数时的处理方式；默认action='store' 保留出现的第一个，action='append' 以列表追加保存所有同名参数的值
# location  参数在请求数据中出现的位置，未指定时会尽可能去找，可以的值如下
#         args          Look only in the querystring
#         form          Look only in the POST body
#         headers       From the request headers
#         cookies       From http cookies
#         json          From json
#         files         From file uploads
# type  限制参数类型
#         正则表达式  inputs.regex(r'')
#         自然数  inputs.natural()
#         正整数  inputs.positive
#         url类型  inputs.url()
#         整数范围  inputs.int_range(low ,high)
# 自定义类型type
def type_mobile(mobile_str):
    """
    自定义手机号类型type
    :param mobile_str:    被校验字符串
    :return:              检验通过的字符串
    """
    if re.match(r'^1[3-9]\d{9}$', mobile_str):
        return mobile_str
    else:
        raise ValueError(f'{mobile_str} is not valid')




# 请求url  http://127.0.0.1:5000/req?username=helen&age=22&mobile=18512345678
class RestfulUseRequestParser(Resource):
    def get(self):

        # 创建RequestParser对象
        rp = reqparse.RequestParser()

        # 声明需校验的参数
        # rp.add_argument('username', type=str, required=True, location='args')
        rp.add_argument('username', type=inputs.regex(r'^h'))
        # rp.add_argument('age', action='store')
        # rp.add_argument('age', action='append')
        # rp.add_argument('age', type=inputs.natural)
        # rp.add_argument('age', type=inputs.positive)
        # rp.add_argument('age', type=inputs.date)
        rp.add_argument('age', type=inputs.int_range(10, 30))
        rp.add_argument('mobile', type=type_mobile)                      # 自定义type类型
        rp.add_argument('password', location='json')                     # password参数只能在json中
        rp.add_argument('password', location=['form', 'headers'])        # 指明可能的多个位置


        # 执行检验
        args = rp.parse_args()

        # 取已通过检验的参数(字典或者对象的方式取)
        username1 = args['username']
        username2 = args.username
        age = args['age']
        mobile = args['mobile']

        return {'code': 0, 'msg': 'success', 'data': {'username': username1, 'age': age, 'mobile': mobile}}


api.add_resource(RestfulUseRequestParser, '/req', endpoint='req-demo')







