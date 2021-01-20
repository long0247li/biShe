from django.urls import re_path
from . import views

urlpatterns = [
    # 发送图形验证码
    re_path(r"^api/v1.0/imagecode/$", views.YzCode.as_view()),
    # 发送短信验证码
    re_path(r"^api/v1.0/sms/$", views.DxCode.as_view()),
    # 注册按钮
    re_path(r"^api/v1.0/users$", views.ZhuCe.as_view()),
    # 登录
    re_path(r"^api/v1.0/session$", views.DengLu.as_view()),
]
