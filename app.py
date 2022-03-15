from flask import Flask
import settings
from singlefile_blueprint import user_bp
from package_blueprint import goods_bp

print('-----当前文件名------', __name__)
# 初始化Flask对象，参数如下:
# import_name为当前 Flask 程序所指定的包(模块)，__name__指明为当前文件作为主入口文件，当前文件所在目录作为根目录
# static_url_path 静态文件访问路径，可以不传，默认为：/ + static      如访问静态文件：http://127.0.0.1:5000/static/screenshot.png
# static_folder 静态文件存储的文件夹，可以不传，默认为 static
# template_folder 模板文件存储的文件夹，可以不传，默认为 templates
app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')


# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/user')   # 注册单文件蓝图
app.register_blueprint(goods_bp, url_prefix='/goods')   # 注册包蓝图


# flask配置:字典的形式访问设置
# app.config.get(key)
# app.config[key]
# 导入配置三种方式:
# 方式一、从配置对象中加载(可继承复用，但一些敏感数据暴露在代码中，用于一些默认配置)
class FlaskDevConfig:
    SECRET_KEY = 'TPmi4aLWRbyVq8zu9v82dWYW1'
    DEBUG = True
app.config.from_object(FlaskDevConfig)
# 方式二、从配置文件中加载(配置文件独立，保护敏感配置数据，但无法继承，且配置文件目录固定在代码中不灵活)
# app.config.from_pyfile('settings.py')
# 方式三、从环境变量中加载，实际也是读取配置文件，只是配置文件名保存在OS环境中(配置文件独立，保护敏感配置数据，配置文件目录不固定灵活，只需指定环境变量名及配置路径即可在多处配置好启动；不方便，得记得环境变量名并设置)
# app.config.from_envvar('FLASK_ENV_NAME')    # pycharm启动时需要在配置里指定
# app.config.from_envvar('FLASK_ENV_NAME', silent=False)  # silent指定当系统环境变量中没有设置相应值时是否抛出异常，默认False，报错通知无此环境，True忽略 则继续运行
# Linux/Mac设置环境变量 export 变量名=变量值      如 export FLASK_ENV_NAME='settings.py'
# Linux/Mac读取环境变量 echo $变量名            如 echo $FLASK_ENV_NAME
# 终端设置环境变量执行 export FLASK_ENV_NAME='settings.py'   !!!此环境变量只在此终端环境有效
# 然后终端执行 python3 app.py 运行


@app.route('/')
def hello_world():
    print('SECRET_KEY--------', app.config.get('SECRET_KEY'))
    return 'Hello World!'





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
