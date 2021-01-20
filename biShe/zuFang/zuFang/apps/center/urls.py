from django.urls import re_path
from . import views

urlpatterns = [
    # 个人中心
    re_path('^api/v1.0/user$', views.PersonalInfoView.as_view()),
]