from django.conf.urls import url
from . import views

urlpatterns = [
    # 注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),
    url(r'^emails/$', views.EmailView.as_view(), name='email'),
    url(r'^emails/verification/$', views.EmailVerifyView.as_view(), name='emailverifications'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/$', views.RegisterCountView.as_view(), name='registercount'),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view(), name='mobilecount'),
    url(r'^addresses/$', views.AdressView.as_view(), name='addresses'),
    url(r'^addresses/create/$', views.CreateAddressView.as_view(), name='addresses_create'),
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateAddressView.as_view(), name='addresses_update'),
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddress.as_view(), name='DefaultAddress'),
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.TitleAddress.as_view(), name='TitleAddress'),
    url(r'^changepassword/$', views.ChangePasswordView.as_view(), name='changepassword'),
    url(r'^browse_histories/$', views.HistoryView.as_view(), name='history'),

]