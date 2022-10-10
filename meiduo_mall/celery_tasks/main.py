# celery -A celery_tasks.main worker -l info -P eventlet 启用任务(虚拟环境下输入)

import os

from celery import Celery

# 指定django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

# 实例化celery, 参数设置脚本路径
app = Celery('celery_tasks')

# 加载配置文件以设置broker队列
app.config_from_object('celery_tasks.config')

# celery自动检测包内的任务
app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
