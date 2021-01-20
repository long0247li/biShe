from django.contrib.auth.backends import ModelBackend
import re
from .models import User
from django.http import JsonResponse


def get_user_by_account(account):
    # 判断account是否是手机号，返回user对象
    try:
        if re.match('^1[3-9]\d{9}$', account):
            # account是手机号
            # 根据手机号从数据库获取user对象返回
            user = User.objects.get(mobile=account)
        else:
            # account是用户名
            # 根据用户名从数据库获取user对象返回
            user = User.objects.get(username=account)
    except Exception as e:
        # 如果account既不是用户名也不是手机号
        # 我们返回None
        return None
    else:
        # 如果得到user，则返回user
        return user


# 继承自ModelBackend，重写authenticate函数
class UsernameMobileAuthBackend(ModelBackend):
    # 自定义用户认证后端,进行认证校验, 查看用户是否是声明的那一个
    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
        重写认证方法，实现用户名和mobile登录功能
        :param request:
        :param username:
        :param password:
        :param kwargs:
        :return:
        '''
        # 自定义验证用户是否存在的函数
        # 根据传入的username获取user对象
        # username可以是手机号也可以是账号
        user = get_user_by_account(username)

        # 校验user是否存在并校验密码是否正确
        if user and user.check_password(password):
            # 如果user存在，密码正确则返回user
            return user


def my_decorator(func):
    #自定义的装饰器，判断是否登录
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            # 如果用户登录，则进入这里正常执行
            return func(request, *args, **kwargs)
        else:
            # 如果用户未登录，则进入这里，返回400的状态码
            return JsonResponse({
                'errno': 4101,
                'errmsg': '请登录后重试'
            })
    return wrapper  # 调用内函数


class LoginRequiredMixin(object):
    # 自定义的Mixin扩展类
    # 重写的as_view方法
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        # 调用上面的装饰器进行过滤处理
        return my_decorator(view)
