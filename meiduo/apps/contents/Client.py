from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526 import StopInstanceRequest
# 创建AcsClient实例
client = AcsClient(
   "<your-access-key-id>LTAIoI2JQ2al8llP",
   "<your-access-key-secret>Hnz6Cl2rTqZmUAb0M0LxZnnWVadTMY",
   "<your-region-id>"
);
# 创建request，并设置参数
request = DescribeInstancesRequest.DescribeInstancesRequest()
request.set_PageSize(10)
# 发起API请求并显示返回值
response = client.do_action_with_exception(request)
print (response)