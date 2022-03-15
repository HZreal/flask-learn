from flask import Flask


app = Flask(__name__)


class DefaultConfig:
    """默认配置"""
    SECRET_KEY = 'TPmi4aLWRbyVq8zu9v82dWYW1'

class DevConfig(DefaultConfig):
    """开发配置"""
    DEBUG = True

class ProConfig(DefaultConfig):
    """生产配置"""
    DEBUG = False

app.config.from_object(ProConfig)
# 读取环境变量配置
# 终端创建环境变量：export PRODUCTION_CONFIG=~/Desktop/hz/Flask/flask-learn/settings.py
# 注意不能是export PRODUCTION_CONFIG='~/Desktop/hz/Flask/flask-learn/settings.py' 这样系统会在当前目录开始拼接字符串内的路径
# app.config.from_envvar('PRODUCTION_CONFIG')



@app.route('/')
def hello_world():
    print('SECRET_KEY--------', app.config.get('SECRET_KEY'))
    return 'Hello World!'




# 终端命令启动 flask run -h 0.0.0.0 -p 8888  默认读取名为FLASK_APP的环境变量，FLASK_APP的值即是启动的对象
# 生产模式或者开发模式通过FLASK_ENV环境变量指明，export FLASK_ENV=production 运行在生产模式，未指明则默认为此方式；export FLASK_ENV=development运行在开发模式
#  flask run  等价于  python -m flask run
# if __name__ == '__main__':
#     app.run()