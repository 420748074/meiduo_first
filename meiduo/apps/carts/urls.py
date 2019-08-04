from django.conf.urls import url
from . import views

urlpatterns = [
    # 注册
    url(r'^carts/$', views.CartsView.as_view(), name='info'),
    url(r'^carts/selection/$', views.CartsSelectAllView.as_view(), name='cartsselectall'),
    url(r'^carts/simple/$', views.CartsSimpleView.as_view(), name='cartssimple'),
]