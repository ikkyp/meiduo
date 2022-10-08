# Create your views here.
from random import randint

from django.http import HttpResponse, JsonResponse
from django.views import View
from django_redis import get_redis_connection

from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP


class ImageCodeView(View):
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis_cli = get_redis_connection('code')
        redis_cli.setex(uuid, 100, text)
        # 由于图片是二进制格式，所以用HttpResponse
        # content_type 是告诉响应数据，这是什么格式的图片
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):
    def get(self, request, mobile):
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        # 链接redis code库
        redis_cli = get_redis_connection('code')
        redis_imag_code = redis_cli.get(uuid)

        if redis_imag_code is None:
            return JsonResponse({'code': 400, 'errmsg': '图片验证码已过期'})

        if redis_imag_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': 400, 'errmsg': '图片验证码错误'})

        send_flag = redis_cli.get('send_flag_%s' % mobile)
        if send_flag is not None:
            return JsonResponse({'code': 400, 'errmsg': '不要频繁发送短信'})
        sms_code = "%06d" % randint(0, 99999)

        # 新建管道
        pipeline = redis_cli.pipeline()
        pipeline.setex(mobile, 300, sms_code)
        # 发送标记，避免多次重复发送验证码
        pipeline.setex('send_flag_%s' % mobile, 60, 1)
        # 执行管道内的指令，减少redis数据库的访问次数
        pipeline.execute()

        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
