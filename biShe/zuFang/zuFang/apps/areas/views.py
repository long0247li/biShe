from django.http import HttpRequest, HttpResponse, JsonResponse
# Django中配置文件settings全局变量的导入
from django.conf import settings
from django.views import View

# 自己写的打印错误方法
from areas.utils import return_err
from users.models import Area, House
# 登录访问控制，如果未登录则跳转到登录页面
from users.utils import LoginRequiredMixin


# 城区列表
class AreasView(View):
    # 获得城区数据
    def get(self, request: HttpRequest) -> HttpResponse:
        data = []
        try:
            # 返回QuerySet对象，支持迭代
            areas = Area.objects.all()
        except Exception as e:
            # 自己写的打印错误方法
            return return_err('4001', e)
        for area in areas:
            data.append({
                "aid": area.pk,  # 城区id
                "aname": area.name  # 城区名字
            })
        return JsonResponse({
            "errmsg": "获取成功",
            "errno": "0",
            'data': data
        })


# 用户房屋中心，我的房屋列表
class UserHouseView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        try:
            # 从数据库中取得匹配结果，返回一个对象列表
            houses = House.objects.filter(user=request.user)
        except Exception as e:
            return return_err(4001, e)
        house_list = []
        for house in houses:
            house_list.append({
                "address": house.address,  # 房屋地址
                "area_name": house.area.name,  # 城区名
                "ctime": house.create_time,  # 创建时间
                "house_id": house.id,  # 房屋id
                "img_url": settings.QINIUYUN_URL + house.index_image_url,  # 房屋图片
                "order_count": house.order_count,  # 订单数据
                "price": house.price,  # 价格
                "room_count": house.room_count,  # 房间数目
                "user_avatar": settings.QINIUYUN_URL + str(request.user.avatar),  # 该房屋所有者的头像
            })
        return JsonResponse({
            'errmsg': 'ok',
            'errno': 0,
            'data': {
                'houses': house_list  # 房屋列表
            }
        })
