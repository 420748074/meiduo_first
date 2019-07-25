# １．需要单独常见一个任务包，任务包中的py文件必须以tasks.py明明
# 2.生产者／任务　　其本质就是一个函数
# ３．这个函数必须要经过celery的实例对象的task装饰其装饰
# ４．这个任务需要让celery自动检测
from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

@app.task
# 需要的参数直接传入函数中
def send_sms_code(mobile,sms_code):
    CCP().send_template_sms(mobile, [sms_code, 5], 1)