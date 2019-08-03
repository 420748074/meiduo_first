from django.conf.urls import url
from . import views

urlpatterns = [
    # 注册
    url(r'^carts/$', views.CartsView.as_view(), name='info'),
]