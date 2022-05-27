from flask import Flask, request, session, current_app, Request, g, abort
from use_current_app_in_blueprint import bp


# 一、请求上下文 request context
# 1.导入的全局变量request：并非真正意义的全局变量，而是请求上下文的对象，保存了当前本次请求的相关数据，针对多个并发请求，request实际为不同的上下文环境(这个环境是由app.app_context()构造的)
#       /articles?channel_id=123  request.args.get('channel_id') --> 123   Thread A
#       /articles?channel_id=124  request.args.get('channel_id') --> 124   Thread B
#       当上述两个并发请求，调用的都是'全局变量request'，但实际会根据每个请求创建的线程环境去取值，保证取值无误
#       可能如：request.args = {'Thread-A': 123, 'Thread-B': 124}
# 2.全局session：也是请求上下文的对象，用来记录请求会话中的信息，针对的是用户信息

# 二、应用上下文 application context 是request context 中的一个对 app 的代理，主要是帮助 request 获取当前的应用，它是伴 request 而生，随 request 而灭的
# 应用上下文对象有：current_app，g
# 1.current_app应用上下文对象，用于存储Flask app中的变量，用于在其他地方(如蓝图文件中)不方便调用Flask app对象时使用，使用方式与Flask app相同
# 可以在app 或 current_app中存储一些变量，然后在蓝图中获取这些变量，例如：
#         应用的启动脚本是哪个文件，启动时指定了哪些参数
#         加载了哪些配置文件，导入了哪些配置
#         连了哪个数据库
#         有哪些public的工具类、常量
#         应用跑再哪个机器上，IP多少，内存多大
# 2.g应用上下文对象
#     g对象作为Flask app全局的一个临时变量，充当中间媒介的作用，我们可以通过它在一次请求调用的多个函数间传递一些数据。
#     注意，虽然称为应用上下文，其每次请求都会重设这个变量!!!，也就是其数据与每个不同请求挂钩，互相之前不影响。



redis_conn = 'redis connection object'  # 模拟一个redis连接对象


app = Flask(__name__)
# 将redis连接对象保存到app对象的一个属性中
app.redis_conn = redis_conn
app.register_blueprint(bp, url_prefix='/bp')


# 创建多个Flask app  通常不会在一个文件创建多个app，多个app一般是用于分布式，在不同终端启动，这里仅作为描述current_app的demo
# 注意：启动时只能启动一个app，需要指定哪一个app启动，如export FLASK_APP=app_context:app1
# app1 = Flask(__name__)
# app2 = Flask(__name__)
# app1.redis_conn = redis_conn
# app2.redis_conn = redis_conn
#
# @app1.route('/app1')
# def use_current_app_in_multi_app_1():
#     redis_conn = current_app.redis_conn
#     return '{}'.format(redis_conn)
#
# @app2.route('/app2')
# def use_current_app_in_multi_app_2():
#     redis_conn = current_app.redis_conn
#     return '{}'.format(redis_conn)


def query_db_operation_1(user_id):
    """模拟查询数据库操作"""
    res = user_id + 1
    return res

def query_db_operation_2():
    """函数通过g对象获取参数"""
    user_id = g.user_id
    res = user_id + 1
    return res

@app.route('/user_profile')
def user_profile():
    user_id = 123

    # 调用函数并传参
    res = query_db_operation_1(user_id)

    # 通过g容器对象保存我们需要传参的变量，在需要使用变量的地方通过调用g对象获取，避免了函数直接的传参
    g.user_id = user_id
    # 调用函数不传参
    res = query_db_operation_2()
    return 'data-------{}'.format(res)




# g对象与请求钩子的结合
# 需求: 构建认证机制
# 对于特定视图需要要求用户登录才能访问     --------> 使用装饰器
# 对于所有视图，无论是否要求用户登录，都可以在视图中尝试获取用户认证后的身份信息     ---------> 使用请求钩子
# 逻辑： 在请求钩子before_request中进行用户登录认证，并将用户信息(未认证则是None)写入g对象，然后进入视图
#       若请求的视图要求登录，则会执行登录装饰器进行用户信息(g对象获取)判断，认证通过可进入视图，否则返回401

def login_required(func):
    """
    装饰器------要求登录
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        # 判断用户是否登录认证
        if g.user_id is None:                 # 未能在g中获取到user_id，表示认证失败，抛出401
            abort(401)
        else:
            return func(*args, **kwargs)      # 能在g中获取到user_id，表示认证已通过，可以进入视图即可以执行fun()

    return wrapper

@app.before_request
def authentication():
    """
    认证
    :return:
    """
    # TODO 此处利用鉴权机制（如cookie、session、jwt等）鉴别用户身份信息
    # if 已登录用户，用户有身份信息
    g.user_id = 123                    # 向g中写入user_id表示认证成功
    # else 未登录用户，用户无身份信息
    # g.user_id = None

@app.route('/dashboard')
def index():
    return 'index page that all can access'

@app.route('/user_info')
@login_required       # 登录要求装饰器，补充视图逻辑，因此在route装饰器之前
def user_info():
    return 'login required page'









# app_context 允许我们在外部使用应用上下文current_app、g
# 当在独立于flask app环境外使用current_app时，需要app_context为我们提供了应用上下文环境；正常使用flask环境，默认给我们加载了app_context，才能调用得到current_app
# 可以通过with语句进行使用
# >>> from flask import Flask
# >>> app = Flask(__name__)
# >>> app.user_id = 1
# >>> from flask import current_app
# >>> current_app.user_id   # 错误，没有上下文环境
# >>> with app.app_context():  # 借助with语句使用app_context创建应用上下文
# ...     print(current_app.user_id)
# ...
# 1


# request_context 允许我们在外部使用请求上下文request、session
# 当在独立于flask app环境外使用request时，需要request_context为我们提供了应用上下文环境
# >>> from flask import Flask
# >>> app = Flask(__name__)
# >>> request.args  # 错误，没有上下文环境
# >>> environ = {'wsgi.version':(1,0), 'wsgi.input': '', 'REQUEST_METHOD': 'GET', 'PATH_INFO': '/', 'SERVER_NAME': 'WSGI server', 'wsgi.url_scheme': 'http', 'SERVER_PORT': '80'}  # 模拟解析客户端请求之后的wsgi字典数据
# >>> with app.request_context(environ):  # 借助with语句使用request_context创建请求上下文
# ...     print(request.path)
# ...
# /



# 上下文实现的原理
# ThreadLocal 线程局部变量



