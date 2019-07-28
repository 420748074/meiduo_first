l = [i for i in range(20)]
#
li = l[:]  # 将原始的座位号copy一份出来
n = 8  # 报数的起始数
# a = 1
# while a == 1:
#
#     for i in li:
#
#         if n % 3 == 0:
#             l.remove(i)
#
#         if len(l) == 2:
#             a = 2
#             break
#
#         n += 1
#     li = l[:]
#
#
# print(l)
#
def f(n, li):
    '''
    递归查找最后的两个人
    :param n: 每轮的起始报数值
    :param li: 每轮起始的剩余人的座位号列表
    :return: 每轮剩余的人的座位号列表
    '''
    for i in li:

        # 判断当前报数是否为3的倍数，是的话该人直接出局
        if n % 3 == 0:
            l.remove(i)

        # 判断列表中还剩多少人，剩余2人终止递归
        if len(l) == 2:
            return l

        n += 1  # 报数自增1

    li = l[:]  # 一次递归调用后剩下的人，copy一份数据供下次递归使用

    return f(n, li)


print(f(n, li))
