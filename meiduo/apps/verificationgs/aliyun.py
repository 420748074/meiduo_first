#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from meiduo.settings import ALIKEY_SECRET

client = AcsClient('ALIKEY_ID', ALIKEY_SECRET, 'cn-hangzhou')

request = CommonRequest()
request.set_accept_format('json')
request.set_domain('dysmsapi.aliyuncs.com')
request.set_method('POST')
request.set_protocol_type('https') # https | http
request.set_version('2017-05-25')
request.set_action_name('SendSms')

request.add_query_param('RegionId', "cn-hangzhou")
request.add_query_param('PhoneNumbers', "123123123123")
request.add_query_param('SignName', "美多商城")
request.add_query_param('TemplateCode', "SMS_171117738")

response = client.do_action(request)
# python2:  print(response)
print(str(response, encoding = 'utf-8'))
