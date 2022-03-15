from flask import Flask
from utils.customConverter import MobileNumberConverter



app = Flask(__name__)

# 注册自定义的转换器  app.url_map.converter转换器字典
app.url_map.converters['mobile'] = MobileNumberConverter


@app.route('/user/<string:user_id>')   # 路径参数默认string类型
# @app.route('/user/<int:user_id>')    # /user/abc123 无法匹配
def user_info(user_id):
    print(type(user_id))
    return 'user_id is {}'.format(user_id)


# 使用自定义的转换器
@app.route('/phone/<mobile:phone_num>')   # /phone/123 不符合正则，无法匹配
def phone_info(phone_num):
    return 'phone_num is %s' % phone_num
