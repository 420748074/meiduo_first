from django.core.files.storage import Storage

from django.utils.deconstruct import deconstructible

from meiduo import settings


# @deconstructible
# class MyStorage(Storage):
#
#     def _open(self,name,mode='rb'):
#         pass
#     def _save(self,name,content,max_lenth=None):
#         pass
#     def url(self, name):
#         #这个ｎａｍｅ就是ｆｉｌｅ－ｉｄ
#         # name = group1/m00/00/01/CtmebVirmc-AJdvSAAEI5Wm7zaw8639396
#
#         return settings.FDFS_URL + name

@deconstructible
class MyStorage(Storage):

    def __init__(self, fdfs_url=None):
        if not fdfs_url:
            fdfs_url = settings.FDFS_URL
        self.fdfs_url=fdfs_url

    def _open(self, name, mode='rb'):
        pass
    def _save(self, name, content, max_length=None):
        pass

    def url(self, name):
        # 这个name 其实就是 file_id
        # name = group1/M00/00/01/CtM3BVrLmc-AJdVSAAEI5Wm7zaw8639396

        # http://192.168.229.148:8888/ + name
        # return 'http://192.168.229.148:8888/' + name
        # return settings.FDFS_URL + name
        return self.fdfs_url + name