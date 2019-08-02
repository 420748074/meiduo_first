from haystack import indexes
from apps.goods import models
from apps.goods.models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
                            # 索引文档        　　可以在templates里面创建文件夹
    text = indexes.CharField(document=True, use_template=True)
    # author = indexes.CharField(model_attr='user')
    # pub_date = indexes.DateTimeField(model_attr='pub_date')

    #对哪个模型进行检索
    def get_model(self):
        return SKU

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
                                                # 默认为上线，
        return self.get_model().objects.filter(is_launched=True)