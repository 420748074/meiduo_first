import re
from django import http
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from QQLoginTool.QQtool import OAuthQQ
from django_redis import get_redis_connection
from apps.aouth.utils import generic_openid_token, check_openid_token
from apps.users.models import User
from meiduo import settings
from django.urls import reverse
from django.views import View

from apps.aouth.models import OAuthQQUser
from meiduo import settings
import logging
logger = logging.getLogger('django')
# 跳转到ＱＱ扫登陆界面
class OauthQQURLView(View):

    def get(self,request):
        next=request.GET.get('next')
        # login_url = 'https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&client_id=101518219&redirect_uri=http://www.meiduo.site:8000/oauth_callback&state=test'
        qq = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=next
        )
        login_url = qq.get_qq_url()


        return JsonResponse({'code':200,'errmsg':'ok','login_url':login_url})


"""
对于应用而言，需要进行两部：
１．获取ｃｏｄｅ
２．通过ｃｏｄｅ　获取Ｔｏｋｅｎ
"""

class OauthQQUserViw(View):

    def get(self,request):
        code = request.GET.get('code')
        if code is None:
            return http.HttpResponseBadRequest('你缺啊')

        qq = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state='text'
        )
        token = qq.get_access_token(code)

        openid = qq.get_open_id(token)

        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            openid_tocken = generic_openid_token(openid)

            return render(request,'oauth_callback.html',{'openid':openid_tocken})
          #无异常走ｅｌｓｅ
        else:
            # 若存在进行登陆跳转
            user = qquser.user
            # 保持登陆状态
            login(request,user)
            # 设置ｃｏｏｋｉｅ
            response = redirect(reverse("contents:index"))
            response.set_cookie('username',user,max_age=3600*24*14)
            # 跳转
            return response

        # return render(request,'oauth_callback.html')

    def post(self,request):
        #  1.接收数据
        data = request.POST
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code_client = data.get('sms_code')
        access_token = data.get('access_token')
        #  2.验证数据
        if not all([mobile, password, sms_code_client]):
            # from django import http
            return http.HttpResponseBadRequest('参数不全')
        # ④验证用户名
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('手机号不满足条件')
        # ⑤验证密码
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('密码格式不正确')
        # 短信验证码
        #  连接reids
        redis_conn = get_redis_connection('code')
        # 获取redis中的短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        #  判断redis中的短信验证码是否过期
        if not sms_code_server:
            return http.HttpResponseBadRequest('短信验证码已过期')
        # 比对
        if sms_code_server.decode() != sms_code_client:
            return http.HttpResponseBadRequest('短信验证码不一致')
        # openid_token
        openid = check_openid_token(access_token)
        if openid is None:
            # return http.HttpResponseBadRequest('openid错误')
            return render(request,'oauth_callback.html',{'openid_errmsg':'openidguoqi '})
        # 3.绑定信息
        #     openid      是通过对oepnid_token的解密来获取
        #     user        需要根据 手机号进行判断
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            #                     如果没有注册,我们就创建一个user用户
            user = User.objects.create_user(
                username=mobile,
                password=password,
                mobile=mobile
            )
        else:
            #如果手机号注册,已经有user信息
            # 我们需要再次验证密码是否正确
            if not user.check_password(password):
                return http.HttpResponseBadRequest('密码错误')
        try:
            OAuthQQUser.objects.create(
                openid=openid,
                user=user
            )
        except Exception as e:
            logger.error(e)
            return http.HttpResponseBadRequest('数据库错误')

        # 4.登陆状态保持
        login(request, user)
        # 5.cookie
        response = redirect(reverse('contents:index'))

        response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        # 6.返回相应
        return response


#########################itsdangerous加密#####################################
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from meiduo import settings

#1创建实例对象
# secret_key, expires_in
# secrey_key, 密钥      习惯上用settings中的SECRET_KEY
# expires_in  过期时间（单位：秒）
s = Serializer(settings.SECRET_KEY,300)

#2组织数据

data = {'openid':'abcd'}

#3.加密处理

token = s.dumps(data)

token.decode()

#########################itsdangerous解密#####################################
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meiduo import settings

#1创建实例对象
# secret_key, expires_in
# secrey_key, 密钥      习惯上用settings中的SECRET_KEY
# expires_in  过期时间（单位：秒）
s = Serializer(settings.SECRET_KEY,300)

#2.解密处理
try:
    s.loads(token)
except Exception as e:
    pass

#########################itsdangerous解密失败#####################################
"""
过期

Traceback (most recent call last):
  File "<console>", line 1, in <module>
  File "/home/python/.virtualenvs/py3_meiduo_mall_40/lib/python3.5/site-packages/itsdangerous/jws.py", line 205, in loads
    date_signed=self.get_issue_date(header),
itsdangerous.exc.SignatureExpired: Signature expired
"""

"""
加密数据被篡改，解密失败
s.loads('eyJhbGciOiJIUzUxMiIsImV4cCI6MTU1NzgwNzExNCwiaWF0IjoxNTU3ODA2ODE0fQ.eyJvcGVuaWQiOiJhYNkZSJ9.GRigrxTwflc74khO4LP0-VtxUeqxU0lXCdOLOv5jj3kZowTBW_SKWGUe0OzVTQPVQFDTGdxEtXyvRmJZA-ANQ')
Traceback (most recent call last):
  File "<console>", line 1, in <module>
  File "/home/python/.virtualenvs/py3_meiduo_mall_40/lib/python3.5/site-packages/itsdangerous/jws.py", line 187, in loads
    self, s, salt, return_header=True
  File "/home/python/.virtualenvs/py3_meiduo_mall_40/lib/python3.5/site-packages/itsdangerous/jws.py", line 143, in loads
    self.make_signer(salt, self.algorithm).unsign(want_bytes(s)),
  File "/home/python/.virtualenvs/py3_meiduo_mall_40/lib/python3.5/site-packages/itsdangerous/signer.py", line 169, in unsign
    raise BadSignature("Signature %r does not match" % sig, payload=value)
itsdangerous.exc.BadSignature: Signature b'GRigrxTwflc74khO4LP0-VtxUeqxU0lXCdOLOv5jj3kZowTBW_SKWGUe0OzVTQPVQFDTGdxEtXyvRmJZA-ANQ' does not match

"""