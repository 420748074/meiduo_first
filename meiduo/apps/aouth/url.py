from django.conf.urls import url
from . import views

urlpatterns = [
    # 注册
    url(r'^qq/login/$', views.OauthQQURLView.as_view(), name='qqurl'),
    url(r'^oauth_callback/$', views.OauthQQUserViw.as_view(),name='qquser'),
]