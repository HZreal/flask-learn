from flask import Flask
from singlefile_blueprint import user_bp
from package_blueprint import goods_bp


app = Flask(__name__)


# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/user')   # 注册单文件蓝图
app.register_blueprint(goods_bp, url_prefix='/goods')   # 注册包蓝图


@app.route('/')
def hello_world():
    print('SECRET_KEY--------', app.config.get('SECRET_KEY'))
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
