import json

from flask import Flask
from werkzeug.routing import Map, Rule

app = Flask(__name__)


@app.route('/', methods=['GET'], endpoint='route_map')
def route_map():
    url_map: Map = app.url_map  # werkzeug.routing.Map Object
    print('url_map-----------\n', url_map, type(url_map))
    rules = url_map.iter_rules()  # werkzeug.routing.Rule对象的迭代器
    print('rules-----------\n', rules, type(rules))

    return json.dumps({rule.endpoint: rule.rule for rule in rules})


@app.route('/login')
def login():
    return 'login view'


@app.route('/index')
def index():
    return 'index view'


for rule in app.url_map.iter_rules():
    print('view:{} path:{}'.format(rule.endpoint, rule.rule))
