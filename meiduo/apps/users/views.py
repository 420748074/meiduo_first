import json
import re
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import http
from django.db import DatabaseError
import logging
from django_redis import get_redis_connection

from apps.users.utils import generic_verify_email_url, check_verfy_email_token
from meiduo import settings
from utils.views import LoginRequiredJSONMixin

logger = logging.getLogger('django')

# 用户注册视图
from apps.users.models import User

log = logging.getLogger('django')

"""注册"""
class RegisterView(View):
    def get(self, request):

        return render(request, 'register.html')

    def post(self, request):

        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        sms_client = request.POST.get('sms_code')

        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseBadRequest('参数不全')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseBadRequest('请勾选用户协议')
        try:
            redis_conn = get_redis_connection('code')
            sms_server = redis_conn.get('sms_{}'.format(mobile))

            if sms_server is None:
                return render(request, 'register.html', {'sms_code_errmsg': 'guoqi'})

            if sms_server.decode() != sms_client:
                return render(request, 'register.html', {'sms_code_errmsg': '验证码错误'})
        except Exception as e:
            logger.error(e)
            return http.HttpResponseBadRequest('数据库连接失败')


        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            log.error(DatabaseError)
            return render(request, 'register.html', {'register_errmsg': '注册失败'})
        # return http.HttpResponse('注册成功，重定向到首页')
        login(request, user)
        response = redirect(reverse('contents:index'))

        response.set_cookie('username',user.username,max_age=3600*24*15)

        return response


# 验证用户名重复
class RegisterCountView(View):
    def get(self,request,username):

        count = User.objects.filter(username=username).count()

        return JsonResponse({'code':'ok','errmsg':'ok','count':count})

#验证手机号重复
class MobileCountView(View):

    def get(self,request,mobile):

        count = User.objects.filter(mobile=mobile).count()

        return JsonResponse({'code':'ok','msg':'ok','count':count})


#登陆
class LoginView(View):
    def get(self,request):

        return render(request,'login.html')

    def post(self,request):

        data = request.POST
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        if not all([username,password]):
            return http.HttpResponseBadRequest('缺少参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')

        from django.contrib.auth import authenticate

        # user = authenticate(username=username,password=password)
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request,'login.html',{'account_errmsg':'账户名或密码错误'})
        login(request,user)

        if remembered !='on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        # return redirect(reverse('contents:index'))

        response = redirect(reverse('contents:index'))
        if remembered != 'on':
            response.set_cookie('username', user.username, max_age=None)
        else:
            response.set_cookie('username', user.username, max_age=3600 * 24 * 14)

        return response


# 退出登陆
from django.contrib.auth import logout

class LogoutView(View):
    def get(self,request):

        logout(request)
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')

        return response


# 用户中心
from django.contrib.auth.mixins import LoginRequiredMixin
class UserInfoView(LoginRequiredMixin,View):

    def get(self,request):
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }

        return render(request, 'user_center_info.html',context=context)

# email发送邮件
class EmailView(LoginRequiredJSONMixin,View):

    def put(self,request):
        # １．用户必须登陆
        # ２．接受用户提交的信息
        # data = request.POST
        # (1)获取ｂｏｄｙ数据
        body = request.body
        # （２）ｂｏｄｙ数据是ｂｙｔｅｓ类型，进行转换
        body_str=body.decode()
        # （３）对字符串ｊｓｏｎ进行转换
        data = json.loads(body_str)
        email = data.get('email')
        # ３．验证邮箱是否符合规则
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return http.JsonResponse({'code':'nono','errmsg':'参数错误'})
        try:
            # ４．更新数据
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':'nono','errmsg':'更新错误'})
        # ５．发送邮件
        from django.core.mail import send_mail
        # subject, 主题
        # message, 消息
        # from_email, 谁发的
        # recipient_list　　收件人列表
        subject = '激活邮件'
        message = ''
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        #激活　ｕｒｌ中包含　用户的信息就可以
        verify_url=generic_verify_email_url(request.user.id)
        html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

        # send_mail(
        #     subject=subject,
        #     message=message,
        #     from_email=from_email,
        #     recipient_list=recipient_list
        # )
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message
        )

        # ６．返回响应
        return http.JsonResponse({'code':'ok','errmsg':'ok'})

# email验证
class EmailVerifyView(View):

    def get(self,request):
        token = request.GET.get('token')
        if token is None:
            return http.HttpResponseBadRequest('缺少参数')
        user_id=check_verfy_email_token(token)
        if user_id is None:
            return http.HttpResponseBadRequest('参数错误')
        try:
            user = User.objects.get(pk = user_id)
            if user is not None:
                user.email_active = True
                user.save()
        except User.DoesNotExist:
            return http.HttpResponseBadRequest('参数错误')

        return redirect(reverse('users:info'))

# 收货地址

class AdressView(View):

    def get(self,request):

        return render(request,'user_center_site.html')