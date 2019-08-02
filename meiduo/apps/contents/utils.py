from collections import OrderedDict

from apps.goods.models import GoodsChannel


def get_categories():
    """提供首页广告界面"""
    # 查询商品频道和分类
    categories = OrderedDict()
    # 查询所有的频道信息
    channels1 = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 对所有频道进行遍历
    for channel in channels1:
        # 获取当前频道的ｇｒｏｕｐ【ｉｄ】（获取当前频道）
        group_id = channel.group_id  # 当前组
        # 判断当前频道是否在有序字典中
        if group_id not in categories:
            categories[group_id] = {'channels': [],
                                    'sub_cats': []
                                    }

        cat1 = channel.category  # 当前频道的类别

        # 追加当前频道
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })
        # 构建当前类别的子类别
        for cat2 in cat1.subs.all():
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)


    return categories