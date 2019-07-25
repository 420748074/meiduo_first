from random import randint

from django import http
from django.shortcuts import render
from django_redis import get_redis_connection
from django.views import View
from libs.captcha.captcha import captcha
import logging

from libs.yuntongxun.sms import CCP

logger = logging.getLogger('django')

# 图片验证码／
class ImageCodeView(View):

    def get(self,request,uuid):
        # generate_captcha()返回值有两个
        text,image=captcha.generate_captcha()
        # 储存到ｒｅｄｉｓ
        redis_conn = get_redis_connection('code')
        # 设置过期
        redis_conn.setex('img_%s' % uuid,60*5,text)
        return http.HttpResponse(image,content_type='image/jpeg')


class SMSCodeView(View):

    def get(self,request,mobile):
        image_client = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')



        if not all([image_client,uuid]):
            return http.HttpResponseBadRequest('缺少参数')

        try:
            redis_conn = get_redis_connection('code')
            image_server = redis_conn.get('img_{}'.format(uuid))
            if image_server is None:
                return http.HttpResponseBadRequest('验证码过期')

            redis_conn.delete('img_{}'.format(uuid))

            if image_client.lower() != image_server.decode().lower():
                return http.HttpResponseBadRequest('验证码错误')
        except Exception as e:
            logger.error(e)
            return http.HttpResponseBadRequest('找不到我的数据库了')
        send_flag=redis_conn.get('send_flag{}'.format(mobile))
        if send_flag:
            return http.JsonResponse({'code': 'ok', 'errmsg': '发送短信过于频繁'})

        sms_code = '%06d' % randint(0, 999999)
        # 打印验证码可以不写
        logger.info(sms_code)
        try:
            # redis_conn.setex('sms_{}'.format(mobile),60,sms_code)
            # send_flag=redis_conn.setex('send_flag{}'.format(mobile),60,1)

            pl = redis_conn.pipeline()
            pl.setex('sms_{}'.format(mobile), 60, sms_code)
            pl.setex('send_flag{}'.format(mobile), 60, 1)
            pl.execute()

        except Exception as e:
            logger.error(e)
            return http.HttpResponseBadRequest('找不到我的数据库了')


        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        from celery_tasks.sms.tasks import send_sms_code

        # delay()里面的参数就是ｔａｓｋｓ任务需要传的参数
        send_sms_code.delay(mobile,sms_code)

        return http.JsonResponse({'code':'ok','errmg':'发送成功'})
