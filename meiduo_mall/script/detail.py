#!/usr/bin/env python

import sys
sys.path.insert(0, '../')

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")


import django
django.setup()

import os

from django.template import loader

from apps.goods.models import SKU
from meiduo_mall.settings import BASE_DIR
from utils.goods import get_categories, get_goods_specs, get_breadcrumb


def generic_detail_html(sku):
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
    detail_template = loader.get_template('detail.html')
    detail_html_data = detail_template.render(context)
    file_path = os.path.join(os.path.dirname(BASE_DIR), 'front_end_pc/goods/%s.html' % sku.id)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(detail_html_data)
    print(sku.id)


skus = SKU.objects.all()
for sku in skus:
    generic_detail_html(sku)
