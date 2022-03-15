import json
from flask import Flask, request
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)

@app.route('/request')
def request_info():
    # 请求url
    url = request.url

    # 查询参数
    query_params = request.args
    id = query_params.get('id')

    # 请求头
    headers = request.headers

    # 请求cookies
    cookies = request.cookies

    # 请求方式
    method = request.method

    # 原始body数据，bytes类型
    data = request.data

    # 表单
    form_data = request.form

    # 文件
    files = request.files

    return 'request object information'


@app.route('/uploadFile', methods=['POST'])
def upload_file():
    r = request                                     # 查看request对象
    body = request.get_data()                       # 获取原始body
    body = request.data                             # 数据流被读过则为空
    file = request.files.get('file')
    file_name = request.form.get('file_name')

    # 保存文件
    # with open('upload.txt', 'wb') as f:
    #     f.write(file.read())
    file.save('upload.txt')

    return json.dumps({'code': 0, 'msg': 'success', 'data': None})





