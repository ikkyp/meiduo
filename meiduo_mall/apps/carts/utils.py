"""
    合并购物车 (将登陆前的cookie中的购物车数据与redis数据库中的数据进行合并)
    分为三种：
            1 以cookie数据为主
            2 以redis数据为主
            3 将cookie和redis中的数据进行累加
    这里我们进行第一种方式，以cookie数据为主，将cookie数据存入redis中，如果存在相同的商品id，则以cookie为主
    1 读取cookie数据
    2 初始化一个字典存放商品id及数量
    3 初始化一个列表存放选中的商品id，初始化一个列表存放未选中的商品id
      后来通过selected的值来确定redis中的数据的增删改查
    4 遍历cookie数据， 将数据添加到redis中
    5 删除cookie数据
    6 返回响应
"""
import base64, pickle
from django_redis import get_redis_connection


def merge_cookie_to_redis(request, response):
    data = request.COOKIE.get('carts')
    if data:
        carts = pickle.loads(base64.b64decode(data))
        skus = {}
        selected = []
        unselected = []

        # carts数据格式为:{1: {'count':xxx, 'selected':xxx}}
        for sku_id, count_selected in carts.items():
            skus[sku_id] = count_selected['count']
            if count_selected['selected']:
                selected.append(sku_id)
            else:
                unselected.append(sku_id)
        user = request.user
        redis_conn = get_redis_connection('carts')
        pl = redis_conn.pipeline()
        pl.hmset('carts_%s' % user.id, skus)
        if len(selected):
            pl.sadd('selected_%s' % user.id, *selected)
        if len(unselected):
            pl.srem('selected_%s' % user.id, *unselected)

        pl.execute()

        response.delete_cookie('carts')
        return response


