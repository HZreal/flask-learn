from . import goods_bp


@goods_bp.route('/goods_list')
def get_goods_list():
    return 'goods list'

@goods_bp.route('/goods/<goods_id>', methods=['GET'])
def goods_info(goods_id):
    return 'goods detail info'
