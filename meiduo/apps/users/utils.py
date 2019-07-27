import re
from django.contrib.auth.backends import ModelBackend

from apps.users.models import User
from meiduo import settings


def get_user_by_username(username):
    try:
        if re.match(r'^1[3-9]\d{9}', username):
            user = User.objects.get(mobile=username)
        else:
            user = User.objects.get(username=username)
    except User.DoesNotExsit:
        return None

    return user



class UsernameModelBackendBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):

        # try:
        #     if re.match(r'^1[3-9]\d{9}',username):
        #         user =User.objects.get(mobile=username)
        #     else:
        #         user = User.objects.get(username=username)
        # except User.DoesNotExsit:
        #     return None
        user = get_user_by_username()
        if user is not None and user.check_password(password):
            return user

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

# 邮箱验证加密
def generic_verify_email_url(user_id):
    # 创建实例对象
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    # 组织数据
    data = {
        'user_id':user_id
    }
    # 加密数据
    token = s.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    # 返回数据
    return verify_url
