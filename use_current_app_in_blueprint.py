from flask import Blueprint, current_app


bp = Blueprint('bp', __name__)


@bp.route('/use_current_app')
def use_current_app():
    redis_conn = current_app.redis_conn       # 不方便直接调用flask app，采用调用current_app(flask app的代理)
    print(redis_conn)
    return 'show the property in current_app ------------%s' % redis_conn









