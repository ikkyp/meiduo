import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from haystack.views import SearchView

from apps.contents.models import ContentCategory
from apps.goods.models import GoodsCategory
from apps.goods.models import SKU
from utils.goods import get_breadcrumb, get_goods_specs
from utils.goods import get_categories


class IndexView(View):

    def get(self, request):
        """
        首页的数据分为2部分
        1部分是 商品分类数据
        2部分是 广告数据

        """
        # 1.商品分类数据
        categories = get_categories()
        # 2.广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 我们的首页 后边会讲解页面静态化
        # 我们把数据 传递 给 模板
        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request, 'index.html', context)


class ListView(View):

    def get(self, request, category_id):
        # 1.接收参数
        # 排序字段
        ordering = request.GET.get('ordering')
        # 每页多少条数据
        page_size = request.GET.get('page_size')
        # 要第几页数据
        page = request.GET.get('page')

        # 2.获取分类id
        # 3.根据分类id进行分类数据的查询验证
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})
        # 4.获取面包屑数据
        breadcrumb = get_breadcrumb(category)

        # 5.查询分类对应的sku数据，然后排序，然后分页
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(ordering)
        # 分页

        # object_list, per_page
        # object_list   列表数据
        # per_page      每页多少条数据
        paginator = Paginator(skus, per_page=page_size)

        # 获取指定页码的数据
        page_skus = paginator.page(page)

        sku_list = []
        # 将对象转换为字典数据
        for sku in page_skus.object_list:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })

        # 获取总页码
        total_num = paginator.num_pages

        # 6.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'list': sku_list, 'count': total_num, 'breadcrumb': breadcrumb})


class SKUIndex(SearchView):
    # 重写 create_response方法
    def create_response(self):
        context = self.get_context()
        data_list = []
        for sku in context['page'].object_list:
            data_list.append({
                'id': sku.object.id,
                'name': sku.object.name,
                'price': sku.object.price,
                'default_image_url': sku.object.default_image.url,
                'searchkey': context.get('query'),
                'page_size': context['page'].paginator.num_pages,
                'count': context['page'].paginator.count
            })
        return JsonResponse(data_list, safe=False)


class DetailView(View):
    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            pass
        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)
        # 规格信息
        goods_specs = get_goods_specs(sku)
        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }

        return render(request, 'detail.html', context)


# 用户的历史记录的记录及查询
class UserBrowseHistory(View):
    def post(self, request):
        # 获取json数据并得到sku_id的值
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 验证该产品是否存在在数据库中
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '数据不存在'})

        # 保存用户的浏览数据
        redis_conn = get_redis_connection('history')
        p1 = redis_conn.pipeline()
        user_id = request.user.id

        # 去除redis中存在的历史记录
        p1.lrem('history_%s' % user_id, 0, sku_id)
        # 将新浏览的记录导入redis中
        p1.lpush('history_%s' % user_id, sku_id)
        # 截取前五个数据
        p1.ltrim('history_%s' % user_id, 0, 4)
        # 执行管道数据
        p1.execute()

        return JsonResponse({'code': 0, 'errmsg': 'OK'})

    def get(self, reqeust):
        # 获取该用户id保存在redis中的数据并将产品信息传输到前端
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange('history%s' % reqeust.user.id, 0, -1)
        skus = []

        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
            })
            return JsonResponse({'code': 0, 'errmsg': 'OK', 'skus': skus})
