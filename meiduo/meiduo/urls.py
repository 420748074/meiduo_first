"""meiduo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^',include('apps.users.url',namespace='users')),
    url(r'^',include('apps.contents.url',namespace='contents')),
    url(r'^',include('apps.verificationgs.url',namespace='verificationgs')),
    url(r'^',include('apps.aouth.url',namespace='aouth')),
    url(r'^',include('apps.areas.urls',namespace='areas')),
    url(r'^',include('apps.goods.urls',namespace='goods')),
    url(r'^search/', include('haystack.urls')),
]
