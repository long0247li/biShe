from django.urls import re_path
from . import views

urlpatterns = [
    # 个人中心
    re_path('^api/v1.0/user$', views.PersonalInfoView.as_view()),
    # 用户头像
    re_path('^api/v1.0/user/avatar$', views.PersonalImageView.as_view()),
    # 修改姓名
    re_path('^api/v1.0/user/name$', views.PersonalNameView.as_view()),
    # 用户实名认证
    re_path('^api/v1.0/user/auth$', views.RealNameVerifyView.as_view()),
]
