import datetime
import json
import re

# 分页器Paginator,是导入了一个类，在用实列出来的对象调用方法，
from django.core.paginator import Paginator
# 对对象进行复杂查询，使用多样化的操作符生成sql语句
from django.db.models import Q
from django.http import HttpResponse, HttpRequest, JsonResponse
# Django中配置文件settings全局变量的导入
from django.conf import settings

from django.views import View

# 七牛云
from zuFang.utils.qiniu_storage import storage

# 自己写的打印错误方法
from areas.utils import return_err
from users.models import House, HouseImage, Area, Order
# 登录访问控制，如果未登录则跳转到登录页面
from users.utils import LoginRequiredMixin


# 发布房源 搜索房源
class HousesView(View):
    # 发布房源
    def post(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return JsonResponse({
                "errno": 4888,
                'errmsg': '请先登陆',
            })
        # 用来接收json数据，将json格式转换为字典，获取前台参数
        house_dict = json.loads(request.body)
        title = house_dict.get('title')  # 标题
        price = house_dict.get('price')  # 价格
        area_id = house_dict.get('area_id')  #城区id
        address = house_dict.get('address')  # 房屋地址
        room_count = house_dict.get('room_count')  # 房间数目
        acreage = house_dict.get('acreage')  # 房屋面积
        unit = house_dict.get('unit')  # 房屋单元，如：几室几厅
        capacity = house_dict.get('capacity')  # 房屋容纳的人数
        beds = house_dict.get('beds')  # 房屋床铺的配置
        deposit = house_dict.get('deposit')  # 房屋押金
        min_days = house_dict.get('min_days')  # 最少入住天数
        max_days = house_dict.get('max_days')  # 最大入住天数
        facility = house_dict.pop('facility')  # 用户选择设施id列表，如：[7,8]

        # 校验，如果所有都不
        if not all((title, price, area_id, address, room_count, acreage,
                    unit, capacity, beds, deposit, min_days)):
            return return_err(4002)
        try:
            # 城区id匹配数据库中的id数据
            Area.objects.get(pk=area_id)
        except Exception as e:
            return return_err(4103, e, '所在城区不正确')
        if not re.match(r"^[+-]?([0-9]*\.?[0-9]+|[0-9]+\.?[0-9]*)([eE][+-]?[0-9]+)?$", price):
            return return_err(4103, price, '价格错误不符合')
        if not re.match(r"^\d+$", deposit):
            return return_err(4103, deposit, '容纳人数不符合')
        if not re.match(r'[无一两二三四五六七八九十]室[无一二两三四五六七八九十]厅.{0,30}', unit) or len(unit) > 32:
            return return_err(4103, unit, '房间必须是几室几厅后跟具体设置，中文数字小于十可以写无，数据不可以太长')
        try:
            room_count = int(room_count)  # 房间数目
            acreage = int(acreage)  # 房屋面积
            capacity = int(capacity)  # 房屋容纳的人数
            min_days = int(min_days)  # 最少入住天数
            max_days = int(max_days)  # 最大入住天数
        except Exception as e:
            return return_err(4103, e, '请在需要数字的选项输入阿拉伯数字')
        if min_days <= 0 or (not max_days == 0 and max_days < min_days):
            return return_err(4103, min_days, '居住最大时间小于最小时间')
        try:
            # 创建并保存一个用户对象，request.user是用户模型对象
            house = House.objects.create(
                user=request.user,
                **house_dict
            )
            if facility:
                house.facility.add(*facility)
        except Exception as e:
            return return_err(4001, e, "新建数据错误")
        return JsonResponse({
            "errno": "0",
            "errmsg": "发布成功",
            "data": {
                "house_id": house.pk
            }
        })

    # 获取房源，房屋数据搜索
    # get参数通过url传递， post参数放在request.body中
    def get(self, request: HttpRequest) -> HttpResponse:
        # request.GET.get获取查询字符串数据
        aid = request.GET.get('aid')  # 区域id
        sd = request.GET.get('sd')  # 开始日期
        ed = request.GET.get('ed')  # 结束时间
        sk = request.GET.get('sk')  # 排序方式booking(订单量),price-inc(低到高),price-des(高到低)
        p = request.GET.get('p')  # 页数，不传默认值为1
        date_flag = True
        try:
            # 数据库过滤id为区域id，区域id存在，返回QuerySet对象，支持迭代
            addresses = Area.objects.filter(pk=aid) if aid else Area.objects.all()
        except Exception as e:
            return return_err(4001, e)
        if sd:  # 开始日期
            try:
                # 字符串转换为datetime类型
                sd = datetime.datetime.strptime(sd, '%Y-%m-%d').date()
            except Exception as e:
                return return_err(4103, e, '时间格式错误')
        else:
            # 系统当前日期
            sd = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
            sd = datetime.datetime.strptime(sd, '%Y-%m-%d').date()
            date_flag = False
        if ed:  # 结束时间
            try:
                # 字符串转换为datetime类型
                ed = datetime.datetime.strptime(ed, '%Y-%m-%d').date()
            except Exception as e:
                return return_err(4103, e, '时间格式错误')
        else:
            ed = datetime.datetime.strptime('9999-12-31', '%Y-%m-%d').date()
            date_flag = False
        ld = (ed - sd).days
        if date_flag and ld < 0:
            return return_err(4103, ld, '不能居住小于0天')
        # 条件成立返回if前面值，不成立返回if后面值
        o = '-update_time' if sk == 'new' else '-order_count' if sk == 'booking' else 'price' if sk == 'price-inc' else '-price'
        try:
            # 对对象进行复杂查询，使用多样化的操作符生成sql语句
            houses = House.objects.filter(area__in=addresses,
                                          min_days__lte=ld).filter(Q(max_days=0) |
                                                                   Q(max_days__gte=ld)).order_by(
                o) if date_flag else House.objects.filter(area__in=addresses).order_by(o)

            is_order_list = [order.house.pk for order in
                             Order.objects.filter(status=3).filter(
                                 ~Q(Q(begin_date__gte=ed) | Q(end_date__lte=sd)))]
        except Exception as e:
            return return_err(4001, e)
        try:
            # 分页器Paginator，每页显示的条数
            paginator = Paginator(houses, 2)  # 生成的每页的对象
            houses_page = paginator.page(p)  # 动态显示指定页码的数据
        except Exception as e:
            return return_err(4001, e)
        house_list = []
        for house in houses_page:
            house_list.append({
                "address": house.address,  # 房屋地址
                "area_name": house.area.name,  # 城区名
                "ctime": house.create_time,  # 创建时间
                "house_id": house.pk,  # 房屋id
                "img_url": settings.QINIUYUN_URL + house.index_image_url,  # 房屋图片
                "order_count": house.order_count,  # 订单数据
                "price": house.price,  # 价格
                "room_count": house.room_count,  # 房间数目
                "title": house.title,  # 标题
                "user_avatar": settings.QINIUYUN_URL + str(house.user.avatar),  # 该房屋所有者的头像
                'status': house.pk in is_order_list
            })
        return JsonResponse({
            'data': {'houses': house_list,  # 房屋列表
                     "total_page": paginator.num_pages  # 总页数
                     },
            "errmsg": "请求成功",
            "errno": "0"
        })


# 上传房源图片
class HousesImageView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, house_id) -> HttpResponse:
        image = request.FILES.get('house_image')  # 获得要上传的图片文件
        if not image:
            return return_err(4002, Exception(), '上传信息错误')
        with image.file as f:  # 读取文件
            url = storage(f.read())  # 从文件中读取指定的字节数，默认所有
        try:
            # 创建并保存一个用户对象
            HouseImage.objects.create(house_id=house_id, url=url)
            house = House.objects.get(pk=house_id)
            if not house.index_image_url:
                House.objects.filter(pk=house_id).update(index_image_url=url)  # 追加进数据库
        except Exception as e:
            return return_err(4001, e)
        return JsonResponse({
            "data": {
                "url": settings.QINIUYUN_URL + url  # 用户上传成功后的房源图片地址
            },
            "errno": "0",
            "errmsg": "图片上传成功"
        })


# 首页房屋推荐
class HouseIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        try:
            house_list = House.objects.filter(index_image_url__isnull=False).order_by('-order_count')
        except Exception as e:
            return return_err(4001, e)
        data = []
        for i, house in enumerate(house_list):  # 列出数据下标和数据
            if i > 4:
                break
            data.append({
                'house_id': house.pk,  # 房屋id
                'img_url': settings.QINIUYUN_URL + house.index_image_url,  # 房屋主图片
                'title': house.title  # 房屋标题
            })
        return JsonResponse({
            "errmsg": "ok",
            "errno": "0",
            'data': data
        })


# 房屋详情页面
class HouseDetailsView(View):
    def get(self, request, house_id):
        # 判断用户是否为登录用户
        user = request.user  # 请求的用户对象
        if user.is_authenticated:
            current_user_id = user.id
        else:
            current_user_id = -1
        try:
            # 返回的是字典，匹配参数是否正确
            house = House.objects.get(id=house_id)
        except Exception as error:
            return JsonResponse({
                'errno': 4103,
                'errmsg': '参数错误'
            })

        # 获取评价列表
        comments_list = list()
        try:
            # 订单数据库中查找，返回列表
            orders = Order.objects.filter(house=house)
        except Exception as error:
            return JsonResponse({
                'errno': 4001,
                'errmsg': '数据库查询错误'
            })

        for order in orders:
            comments_list.append({
                "comment": order.comment,  # 评论内容
                "ctime": order.update_time,  # 评论时间
                "user_name": order.user.username  # 评论人昵称
            })

        # 获取设施信息id列表
        facilities_list = list()
        try:
            facilities = house.facility.all()
        except Exception as error:
            return JsonResponse({
                'errno': 4001,
                'errmsg': '数据库查询错误'
            })
        for facility in facilities:
            facilities_list.append(facility.id)

        # 获取图片链接列表
        img_urls_list = list()
        try:
            images = HouseImage.objects.filter(house=house)
        except Exception as error:
            return JsonResponse({
                'errno': 4001,
                'errmsg': '数据库查询错误'
            })
        for image in images:
            img_urls_list.append(settings.QINIUYUN_URL + image.url)

        # 拼接参数
        house_info = {
            "acreage": house.acreage,  # 房屋面积
            "address": house.address,  # 房屋地址
            "beds": house.beds,  # 房屋床铺的配置
            "capacity": house.capacity,  # 房屋容纳的人数
            "comments": comments_list,  # 该房屋的评论列表
            "deposit": house.deposit,  # 房屋押金
            "facilities": facilities_list,  # 设施信息id列表
            "hid": house.id,  # 房屋id
            "img_urls": img_urls_list,  # 房屋图片列表
            "max_days": house.max_days,  # 最大入住天数
            "min_days": house.min_days,  # 最少入住天数
            "price": house.price,  # 价格
            "room_count": house.room_count,  # 房间数目
            'title': house.title,  # 标题
            'unit': house.unit,  # 房屋单元，如：几室几厅
            "user_avatar": settings.QINIUYUN_URL + str(house.user.avatar),  # 该房屋所有者的头像
            "user_id": house.user.id,  # 该房屋所有者的用户id
            "user_name": house.user.username  # 该房屋所有者的昵称
        }
        # 拼接参数
        data = {
            'house': house_info,  # 房屋详细信息
            'user_id': current_user_id  # 登录的用户id，没登录为-1
        }
        return JsonResponse({
            'data': data,
            'errmsg': "ok",
            "errno": 0
        })
