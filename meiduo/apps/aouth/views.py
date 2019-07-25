from django.http import JsonResponse
from django.shortcuts import render
from QQLoginTool.QQtool import OAuthQQ

# Create your views here.
from django.views import View

from meiduo import settings


class OauthQQURLView(View):

    def get(self,request):
        # login_url = 'https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&client_id=101518219&redirect_uri=http://www.meiduo.site:8000/oauth_callback&state=test'
        qq = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state='text'
        )
        login_url = qq.get_qq_url()


        return JsonResponse({'code':200,'errmsg':'ok','login_url':login_url})


"""
对于应用而言，需要进行两部：
１．获取ｃｏｄｅ
２．通过ｃｏｄｅ　获取Ｔｏｋｅｎ
"""

class OauthQQUserViw(View):


    pass