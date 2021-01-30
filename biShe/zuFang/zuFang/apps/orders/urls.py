from django.urls import re_path
from . import views

urlpatterns = [
    # 添加订单 获取订单列表
    re_path(r'^api/v1.0/orders$', views.AddOrderView.as_view()),
    # 接单和拒单模块
    re_path(r'^api/v1.0/orders/(?P<order_id>\d+)/status$', views.HandleOrderView.as_view()),
    # 评价订单
    re_path(r'^api/v1.0/orders/(?P<order_id>\d+)/comment$', views.CommentOrderView.as_view()),
]
