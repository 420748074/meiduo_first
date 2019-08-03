# l = [i for i in range(20)]
# #
# li = l[:]  # 将原始的座位号copy一份出来
# n = 8  # 报数的起始数
# # a = 1
# # while a == 1:
# #
# #     for i in li:
# #
# #         if n % 3 == 0:
# #             l.remove(i)
# #
# #         if len(l) == 2:
# #             a = 2
# #             break
# #
# #         n += 1
# #     li = l[:]
# #
# #
# # print(l)
# #
# def f(n, li):
#     '''
#     递归查找最后的两个人
#     :param n: 每轮的起始报数值
#     :param li: 每轮起始的剩余人的座位号列表
#     :return: 每轮剩余的人的座位号列表
#     '''
#     for i in li:
#
#         # 判断当前报数是否为3的倍数，是的话该人直接出局
#         if n % 3 == 0:
#             l.remove(i)
#
#         # 判断列表中还剩多少人，剩余2人终止递归
#         if len(l) == 2:
#             return l
#
#         n += 1  # 报数自增1
#
#     li = l[:]  # 一次递归调用后剩下的人，copy一份数据供下次递归使用
#
#     return f(n, li)
#
#
# print(f(n, li))

# a =range(10)[2:8]
# print(type(a))
# print(a)
# print(range(5))
# for i in range(5):
#     print(i)
# 0 1 2 3 4
# for i in a:
#     print(i)
#
#
# a = [1,3,3,4,2,2]
# b = []
#
# for i in a:
#     if i not in b:
#         b.append(i)
# print(b)
#
# c = list(set(a))
# print(c)
# a = 0
# if True:
#     print (bool(a))

# i = int(input('净利润:'))
# arr = [1000000,600000,400000,200000,100000,0]
# rat = [0.01,0.015,0.03,0.05,0.075,0.1]
# r = 0
# for idx in range(0,6):
#     if i>arr[idx]:
#         r+=(i-arr[idx])*rat[idx]
#         print ((i-arr[idx])*rat[idx])
#         i=arr[idx]
# print (r)
# num = 0
# for i in range(1,5):
#     for j in range(1,5):
#         for k in range(1,5):
#             if ( i != k ) and (i != j) and (j != k):
#                 num+=1
#                 print(i,j,k)
# print(num)

#
# for a in range(1,1000):
#     for c in range(1,1000):
#         for d in range(1,1000):
#             if a+100 ==c*c & a+268 == d*d:
#                 print(a)

# for i in range(1,85):
#     if 168 % i == 0:
#         j = 168 / i;
#         if  i > j and (i + j) % 2 == 0 and (i - j) % 2 == 0 :
#             m = (i + j) / 2
#             n = (i - j) / 2
#             x = n * n - 100
#             print(x)
