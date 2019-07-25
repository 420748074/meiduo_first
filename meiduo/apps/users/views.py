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
            response.set_cookie('username', user.username, max_age=0)
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

        return render(request, 'user_center_info.html')


    # def get(self,request):
    #     next = request.GET.get('next')
    #     if next:
    #         response = redirect(next)
    #     else:
    #         response = redirect(reverse('users:info'))
    #
    #     return response

    # def get_redirect_field_name(self,request):
    #
    #     next = request.GET.get('next')
    #     if next:
    #         response = redirect(next)
    #     else:
    #         response = redirect(reverse('users:info'))
    #
    #     return response
