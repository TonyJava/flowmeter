# coding=utf-8

from flowmeter.applications.core import dtu_region as core
from flowmeter.common.const import RoleType
from flowmeter.config.api import dtu_region as conf_region_api
from flowmeter.common.api.validators import param_check
from flowmeter.exceptions import ParameterErrorException
from flowmeter.common.api.validators import IntCheck


def add_region(region):
    """
    添加一个dtu区间
    :return:
    """
    must_dict = {
        "manufacturer_id": int,
        "total_num": int,
    }
    param_check(region, must_dict)

    region_info = core.find_can_alloc_region(region['total_num'])
    region_info['manufacturer_id'] = region['manufacturer_id']
    region_info['used_num'] = 0
    core.add_region(region_info)


def find_regions_by_query_terms(query_terms, page=None):
    """
    查找DTU区间
    """

    optional_dict = {
        "query_box": str,
    }
    param_check(query_terms, optional_dict=optional_dict)

    regions, num = core.find_dtu_regions_by_query_terms(query_terms, page)

    region_dicts = []
    for region in regions:
        region_dict = core.transfer_dtu_region_obj_to_dict(region)
        region_dicts.append(region_dict)

    return region_dicts, num


def find_regions_by_man_id(id):

    """
    查找DTU区间
    """

    regions = conf_region_api.find_region_by_manufacturer_id(id)

    region_dicts = []
    for region in regions:
        region_dict = core.transfer_dtu_region_obj_to_dict(region)
        region_dicts.append(region_dict)

    return region_dicts


def update_dtu_region(region_info):

    must_dict = {
        "id": int,
        "total_num": IntCheck.check_is_positive_int,
    }
    param_check(region_info, must_dict)

    region = conf_region_api.find_region_by_id(region_info['id'])
    total_num = region_info['total_num']
    # 先判断total_num是否合法
    if core.is_total_num_legal(region, total_num):
        core.update_region_total_num(region, total_num)
    else:
        raise ParameterErrorException("DTU最大数目：{}，太大，更新失败！".format(total_num))


def del_batch_region(region_ids):
    """
    :return:
    """
    for region_id in region_ids:
        core.check_region_can_del(region_id)

    conf_region_api.del_batch_region(region_ids)


def query_dtu_region_of_select_box(user):

    if user['role'] == RoleType.MANUFACTURER:
        dtu_regions = conf_region_api.find_can_used_regions_by_man_id(user['id'])
    else:
        dtu_regions = conf_region_api.find_all_can_used_regions()

    return dtu_regions

