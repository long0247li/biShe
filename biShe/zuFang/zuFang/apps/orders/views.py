import datetime
import json
import logging
from django.http import JsonResponse
from django.views import View

# Django中配置文件settings全局变量的导入
from django.conf import settings
from users.models import House, Order, User

# 登录访问控制，如果未登录则跳转到登录页面
from users.utils import LoginRequiredMixin
# 创建日志记录器：导入创建日志器才能使用
logger = logging.getLogger('django')


#添加订单
class AddOrderView(LoginRequiredMixin, View):
    def post(self, request):
        # 用来接收json数据，将json格式转换为字典，获取前台参数
        json_dict = json.loads(request.body)
        house_id = json_dict.get('house_id')  # 房屋id
        start_date = json_dict.get('start_date')  # 开始日期
        end_date = json_dict.get('end_date')  # 结束时间
        # 总体检验数据
        if not all([house_id, start_date, end_date]):
            return JsonResponse({
                'errno': 4103,
                'errmsg': '缺少必传参数'
            })

        # 检查日期格式
        try:
            # 字符串转换为datetime类型
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        except Exception as error:
            return JsonResponse({
                'errno': 4103,
                'errmsg': '日期参数错误'
            })
        try:
            # 从数据库中取得匹配结果，返回一个对象列表，订单状态为待评价
            orders = Order.objects.filter(house_id=house_id, status=3)
        except Exception as error:
            return JsonResponse({
                'errno': 4001,
                'errmsg': '获取数据错误'
            })

        # 判断是否存在多个订单
        for order in orders:
            st = order.begin_date  # 预定的起始时间
            et = order.end_date  # 结束时间
            # 前台接收参数与数据库内容比较，数据库结束<=前端入住 或 前端结束<=数据库入住
            if not (et <= start_date or end_date <= st):
                return JsonResponse({
                    'errno': 4004,
                    'errmsg': '该时间段已有订单存在'
                })

        # 检查房屋id是否存在于数据库中
        try:
            house = House.objects.get(id=house_id)
        except Exception as error:
            return JsonResponse({
                'errno': 4002,
                'errmsg': '无数据'
            })

        # 获取当前日期
        today = datetime.date.today()
        current_year = today.year
        current_month = today.month
        current_day = today.day

        # 开始日期检验
        start_year = start_date.year
        start_month = start_date.month
        start_day = start_date.day

        # 判断开始日期是否大于等于当前的日期
        if not start_year >= current_year and start_month >= current_month and start_day >= current_day:
            return JsonResponse({
                # 如果开始日期小于当前日期则日期非法
                'errno': 4103,
                'errmsg': '开始日期参数非法'
            })

        # 离店日期检验
        end_year = end_date.year
        end_month = end_date.month
        end_day = end_date.day
        # 判断结束日期是否大于等于开始日期
        if not end_year >= start_year and end_month >= start_month and end_day >= start_day:
            return JsonResponse({
                # 如果结束日期小于开始日期则日期非法
                'errno': 4103,
                'errmsg': '开始日期参数非法'
            })
        # 获取开始日期与结束日期差值
        left_days = (end_date - start_date).days
        # 保存到数据库
        try:
            order = Order.objects.create(
                user=request.user,  # 请求用户对象
                house=house,
                begin_date=start_date,  # 开始日期
                end_date=end_date,  # 结束时间
                days=left_days,  # 日期差值
                house_price=house.price,  # 房屋单价
                amount=house.price * left_days,
                status=0,
            )
        except Exception as error:
            return JsonResponse({
                'errno': 4001,
                'errmsg': '数据库保存错误'
            })

        data = {'order_id': order.id}  # 订单id
        return JsonResponse({
            'data': data,
            'errno': 0,
            'errmsg': 'ok'
        })

    # 获取订单列表
    def get(self, request):
        user = request.user
        # 验证登录
        if user.is_authenticated:
            # 获取查询的字符串数据
            role = request.GET.get('role')
            # 房东
            if role == 'landlord':
                try:
                    id = request.user.id
                    user = User.objects.get(id=id)
                    houses = House.objects.filter(user=user)
                    orders = Order.objects.filter(house__in=houses)
                    orders_list = []
                    for order in orders:
                        data = {}
                        data['amount'] = order.amount  # 订单金额，以分为单位
                        data['comment'] = order.comment  # 订单评论/拒单原因
                        data['ctime'] = order.create_time  # 创建时间
                        data['days'] = order.days  # 入住天数
                        data['end_date'] = order.end_date  # 离开日期
                        data['order_id'] = order.id  # 订单id
                        data['img_url'] = settings.QINIUYUN_URL + str(order.house.index_image_url)  # 房屋图片地址
                        data['start_date'] = order.begin_date  # 入住日期
                        if order.status == 3:
                            data['status'] = 'RECEIVED'  # 订单状态
                        else:
                            data['status'] = Order.ORDER_STATUS_ENUM.get(order.status)
                        data['title'] = order.house.title  # 房屋标题
                        orders_list.append(data)
                except Exception as e:
                    return JsonResponse({
                        "errno": "4104",
                        "errmsg": "查询数据错误"
                    })
                return JsonResponse({
                    "data": {
                        "orders": orders_list
                    },
                    "errmsg": "ok",
                    "errno": 0
                })
            # 房客
            else:
                try:
                    id = request.user.id
                    user = User.objects.get(id=id)
                    orders = Order.objects.filter(user=user)
                    orders_list = []
                    for order in orders:
                        data = {}
                        data['amount'] = order.amount  # 订单金额
                        data['comment'] = order.comment  # 订单评论
                        data['ctime'] = order.create_time  # 创建时间
                        data['days'] = order.days  # 入住天数
                        data['end_date'] = order.end_date  # 离店日期
                        data['order_id'] = order.id
                        data['img_url'] = settings.QINIUYUN_URL + str(order.house.index_image_url)  # 房屋图片地址
                        data['start_date'] = order.begin_date  # 入住日期
                        data['status'] = Order.ORDER_STATUS_ENUM.get(order.status)  # 订单状态
                        data['title'] = order.house.title  # 房屋标题
                        orders_list.append(data)
                except Exception as e:
                    logger.error(e)
                    return JsonResponse({
                        "errno": "4104",
                        "errmsg": "查询数据库出错"
                    })
            return JsonResponse({
                "data": {
                    "orders": orders_list  # 订单列表
                },
                "errmsg": "ok",
                "errno": 0
            })


# 接单和拒单模块
class HandleOrderView(LoginRequiredMixin, View):
    # 两个请求相同时，后一个请求会把前一个请求覆盖掉
    def put(self, request, order_id):
        # 用来接收json数据，将json格式转换为字典，获取前台参数
        json_dict = json.loads(request.body)
        action = json_dict.get('action')  # 操作类型：accept接单，reject拒单
        reason = json_dict.get('reason')  # 拒单原因，拒单时需要传入
        # 判断order_id参数是否存在数据库
        try:
            order = Order.objects.get(id=order_id)
        except Exception as error:
            return JsonResponse({
                'errno': 4103,
                'errmsg': '参数错误'
            })

        # 判断是接单还是拒单
        if action == 'accept':
            # 修改订单状态
            try:
                order.status = 3
                house = House.objects.get(pk=order.house.id)
                house.order_count += 1  # 预定完成该房屋的订单数
                house.save()  # 修改结果返回并保存
                order.save()
            except Exception as error:
                return JsonResponse({
                    'errno': 4001,
                    'errmsg': 'db NG'
                })
            return JsonResponse({
                'errno': 0,
                'errmsg': 'ok'
            })
        elif action == 'reject':
            # 判断拒单原因参数是否存在
            if not reason:
                return JsonResponse({
                    'errno': 4103,
                    'errmsg': '参数错误'
                })
            # 修改订单状态
            order.status = 6  # 已拒单
            order.comment = reason  # 订单评论信息或者拒单原因
            order.save()  # 修改结果返回并保存
            return JsonResponse({
                'errno': 0,
                'errmsg': 'ok'
            })
        else:
            return JsonResponse({
                'errno': 4103,
                'errmsg': '参数错误'
            })


# 评价订单
class CommentOrderView(LoginRequiredMixin, View):
    # 两个请求相同时，后一个请求会把前一个请求覆盖掉
    def put(self, request, order_id):
        json_dict = json.loads(request.body)  # 获取最原始的请求体数据
        comment = json_dict.get('comment')  # 评论内容
        if not comment:
            return JsonResponse({
                'errno': 4103,
                'errmsg': '参数错误'
            })

        try:
            order = Order.objects.get(id=order_id)
        except Exception as error:
            return JsonResponse({
                'errno': 4103,
                'errmsg': '参数错误'
            })
        try:
            order.comment = comment
            order.status = 4  # 已完成
            order.save()  # 修改结果返回并保存
        except Exception as error:
            logger.error(error)
            return JsonResponse({
                'errno': 4103,
                'errmsg': '参数错误'
            })
        return JsonResponse({
            'errno': 0,
            'errmsg': 'ok'
        })
