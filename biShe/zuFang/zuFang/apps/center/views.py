import json
import logging
import re

# 创建日志记录器：导入创建日志器才能使用
logger = logging.getLogger('django')
# Django中配置文件settings全局变量的导入
from django.conf import settings
from django.http import JsonResponse
from django.views import View

from zuFang.utils.qiniu_storage import storage
from users.models import User
# 登录访问控制，如果未登录则跳转到登录页面
from users.utils import LoginRequiredMixin


# 个人中心
class PersonalInfoView(LoginRequiredMixin, View):
    def get(self, request):
        # user表的对象
        user = request.user
        # 返回的参数
        data = {
            # 用户头像，使用settings对象，自己七牛云空间的外链域名，用七牛云存储的图片上传数据库
            "avatar_url": settings.QINIUYUN_URL + str(user.avatar),
            "create_time": user.date_joined,  # 注册时间
            "mobile": user.mobile,  # 手机号
            "name": user.username,  # 用户名称
            "user_id": user.id  # 用户id
        }
        return JsonResponse({
            'data': data,  # 返回json对象参数
            'errmsg': 'ok',
            'errno': 0
        })


# 用户头像
class PersonalImageView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            # 等价于 request.FILES.get('avatar')
            data = request.FILES['avatar']  # 获得要上传的头像文件
            image = data.file.read()  # 从文件中读取指定的字节数，默认所有
        except Exception as e:
            # 输出日志，打印错误信息
            logger.error(e)
            return JsonResponse({
                'errno': 4103,
                'errmsg': '无图片'
            })
        key = storage(image)  # 七牛云上传图片，返回访问七牛获取图片的路径，也就是图片名
        url = settings.QINIUYUN_URL  # 自己七牛云上传空间外链域名
        user = request.user
        try:
            User.objects.filter(id=user.id).update(avatar=key)  # 过滤条件，把返回的字典图片名称追加到数据库中
        except Exception as e:
            # 输出日志，打印错误信息
            logger.error(e)
            return JsonResponse({
                'errno': 4001,
                'errmsg': '查询数据库失败'
            })
        return JsonResponse({
            "data": {
                "avatar_url": url + key  # 用户上传成功后的头像地址
            },
            "errno": "0",
            "errmsg": "头像上传成功"
        })


# 修改姓名
class PersonalNameView(LoginRequiredMixin, View):
    # 两个请求相同，后一个请求会把前一个请求覆盖掉
    def put(self, request):
        # 获取前端传来的参数
        data = request.body
        # 以指定解码方式获取前端的值，接收json数据方式获取前台参数
        name = json.loads(data.decode()).get('name')
        id = request.user.id  # user对象的用户id

        try:
            # 过滤条件，把前端返回的用户名追加到数据库中
            User.objects.filter(id=id).update(username=name)
        except Exception as e:
            # 输出日志，打印错误信息
            logger.error(e)
            return JsonResponse({
                'errno': 4001
            })
        return JsonResponse({
            "errno": 0,
            "errmsg": "修改成功"
        })


# 用户实名认证
class RealNameVerifyView(LoginRequiredMixin, View):
    def post(self, request):
        # 以指定解码方式获取前端的值
        data = request.body.decode()
        # 接收json数据方式获取前台参数
        real_dict = json.loads(data)
        real_name = real_dict.get('real_name')  # 用户真实姓名
        id_card = real_dict.get('id_card')  # 用户身份证号码
        if not all([real_name, id_card]):
            return JsonResponse({
                'errno': 4103,
                'errmsg': '缺少必传参数'
            })
        if not re.match('^[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$',id_card):
            return JsonResponse({
                'errno': 4103,
                'errmsg': '身份证号不符规范'
            })
        if not re.match('^[\u4e00-\u9fa5][\u4e00-\u9fa5]{1,5}$',real_name):
            return JsonResponse({
                'errno': 4103,
                'errmsg': '真实姓名要符合2-6个汉字的规范'
            })
        try:
            # 从数据库中取得匹配结果，返回一个对象列表
            user = User.objects.filter(id_card=id_card)
        except Exception as e:
            # 输出日志，打印错误信息
            logger.error(e)
            return JsonResponse({
                'errno': 4001,
                'errmsg': '查询数据库失败'
            })
        if user:
            return JsonResponse({
                'errno': 4001,
                'errmsg': '身份证已注册'
            })
        # user对象的用户id
        id = request.user.id
        user = request.user
        try:
            # 过滤条件，把前端返回的值追加到数据库中
            User.objects.filter(id=id).update(real_name=real_name,id_card=id_card)
        except Exception as e:
            # 输出日志，打印错误信息
            logger.error(e)
            return JsonResponse({
                'errno': 4001,
                'errmsg': '查询数据库失败'
            })
        # 保存进空的字典
        data = {}
        data['real_name'] = user.real_name
        data['id_card'] = user.id_card
        return JsonResponse({
            "errno": "0",
            "errmsg": "认证信息保存成功",
            'data': data
        })

    def get(self, request):
        id = request.user.id
        try:
            # 从数据库中取得匹配结果，返回一个对象列表
            user = User.objects.get(id=id)
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'errno': 4001,
                'errmsg': '查询数据库失败'
            })
        data = {}
        data['real_name'] = user.real_name
        data['id_card'] = user.id_card
        return JsonResponse({
            'errno': 0,
            'errmsg': 'ok',
            'data': data
        })
