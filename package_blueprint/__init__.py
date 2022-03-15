from flask import Blueprint

# 通常将创建蓝图对象放到Python包的__init__.py文件中



# url_prefix='/goods'指定蓝图前缀，在app注册蓝图时若指定了，则此处无效
# static_folder、template_folder、static_url_path参数与Flask对象参数一样，设置蓝图中的静态文件、模板文件目录、静态文件url(基于前缀)
# 蓝图中若有静态文件/模板文件，则必须设置这些参数供Flask app对象读取使用
goods_bp = Blueprint('goods', __name__, url_prefix='/goods', static_folder='static', template_folder='templates', static_url_path='/static')

# 访问静态文件：http://127.0.0.1:5000/goods/static/screenshot.png


from . import goods_blueprint

