# coding=utf-8

from django.db import models
from flowmeter.config.db.dtu_table import Dtu
from flowmeter.config import const


class Meter(models.Model):

    # 所属于的DTU
    dtu = models.ForeignKey(Dtu, on_delete=models.CASCADE)
    # 在DTU内部的相对地址
    address = models.IntegerField(default=const.UNKNOWN_VALUE)
    # 仪表上一次采集数据的时间
    last_update_time = models.DateTimeField(null=True)
    # 剩余气量
    surplus_gas = models.FloatField(default=const.UNKNOWN_VALUE, null=True)
    # 剩余气体限值
    surplus_gas_limits = models.FloatField(default=const.UNKNOWN_VALUE, null=True)
    # 流量系数
    flow_ratio = models.FloatField(default=const.UNKNOWN_VALUE, null=True)
    # 瞬时流量
    flow_rate = models.FloatField(default=const.UNKNOWN_VALUE, null=True)
    # 累计流量
    total_flow = models.FloatField(default=const.UNKNOWN_VALUE, null=True)
    # 温度
    temperature = models.FloatField(default=const.UNKNOWN_VALUE, null=True)
    # 电压
    power = models.FloatField(default=const.UNKNOWN_VALUE, null=True)
    # 版本
    version = models.FloatField(default=const.UNKNOWN_VALUE, null=True)
    # 仪表备注
    remark = models.CharField(max_length=const.REMARK_CHAR_LEN, null=True)

    class Meta:
        unique_together = (("dtu", "address"),)
