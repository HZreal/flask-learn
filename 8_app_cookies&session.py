from flask import Flask, request, make_response, session



class FlaskDevConfig:
    """配置类"""
    SECRET_KEY = 'TPmi4aLWRbyVq8zu9v82dWYW1'
    DEBUG = True    # DEBUG模式开启:后端出错会直接返回真实具体的错误信息给前端(反之关闭DEBUG模式前端只会显示Internal Server Error)，代码修改自动重启

app = Flask(__name__)

app.config.from_object(FlaskDevConfig)
app.secret_key = 'TPmi4aLWRbyVq8zu9v82dWYW1'


@app.route('/cookies')
def response_cookies():
    # 获取cookies
    print('username------', request.cookies.get('username'))
    csrftoken = request.cookies.get('csrftoken')
    sessionid = request.cookies.get('sessionid')
    print(csrftoken, '\n', sessionid)

    response = make_response('set cookies')
    # 设置cookies，set_cookie函数本质是在响应头中增加Set-Cookie字段，值为cookies键值对
    # max_age过期的秒数，expires过期时间对象/字符串，两个参数均存在时使用max_age
    response.set_cookie('username', 'huang', max_age=3600, expires=60 * 60)

    # 删除cookies
    response.delete_cookie('username')   # 实际调用的是set_cookie，设置过期时间max_age=0/expire为一个过期时间
    return response


@app.route('/response_session')
def response_session():
    # 获取session
    username = session.get('username')

    # 设置session，注意需要配置SECRET_KEY
    session['username'] = 'huang'

    return 'username in session is {}'.format(username)

# flask的session默认放在浏览器，但避免用户修改，通过SECRET_KEY进行签名



