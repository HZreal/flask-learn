import json

from flask import Flask

app = Flask(__name__)


# 查询路由信息
# 一、命令flask routes查看Flask应用的路由映射信息
# 二、程序中获取，flask应用对象的url_map属性保存着整个Flask应用的路由映射信息，可以通过读取这个属性获取路由信息


@app.route('/', methods=['GET'])    # 默认GET、OPTIONS(简化版GET请求，询问服务器接口信息，是否允许跨域，返回允许的请求方式请求源等)、HEAD(简化版GET请求，返回GET请求处理后的响应头，而不返回响应体)
def route_map():
    url_map = app.url_map    # werkzeug.routing.Map Object
    print('url_map-----------\n', url_map, type(url_map))
    rules = url_map.iter_rules()   # Rule对象的迭代器
    print('rules-----------\n', rules, type(rules))

    # for rule in rules:
    #     # rule对象属性：rule.endpoint获取视图名，rule.rule获取具体url路径
    #     print('viewname--------\n', rule.endpoint)
    #     print('path----------\n', rule.rule)

    return json.dumps({rule.endpoint: rule.rule for rule in rules})

@app.route('/login')
def login():
    return 'login view'



# 获取pp.url_map时必须在所有url/view之后
for rule in app.url_map.iter_rules():
    print('view:{} path:{}'.format(rule.endpoint, rule.rule))



