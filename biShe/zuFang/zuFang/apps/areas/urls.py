from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^api/v1.0/areas$', views.AreasView.as_view()),
    re_path(r'^api/v1.0/user/houses$', views.UserHouseView.as_view()),
]