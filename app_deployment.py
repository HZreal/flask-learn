from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/doc')
def route_map():
    """
    主视图，返回所有视图网址
    """
    rules_iterator = app.url_map.iter_rules()
    return jsonify({rule.endpoint: rule.rule for rule in rules_iterator if rule.endpoint not in ('route_map', 'static')})



if __name__ == '__main__':
    app.run()






