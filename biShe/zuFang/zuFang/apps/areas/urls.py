from django.urls import re_path
from . import views

urlpatterns = [
    # 城区列表
    re_path(r'^api/v1.0/areas$', views.AreasView.as_view()),
    # 用户房屋中心，我的房屋列表
    re_path(r'^api/v1.0/user/houses$', views.UserHouseView.as_view()),
]
