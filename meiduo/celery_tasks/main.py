
"""
生产者　
    # １．需要单独常见一个任务包，任务包中的ｐｙ文件必须以ｔｅｓｋｓ.py明明
    # 2.生产者／任务　　其本质就是一个函数
    # ３．这个函数必须要经过ｃｅｌｅｒｙ的实例对象的ｔａｓｋ装饰其装饰
    # ４．这个任务需要让ｃｅｌｅｒｙ自动检测
    # 5.让ｃｅｌｅｒｙ自动检测任务

    消费者
    语法：　celery -A celery_tasks.main worker -l info
    语法：　celery -A celery实例对象的文件 worker -l info
"""

# 1.导入ｃｅｌｅｒｙ
from celery import Celery
# 加载有可能用到的ｓｅｔｔｉｎｇｓ的文件
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo.settings')

#创建ｃｅｌｃｅｒｙ实例
#一般情况下将工程名字定为他的名字，只要确保名字唯一就好
app = Celery('celery_tasks')

app.config_from_object('celery_tasks.config')

# 5.让ｃｅｌｅｒｙ自动检测任务
# app.autodiscover_tasks(['任务包的路径'])
app.autodiscover_tasks(['celery_tasks.sms'])