from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.conf import settings


class BaseModel(models.Model):
    """为模型类补充字段"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时的时间，不会再更新
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")  # 更新为当前时间

    class Meta:
        abstract = True
        # 说明是抽象模型类, 用于继承使用，数据库迁移时不会创建BaseModel的表


# 我们重写用户模型类，继承自AbstractUser
class User(AbstractUser):
    # 自定义用户模型类
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")  # 字符型字段
    avatar = models.ImageField(null=True, blank=True, verbose_name='用户头像')  # 图像字段
    real_name = models.CharField(max_length=32, null=True, verbose_name="真实姓名")
    id_card = models.CharField(max_length=20, null=True, verbose_name="身份证号")

    class Meta:
        db_table = "tb_user"  # 设置表名


class Area(BaseModel):
    """城区"""

    name = models.CharField(max_length=32, null=False, verbose_name="区域名字")

    class Meta:
        db_table = "tb_area"


class Facility(BaseModel):
    """设施信息"""

    name = models.CharField(max_length=32, null=False, verbose_name="设施名字")

    class Meta:
        db_table = "tb_facility"


class House(BaseModel):
    """房屋信息"""
    # 一对多外键关联，on_delete要删除模型对象时，也会对该对象相关联的其他对象进行操作
    user = models.ForeignKey("User", related_name='houses', on_delete=models.CASCADE, verbose_name='房屋主人的用户编号')
    area = models.ForeignKey("Area", null=False, on_delete=models.CASCADE, verbose_name="归属地的区域编号")
    title = models.CharField(max_length=64, null=False, verbose_name="标题")
    price = models.IntegerField(default=0)  # 单价，单位：分，默认值0，整型字段
    address = models.CharField(max_length=512, default="")  # 地址
    room_count = models.IntegerField(default=1)  # 房间数目
    acreage = models.IntegerField(default=0)  # 房屋面积
    unit = models.CharField(max_length=32, default="")  # 房屋单元， 如几室几厅
    capacity = models.IntegerField(default=1)  # 房屋容纳的人数
    beds = models.CharField(max_length=64, default="")  # 房屋床铺的配置
    deposit = models.IntegerField(default=0)  # 房屋押金
    min_days = models.IntegerField(default=1)  # 最少入住天数
    max_days = models.IntegerField(default=0)  # 最多入住天数，0表示不限制
    order_count = models.IntegerField(default=0)  # 预订完成的该房屋的订单数
    index_image_url = models.CharField(max_length=256, default="")  # 房屋主图片的路径
    facility = models.ManyToManyField("Facility", verbose_name="和设施表之间多对多关系")

    class Meta:
        db_table = "tb_house"


class HouseImage(BaseModel):
    """
    房屋图片表
    """
    house = models.ForeignKey("House", on_delete=models.CASCADE)  # 房屋编号
    url = models.CharField(max_length=256, null=False)  # 图片的路径

    class Meta:
        db_table = "tb_house_image"


class Order(BaseModel):
    """订单"""
    ORDER_STATUS = {
        "WAIT_ACCEPT": 0,  # 待接单,
        "WAIT_PAYMENT": 1,  # 待支付
        "PAID": 2,  # 已支付
        "WAIT_COMMENT": 3,  # 待评价
        "COMPLETE": 4,  # 已完成
        "CANCELED": 5,  # 已取消
        "REJECTED": 6  # 已拒单
    }

    ORDER_STATUS_ENUM = {
        0: "WAIT_ACCEPT",  # 待接单,
        1: "WAIT_PAYMENT",  # 待支付
        2: "PAID",  # 已支付
        3: "WAIT_COMMENT",  # 待评价
        4: "COMPLETE",  # 已完成
        5: "CANCELED",  # 已取消
        6: "REJECTED"  # 已拒单
    }
    ORDER_STATUS_CHOICES = (
        (0, "WAIT_ACCEPT"),  # 待接单,
        (1, "WAIT_PAYMENT"),  # 待支付
        (2, "PAID"),  # 已支付
        (3, "WAIT_COMMENT"),  # 待评价
        (4, "COMPLETE"),  # 已完成
        (5, "CANCELED"),  # 已取消
        (6, "REJECTED")  # 已拒单
    )

    user = models.ForeignKey("User", related_name="orders", on_delete=models.CASCADE, verbose_name="下订单的用户编号")
    house = models.ForeignKey("House", on_delete=models.CASCADE, verbose_name="预订的房间编号")
    begin_date = models.DateField(null=False, verbose_name="预订的起始时间")  # 日期字段
    end_date = models.DateField(null=False, verbose_name="结束时间")
    days = models.IntegerField(null=False, verbose_name="预订的总天数")
    house_price = models.IntegerField(null=False, verbose_name="房屋单价")
    amount = models.IntegerField(null=False, verbose_name="订单总金额")
    status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=0, db_index=True, verbose_name="订单状态")
    comment = models.TextField(null=True, verbose_name="订单的评论信息或者拒单原因")  # 长文档

    class Meta:
        db_table = "tb_order"
