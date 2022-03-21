import json
from flask import Flask, request, render_template, redirect, jsonify, make_response, session



app = Flask(__name__)



@app.route('/response_templates')
def response_templates():
    """响应模板"""
    context = dict(
        my_str='huang',
        my_int=520
    )
    # jinja2模板，传参直接传变量名和值，若要传字典则 **字典转换成关键字传参
    # return render_template('index.html', my_str='huang', my_int=520)
    return render_template('index.html', **context)

@app.route('/response_redirect')
def response_redirect():
    """响应重定向"""
    return redirect('https://www.baidu.com')

@app.route('/response_json')
def response_json():
    """响应JSON"""
    data_dict = {
        'code': 0,
        'msg': 'success',
        'data': None
    }
    # return json.dumps(data_dict)   # 仅将响应内容设置为json，其他信息未设置如响应头中的Content-type可能还是text/plain文本
    return jsonify(data_dict)     # 设置了Content-type='application/json'

@app.route('/make_response_status_headers')
def make_response_status_headers():
    """设置响应状态码、响应头信息"""
    body = 'make_response_status_headers, you can check status or headers in response'
    status = 200
    headers = {'username': 'huang'}

    # 方式一、以三元祖(响应体body, 状态码status, 响应头headers)的方式返回，可部分传
    # return body, status, headers

    # 方式二、使用make_response函数创建response对象
    response = make_response(body)
    response.headers['username'] = 'huang'
    response.status = 200
    return response










