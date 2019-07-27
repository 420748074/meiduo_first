from itsdangerous import TimedJSONWebSignatureSerializer as Ser
from meiduo import settings
import logging
logger = logging.getLogger('django')

# 对ｏｐｅｎｉｄ　加密
def generic_openid_token(openid):

    #创建实例对象
    s = Ser(secret_key=settings.SECRET_KEY,expires_in=300)
    # 组织数据
    data = {
        'openid':openid
    }

    # 加密处理
    token = s.dumps(data)

    return token.decode()


# 解密
from itsdangerous import SignatureExpired,BadData
def check_openid_token(token):
    s = Ser(secret_key=settings.SECRET_KEY,expires_in=300)

    try:
        result = s.loads(token)
        print(result)
        print(type(result))
    except BadData:
        logger.error(BadData)
        return None
    return result.get('openid')
