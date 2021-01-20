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
# 登录访问控制，如果未登录则跳转到登录页面
from users.utils import LoginRequiredMixin


# 个人中心
class PersonalInfoView(LoginRequiredMixin, View):
    def get(self, request):
        # user表的对象
        user = request.user
        # 返回的参数
        data = {
            # 用户头像，使用settings对象，自己写的网址，用七牛云存储的图片上传数据库
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