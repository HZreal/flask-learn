import functools
from datetime import timedelta, datetime
from flask import Flask, g, request, abort, current_app, jsonify
from flask_restful import Api, Resource, reqparse
import jwt, redis

app = Flask(__name__)

class FlaskDecConfig:
    JWT_SECRET = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA'

    JWT_EXPIRY_HOURS = 2
    JWT_REFRESH_DAYS = 14

app.config.from_object(FlaskDecConfig)

api = Api(app)

redis_cli = redis.Redis(host='127.0.0.1', port=6379, db=0)


# jwt 认证
# 1. 基于pyjwt库封装生成/校验token工具
# 2. 登录成功后，给客户端返回token、refresh_token，这两个token过期时间不同，且可以在payload中添加字段以区分
# 3. 请求中间件在headers中获取token并校验解析，验证成功则可进入视图
# jwt token 刷新
# 1. token过期后，客户端携带refresh_token请求刷新token的接口，获取新的token，若refresh_token也过期，客户端需要重新登录
# jwt token 禁用
# 分析: 由于已经签发出去的未过期的token在客户端可能很多，可能在多端，无法处理，所以只能处理当前生成的最新token，将之保存到白名单
# 如修改密码后，需要禁用曾经的token，可以:
# 1. 修改密码并生成新token，然后清除若存在的白名单并创建白名单保存此token，注意必须先清除可能已存在的白名单再创建，且白名单需要设置有效期，与token有效期一致即可
# 2. 在登录成功返回token之前，若存在白名单，则此token也应添入。
# 3. 认证逻辑只需在token认证通过后，判断是否也在白名单即可，不在白名单表示被禁用




class JWTEncodeDecodeToolHandler:
    """
    封装的JWT处理类，  生成、验证token
    """
    JWT_ALGORITHM = 'HS256'

    def __init__(self, secret=None):
        self.secret = secret or current_app.config['JWT_SECRET']

    def generate_jwt(self, payload, expiry):
        """
        生成JWT token
        :param payload:
        :param expiry:     unix时间戳
        :return:
        """
        payload.update({'exp': expiry})
        return jwt.encode(payload, key=self.secret, algorithm=self.JWT_ALGORITHM)

    def verify_jwt(self, token):
        """
        验证token是否有效
        :param token:
        :return:
        """

        try:
            payload = jwt.decode(token, key=self.secret, algorithms=[self.JWT_ALGORITHM])
        # except jwt.PyJWTError:
        except Exception as e:
            print(e)
            payload = None

        return payload

def save_token_if_whitelist_exist(token, user_id):
    # 判断是否有该用户对应的白名单，若有则将此登录生成的token存入白名单
    key = 'user:{}:token'.format(user_id)
    if redis_cli.exists(key):
        # 将token加入到白名单中
        redis_cli.sadd(key, token)

def verify_token_in_redis(user_id, token):

    key = 'user:{}:token'.format(user_id)
    # 判断该用户是否有白名单(如果有, 说明修改过密码)
    if redis_cli.exists(key):
        # 判断该token是否在白名单中
        if redis_cli.sismember(key, token):
            # 如果在, 允许访问
            print("是新token, 允许访问")
        else:
            # 如果不在, 重新登录
            print('是旧token, 需要重新登录')
            abort(401)
    else:
        print("没有修改过密码. 允许访问")

@app.before_request
def jwt_auth_middleware():
    """
    请求钩子，认证中间件
    :return:
    """
    # 获取请求头中的token
    # Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb21lIjoicGF5bG9hZCJ9.4twFt5NiznN84AWoo1d7KO1T_yoc0Z6XOpOVswacPZg

    # 定义默认值，避免其他地方从g中取值报错；要么函数体不论if、else,最终必有定义这两个数据
    g.user_id = None
    g.is_refresh = False

    token = request.headers.get('Authorization')
    if token is not None and token.startswith('Bearer '):
        # 取token进行验证
        payload = JWTEncodeDecodeToolHandler().verify_jwt(token[7:])

        if payload is not None:
            user_id = payload.get('user_id')
            g.user_id = user_id
            g.is_refresh = payload.get('is_refresh', False)   # 若解析的是refresh_token, 则可以得到is_refresh=True

            # 用于验证该用户redis白名单是否存在token
            verify_token_in_redis(user_id, token)

def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if g.user_id is not None and g.is_refresh == False:       # 认证通过且是一个普通access token，而不是refresh token
            return func(*args, **kwargs)
        else:
            # abort(401)
            return {'message': 'Invalid token'}, 401

    return wrapper


# 登录/刷新token
class AuthorizationResource(Resource):
    """
    post: 登录认证，返回token、 refresh_token
    put: 刷新access token, 不返回refresh_token(前端不变)，只返回access token，
    """

    def _generate_tokens(self, user_id, refresh=True):
        """
        生成access token，refresh_token
        :param user_id: the id of authenticated user
        :param refresh: whether refresh the access token
        :return: access token and refresh token by default, only access token when refresh is False.
        """

        # 生成 access token
        expiry = datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRY_HOURS'])
        access_token = JWTEncodeDecodeToolHandler().generate_jwt({'user_id': user_id}, expiry)

        # 是否生成refresh_token
        if refresh:
            # 默认登录接口，需要生成refresh token，也表示refresh token过期
            exipry = datetime.utcnow() + timedelta(days=current_app.config['JWT_REFRESH_DAYS'])
            refresh_token = JWTEncodeDecodeToolHandler().generate_jwt({'user_id': user_id, 'is_refresh': True}, exipry)      # payload增加is_refresh表示这是refresh token
        else:
            # refresh_token无需改变
            refresh_token = None

        return access_token, refresh_token


    def post(self):
        """
        登录，获取Token
        :return: access Token and refresh Token
        """

        print('这里模拟用户名密码正确，验证码正确，基本认证通过')

        user_id = 524
        token, refresh_token = self._generate_tokens(user_id=user_id)

        # 不影响一般登录，只有在白名单有效时间(修改密码的2小时内)内会执行，这个登录可能位于不同的端
        save_token_if_whitelist_exist(token, user_id)

        return {'access_token': token, 'refresh_token': refresh_token}, 200

    def put(self):
        """
        刷新 access token  请求头中: Authorization传refresh token，为 Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1MjQsImV4cCI6MTY1MzA0NTc2NH0.D8BgUtK5A0uGttC98WNvGCRoyQ5J8Y9awy_hmjy65aY
        :return:  获取access_token
        """
        if g.user_id is not None and g.is_refresh is True:    # 说明refresh token有效，则刷新access token
            token, fresh_token = self._generate_tokens(user_id='user_id', refresh=False)
            return {'token': token}
        else:
            return {'msg': 'Invalid refresh token'}, 403


class ModifyPassword(Resource):
    """
    需求：当修改密码时，需要生成新token，旧的token应当禁用(包括当前端，其他端)
    解决：在redis中使用set类型充当白名单，保存新生成的token，并在白名单有效期内，其他由于登录创建的新token也存入其中，直至白名单过期。
         因此登录接口增添：生成token后，会判断白名单的存在，存在则存入token；如函数save_token_if_whitelist_exist
         验证中间件增添：token认证通过后，若白名单查不到则为旧token，拒绝；如函数verify_token_in_redis()

         中间件验证token通过，先从redis白名单中判断是否存在该用户的key=user:{}:token的记录；
            若不存在记录，说明无白名单，放行，进入视图进行业务处理。
            若存在记录，说明白名单有效存在，于是判断请求的token是否在set白名单中：
                若在，说明认证成功的是修改密码生成的新token，有效，则放行。
                若不在，说明是旧的被禁token，返回403，不再处理业务逻辑。
    """

    def put(self):
        """
        修改密码，生成新token，禁用旧的token
        :return:
        """
        print('模拟修改密码完成。。。')

        user_id = 524
        key = 'user:{}:token'.format(user_id)

        # 不管是什么端(Android/IOS/web端)请求，只要是修改密码完成，都要清空已有的白名单 !!! 使其他端的旧token均踢出白名单，失效
        if redis_cli.exists(key):
            redis_cli.delete(key)

        # 生成 access token
        access_token = JWTEncodeDecodeToolHandler().generate_jwt({
            'user_id': user_id},
            expiry=datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRY_HOURS'])
        )

        # 由于修改密码，新建一个白名单并记录新token
        redis_cli.sadd(key, access_token)
        # 设置有效期
        redis_cli.expire(key, 60 * 60 * 2)

        return {'token': access_token, 'msg': 'password changed successfully'}



api.add_resource(AuthorizationResource, '/authorization')
api.add_resource(ModifyPassword, '/change_password')



@app.route('/doc')
def route_map():
    """
    主视图，返回所有视图网址，无需认证
    """
    rules_iterator = app.url_map.iter_rules()
    return jsonify({rule.endpoint: rule.rule for rule in rules_iterator if rule.endpoint not in ('route_map', 'static')})


@app.route('/user_info')
@login_required
def user_info():
    """
    用户信息，需要认证
    :return:
    """
    print('authenticated, you can access this view.')
    return jsonify({'code': 0, 'msg': 'user info', 'data': {'id': 1, 'name': 'huang'}})





