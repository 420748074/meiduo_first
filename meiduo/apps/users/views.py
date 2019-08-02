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

from apps.goods.models import SKU
from apps.users.utils import generic_verify_email_url, check_verfy_email_token
from meiduo import settings
from utils.response_code import RETCODE
from utils.views import LoginRequiredJSONMixin

logger = logging.getLogger('django')

# 用户注册视图
from apps.users.models import User, Address

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
class AdressView(LoginRequiredJSONMixin,View):

    def get(self,request):
        """
        1.必须是登陆用户
        ２．查询登陆用户端　地址信息
        ３．丢列表数据记性转换为字典列表
        ４．传递给模板
        :param request:
        :return:
        """
        addresses = Address.objects.filter(user=request.user,is_deleted=False)
        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id": address.province_id,
                "city": address.city.name,
                "city_id": address.city_id,
                "district": address.district.name,
                "district_id": address.district_id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)
        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id": address.province_id,
                "city": address.city.name,
                "city_id": address.city_id,
                "district": address.district.name,
                "district_id": address.district_id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)
        context = {
            'default_address_id': request.user.default_address_id,
            'addresses': address_dict_list,
        }


        return render(request,'user_center_site.html',context)

# 新增收货地址
class CreateAddressView(LoginRequiredJSONMixin,View):
    """
    需求，
        当用户填写玩新增数据之后，点击新增按钮，需要让前段将收货人等信息交给后端
    后端
        大体步骤
        判断当期那用户是否登陆
        接受参数
        验证参数
        数据入库
        返回响应
        请求方式和路由：
            ＰＯＳＴ　／ａｄｒｅｓｓｅｓ／ｃｒｅａｔｅ

    """
    def post(self,request):
        #默认地址上限为２０
        count = Address.objects.filter(user=request.user,is_deleted=False).count()
        if count >20:
            return http.JsonResponse({'code':RETCODE.THROTTLINGERR,'errmsg':'个数超过上限'})

        # 接受数据
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            # 如果没有默认　地址，将新增地址设置位默认地址
            if not request.user.default_address:
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':'数据库操作失败'})
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'新增地址成功','address':address_dict})

# 修改地址
class UpdateAddressView(LoginRequiredJSONMixin,View):
    """
    需求：当用户修改了地址信息之后，需要然前段编辑，这个信息全部手机过去
    后端：
        １．判断用户是否登陆
        ２．根据传递过来的更新指定的地址信息
        ３．更新
        ４．返回响应
        请求方式和路由
        PUT/addresses/id/
    """
    def put(self,request,address_id):
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')
        data=json.loads(request.body.decode())
        # 根据传递过来的更新指定的地址信息
        # address=Address.objects.get(pk=address_id)
        # address.receiver=data.get('recever')
        try:
            Address.objects.filter(pk=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            address = Address.objects.get(pk=address_id)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})
        # ３．更新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    #删除收货地址
    def delete(self,request,address_id):
        try:
            address = Address.objects.get(pk=address_id)
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':"删除地址失败"})

        return http.JsonResponse({'code':RETCODE.OK,'errmsg':"删除地址成功"})



class DefaultAddress(LoginRequiredJSONMixin,View):

    def put(self,request,address_id):
        try:
            address = Address.objects.get(pk=address_id)
            request.user.default_address = address
            request.user.default_address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':"修改默认地址失败"})
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':"修改默认地址成功"})


"""修改地址标头"""
class TitleAddress(LoginRequiredJSONMixin,View):
    def put(self,request,address_id):
        json_dict = json.loads(request.body.decode())
        new_title = json_dict.get('title')
        try:
            address = Address.objects.get(pk=address_id)
            address.title=new_title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':'标头更新失败'})
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'标头更新成功'})


class ChangePasswordView(View):

    def get(self,request):

        return render(request,'user_center_pass.html')

    def post(self,request):
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')

        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseBadRequest('密码最少8位，最长20位')
        if new_password != new_password2:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        if not request.user.check_password(old_password):
            return render(request,'user_center_pass.html',{'origin_password_errmsg':'原始密码错误'})
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_password_errmsg': '修改密码失败'})
        logout(request)
        response = redirect(reverse('users:login'))

        response.delete_cookie('username')

        return response


"""
添加用户浏览记录
需求
    当用ｕｆａｎｇｗｅｎ某个商品详情页面的时候，需要让前段发送一个ａｊａｘ请求
    将用户信息和ｓｓｋｕｉｄ发送给后端
后端
    １．接受数据
    ２．判断验证数据
    ３．数据入库
    ４．返回响应
    请求方式
    ＰＯＳＴ　browse_histories/

"""


class HistoryView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        try:
            sku =SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.NODATAERR,'errmsg':'暂无数据'})

        redis_conn =get_redis_connection('history')
        pl=redis_conn.pipelne()
        #先去重，好到和当前ｖｌｕｅ一样的
        pl.lrem('history_{}'.format(user.id),0,sku_id)
        redis_conn.lpush('history_{}'.format(user.id),sku_id)
        # 只保留五个数据
        pl.ltrim('history_{}'.format(user.id),0,4)
        pl.execute()
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok'})
