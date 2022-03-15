from flask import Blueprint

# 蓝图(集url、视图、静态文件、模板等一体的模块，便于某个功能模块的管理和复用，类似于Django的子应用)
# 蓝图实际可以理解为是一个存储一组视图方法的容器对象
# 具有如下特点：
# 一个应用可以具有多个Blueprint
# 可以将一个Blueprint注册到任何一个未使用的URL下比如 “/user”、“/goods”
# Blueprint可以单独具有自己的模板、静态文件或者其它的通用操作方法，它并不是必须要实现应用的视图和函数的
# 在一个应用初始化时，就应该要注册需要使用的Blueprint
# 但是一个Blueprint并不是一个完整的应用，它不能独立于应用运行，而必须要注册到某一个应用(指Flask app)中



# 创建蓝图对象
user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
def get_profile():
    return 'user profile'

@user_bp.route('/login', methods=['POST'])
def login():
    return 'user login'



