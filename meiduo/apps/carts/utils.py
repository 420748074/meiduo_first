import base64
import pickle

from django_redis import get_redis_connection
#合并购物车

def merge_cookie_to_redis(request,user,response):
    # 1.获取到cookie数据
    carts=request.COOKIES.get('carts')
    if carts is not None:
        cookie_cart=pickle.loads(base64.b64decode(carts))
        # {
        #  1:{count:15,selected:True},
        #         2:{count:200,selected:False}
        # }

        # {sku_id:count}
        cookie_hash={}
        #选中的id
        cookie_selected_ids=[]
        #未选中的id
        cookie_unselected_ids=[]
        # 2.遍历cookie数据
        for sku_id,count_selected_dict in cookie_cart.items():

            # 3.当前是以cookie为主,所以我们直接将cookie数据转换为hash, set(记录选中的和未选中的)
            cookie_hash[sku_id]=count_selected_dict['count']

            if count_selected_dict['selected']:
                cookie_selected_ids.append(sku_id)
            else:
                cookie_unselected_ids.append(sku_id)



        # 4.连接redis 更新redis数据
        redis_conn = get_redis_connection('carts')
        #hash {sku_id:count}
        # user=request.user
        redis_conn.hmset('carts_%s'%user.id,cookie_hash)
        # set
        # 选中的ids
        # [1,2]
        if cookie_selected_ids:
            redis_conn.sadd('selected_%s'%user.id,*cookie_selected_ids)

        # 未选中的 ids 从选中的集合中移除
        if cookie_unselected_ids:
            redis_conn.srem('selected_%s'%user.id,*cookie_unselected_ids)
        # 5.将cookie数据删除
        response.delete_cookie('carts')


        return response


    return response
