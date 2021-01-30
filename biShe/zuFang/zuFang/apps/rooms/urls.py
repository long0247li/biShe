from django.urls import re_path
from . import views

urlpatterns = [
    # 发布房源和搜索房源
    re_path(r'^api/v1.0/houses$', views.HousesView.as_view()),
    # 上传房源照片
    re_path(r'^api/v1.0/houses/(?P<house_id>\d{0,10})/images$', views.HousesImageView.as_view()),
    # 首页房屋推荐
    re_path(r'^api/v1.0/houses/index$', views.HouseIndexView.as_view()),
    # 房屋详情页面
    re_path(r'^api/v1.0/houses/(?P<house_id>\d{0,10})$',views.HouseDetailsView.as_view()),
]
