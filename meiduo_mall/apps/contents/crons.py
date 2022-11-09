import os
import time

from django.template import loader

from apps.contents.models import ContentCategory
from meiduo_mall import settings
from utils.goods import get_categories


def generate_static_index_html():
    print('%s: generate_static_index_html' % time.ctime())
    # 1.商品分类数据
    categories = get_categories()
    # 2.广告数据
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
    # 需要改变并且传输的数据
    context = {
        'categories': categories,
        'contents': contents,
    }
    index_template = loader.get_template('index.html')
    index_html_data = index_template.render(context)
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc/index.html')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(index_html_data)
