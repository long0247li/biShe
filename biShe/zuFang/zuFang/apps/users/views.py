import logging
import random
import json
import re

# 状态保持
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, JsonResponse
from django.views import View

from django_redis import get_redis_connection
from zuFang.libs.captcha.captcha import captcha
from users.models import User

# 创建日志记录器：导入创建日志器才能使用
logger = logging.getLogger('django')


# 获取图形验证码
class YzCode(View):
    def get(self, request):
        cur = request.GET.get('cur')  # 验证码编号
        # http请求变为字典，检索字典的值
        pre = request.GET.get('pre')  # 上一次验证码编号
        # 1.调用工具类captcha生成图形验证码
        # 生成图片image和对应的内容text
        text, image = captcha.generate_captcha()

        # 2.链接redis，获取链接对象
        redis_conn = get_redis_connection('yzcode')
        if pre:
            # 删除数据库中的多余验证码
            redis_conn.delete('img_%s' % pre)

        # 3.利用链接对象，保存数据到redis，使用setex函数
        # redis_conn.setex('<key>', '<expire>', '<value>')
        redis_conn.setex('img_%s' % cur, 300, text)

        # 4.返回(图片)
        return HttpResponse(image)


# 获取短信验证码
class DxCode(View):
    def post(self, request):
        # json.loads(request.body.decode("utf-8"))
        # 获取前端传来的参数
        json_a = request.body
        # 以指定编码格式解码字符串
        json_str = json_a.decode()
        # 用来接收json数据，将json格式转换为字典
        dict = json.loads(json_str)
        mobile = dict.get('mobile')  # 手机号
        id = dict.get('id')  # 图形验证码编号
        text = dict.get('text')  # 图形验证码内容

        # 从数据库中取得匹配结果，返回一个对象列表
        # 从前端返回手机号在数据库中查找个数
        # 查询数据库中的手机
        try:
            count = User.objects.filter(username=mobile).count()
        except Exception as e:
            return JsonResponse({
                'code': 4004,
                'errmsg': '查询数据库出错'
            })
        # 判断手机号是否重复注册
        if count != 0:
            return JsonResponse({
                'code': 4003,
                'errmsg': '手机号重复注册'
            })

        # 校验
        # 如果所有都不
        if not all([mobile, id, text]):
            return JsonResponse({
                "errno": "4002",
                "errmsg": "缺少必传参数"
            })

        # 判断手机号是否有误
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({
                "errno": "4103",
                "errmsg": "手机号输入有误"
            })
        # 链接redis数据库
        redis_conn = get_redis_connection('yzcode')
        # 从redis中取值
        image_code_server = redis_conn.get('img_%s'% id)
        # 图形验证码过期或者不存在
        if image_code_server is None:
            return JsonResponse({
                'errno': 4002,
                'errmsg': '图形验证码失效'
            })
        # 删除图形验证码
        try:
            redis_conn.delete('cur')
        # e是异常类的一个实例，可以访问异常类的一些属性
        except Exception as e:
            # 输出日志，打印错误信息
            logger.error(e)
        # 对比验证码，以指定编码格式解码字符串
        image_code_server = image_code_server.decode()
        # 先将所有大写字符转换成小写，再进行比较
        if text.lower() != image_code_server.lower():
            return JsonResponse({
                'errno': 4103,
                'errmsg': '输入图形验证码有误'
            })
        flage = redis_conn.get('send_flag_%s'% mobile)
        if flage:
            # 获取过期时间，返回值：0表示无此键或已过期，None表示未设置过期时间，有过期时间的返回秒数
            tt = redis_conn.ttl('send_flag_%s'% mobile)
            print(tt)
            return JsonResponse({
                'errno': 4003,
                'errmsg': '频繁发送短信',
                'r_time': int(tt)
            })
        # 生成短信验证码，生成6位数验证码
        sms_code = '%06d' % random.randint(0, 999999)
        # 输出日志，打印信息
        logger.info(sms_code)

        # 利用链接对象，保存数据到redis，使用setex函数，键 过期时间 值
        redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        redis_conn.setex('send_flag_%s' % mobile, 60, 1)
        # 发送短信验证码
        # 短信模板
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # ccp_send_sms_code.delay(mobile, sms_code)

        # 10.响应结果
        return JsonResponse({
            'errno': 0,
            'errmsg': '发送成功'
        })


# 注册按钮
class ZhuCe(View):
    def post(self, request):
        # 获取参数
        # json.loads(request.body.decode("utf-8"))
        json_a = request.body
        # 以指定编码格式解码字符串
        json_str = json_a.decode()
        # 用来接收json数据，将json格式转换为字典
        dict = json.loads(json_str)
        mobile = dict.get("mobile")  # 手机号
        phonecode = dict.get("phonecode")  # 短信验证码
        password = dict.get("password")  # 密码
        # 校验
        # 如果所有都不
        if not all([mobile, phonecode, password]):
            return JsonResponse({
                "errno": "4002",
                "errmsg": "缺少必传参数"
            })

        # 判断输入的密码格式
        if not re.match("^[0-9A-Za-z]{6,20}$", password):
            return JsonResponse({
                "errno": "4103",
                "errmsg": "密码格式不符，密码为数字或英文，长度为6-20位"
            })

        # sms_code校验(链接redis数据库)
        redis_conn = get_redis_connection('yzcode')

        # 从redis中取值
        sms_code_server = redis_conn.get('sms_%s' % mobile)

        # 判断该值是否存在
        if not sms_code_server:
            return JsonResponse({
                'code': 4003,
                'errmsg': '手机号已存在'
            })

        # 把redis中取得值和前端发的值对比
        if phonecode != sms_code_server.decode():
            return JsonResponse({
                'code': 4002,
                'errmsg': '手机验证码过期'
            })

        # 保存到数据库
        try:
            user = User.objects.create_user(
                username=mobile,
                mobile=mobile,
                password=password
            )
        except Exception as e:
            # 输出日志，打印错误信息
            logger.error(e)
            return JsonResponse({
                'code': 4004,
                'errmsg': '保存到数据库出错'
            })

        # 状态保持，登录一个用户吧
        login(request, user)

        return JsonResponse({
            "errno": "0",
            "errmsg": "注册成功"
        })


# 登录
class DengLu(View):
    def post(self, request):
        # 获取参数
        json_a = request.body
        json_str = json_a.decode()
        dict = json.loads(json_str)
        # 电话号或用户名
        mobile = dict.get("mobile")
        # 密码
        password = dict.get("password")
        if not all([mobile, password]):
            return JsonResponse({
                "errno": "4002",
                "errmsg": "缺少必传参数"
            })

        # 验证是否能够登录
        user = authenticate(
            username=mobile,
            password=password
        )

        # 判断是否为空，如果为空返回
        if user is None:
            return JsonResponse({
                'code': 4004,
                'errmsg': '用户名或者密码错误'
            })

        login(request, user)

        return JsonResponse({
            "errno": "0",
            "errmsg": "登录成功"
        })

    # 判断是否登录
    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse({
                "errno": "0",
                "errmsg": "已登录",
                "data": {
                    "user_id": request.user.id,
                    "name": request.user.username
                }
            })
        else:
            return JsonResponse({
                "errno": 4101,
                "errmsg": "未登录"
            })

    # 退出登录
    def delete(self, request):
        # 退出登录，session会话信息全部清空
        logout(request)
        response = JsonResponse({
            "errno": "0",
            "errmsg": "已登出"
        })
        return response
