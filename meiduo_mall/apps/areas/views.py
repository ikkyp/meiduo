from django.http import JsonResponse
from django.views import View

from apps.areas.models import Area


# Create your views here.
class AreasView(View):
    def get(self, request):
        provinces = Area.objects.filter(parent=None)
        # provinces获取的是对象数据，不能转化为json数据，需要转化为字典数据才行
        province_list = []
        for province in provinces:
            province_list.append({
                'id': province.id,
                'name': province.name
            })
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'province_list': province_list})


class SubAreasView(View):
    def get(self, request, id):
        # 包揽省市区
        up_level = Area.objects.get(id=id)
        down_level = up_level.subs.all()
        data_list = []
        for item in down_level:
            data_list.append({
                'id': item.id,
                'name': item.name,
            })
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'sub_data': {'subs': data_list}})
