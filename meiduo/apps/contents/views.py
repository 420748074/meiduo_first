from django.shortcuts import render
from django.views import View

from apps.contents.utils import get_categories
from apps.contents.models import ContentCategory
class IndexView(View):

    def get(self,request):
        #1.插叙商品频道和分类
        categories = get_categories()
        # ２．广告楼层数据
        contents ={}
        contents_categories= ContentCategory.objects.all()

        for cat in contents_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request, 'index.html', context)
