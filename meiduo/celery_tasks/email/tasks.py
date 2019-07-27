from django.core.mail import send_mail

from celery_tasks.main import app
import logging
logger = logging.getLogger('django')


# bind=True表示吧任务自己传递过去，这样我们就可以在任务的第一个参数传递ｓｅｌｆ
# 函数中的ｓｅｌｆ就是代表ｔａｓｋ任务本身
# default_retry_delay重试任务间隔时间
@app.task(bind=True,default_retry_delay=5,name= 'send_email')
def send_verify_email(self,subject,message,from_email,recipient_list,html_message):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message
        )
    except Exception as e:
        logger.error(e)
        raise self.retry(exc=e,max_retries=3,)
        # max_retries最大的重试次数


