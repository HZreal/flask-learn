from flask import Blueprint, current_app


bp = Blueprint('bp', __name__)



@bp.route('/use_current_app')
def use_current_app():
    redis_conn = current_app.redis_conn
    print(redis_conn)
    return 'show the property in current_app ------------%s' % redis_conn









