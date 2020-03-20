# coding=utf-8
import datetime

from django.db.models import Q

from flowmeter import settings
from flowmeter.common.api.excel import Excel, ExcelField
from flowmeter.common.api.query import QueryTerms
from flowmeter.config.db.log_table import OprLog, SystemLog
from flowmeter.config.db.operator_table import Operator
from flowmeter.config.api import log as conf_log_api
from flowmeter.common.common import transfer_obj_to_dict


def __transfer_opr_log_database_to_display(oprlog_info):
    """
    将数据库中的值，转为前端显示的值
    :return:
    """
    # 格式化日期
    opr_time = oprlog_info['opr_time']
    oprlog_info['opr_time'] = str(opr_time.strftime(settings.DATETIME_FORMAT_STR))

    if 'state' in oprlog_info.keys():
        # 将英文的状态值，转化为中文
        state = oprlog_info['state']
        if state == OprLog.WAITE_STATE:
            state = '等待'
        elif state == OprLog.SUCCESS_STATE:
            state = '成功'
        elif state == OprLog.ERROR_STATE:
            state = '失败'
        oprlog_info['state'] = state

    opr_type_map = {
        Operator.QUERY: "查询",
        Operator.RECHARGE: "充值",
        Operator.SET_FLOW_RATIO: "设置流量系数",
        Operator.CLOSE_RECHARGE: "关闭预充值功能",
        Operator.OPEN_RECHARGE: "打开预充值功能",
        Operator.CLOSE_VALVE: "关阀",
        Operator.OPEN_VALVE: "开阀",
        Operator.SET_METER_ADDRESS: "设置仪表物理地址",
        Operator.RESET: "重启仪表",
    }

    oprlog_info['opr_type'] = opr_type_map[oprlog_info['opr_type']]


def __transfer_system_log_database_to_display(systemlog_info):
    """
    将系统日志数据库中的值，转为前端显示的值
    :return:
    """
    # 格式化日期
    opr_time = systemlog_info['opr_time']
    systemlog_info['opr_time'] = str(opr_time.strftime(settings.DATETIME_FORMAT_STR))

    if 'state' in systemlog_info.keys():
        # 将英文的状态值，转化为中文
        state = systemlog_info['state']
        if state == SystemLog.SUCCESS_STATE:
            state = '成功'
        elif state == SystemLog.ERROR_STATE:
            state = '失败'
        systemlog_info['state'] = state


def find_logs_by_query_terms(query_terms, page=None):
    name = query_terms.get('username')
    state = query_terms.get('state')
    opr_type = query_terms.get('opr_type')
    begin_time = query_terms.get('begin_time')
    if begin_time:
        begin_time = datetime.datetime.strptime(begin_time, '%Y-%m-%d')
    end_time = query_terms.get('end_time')
    if end_time:
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')

    # 构造创建时间的查询条件
    query_box = QueryTerms.make_and_query_terms(
        opr_user__name__icontains=name,
        state=state,
        opr_type=opr_type,
        opr_time__gte=begin_time,
        opr_time__lte=end_time
    )

    logs = conf_log_api.find_opr_log(query_box.get_filters(), page)

    return transfer_obj_to_dict(logs, ['id', 'opr_user.name', 'opr_time', 'val', 'state', 'opr_type',
                                       'meter.dtu.dtu_no', 'meter.address'], __transfer_opr_log_database_to_display)


def find_system_logs_by_query_terms(query_terms, page=None):
    query_box = query_terms.get('query_box')
    state = query_terms.get('state')
    begin_time = query_terms.get('begin_time')
    if begin_time:
        begin_time = datetime.datetime.strptime(begin_time, '%Y-%m-%d')
    end_time = query_terms.get('end_time')
    if end_time:
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')

    # 构造创建时间的查询条件
    query_and = QueryTerms.make_and_query_terms(
        state=state,
        opr_time__gte=begin_time,
        opr_time__lte=end_time
    )
    query_or = QueryTerms.make_or_query_terms(
        action_type__icontains=query_box,
        opr_user__name__icontains=query_box,
    )

    logs = conf_log_api.find_system_log(query_and.get_filters() & query_or.get_filters(), page)

    return transfer_obj_to_dict(logs, ['id', 'opr_user.name', 'opr_time', 'action_type', 'state'],
                                __transfer_system_log_database_to_display)


def find_alarm_logs_by_query_terms(query_terms, page=None):

    query_box = query_terms.get('query_box')
    state = query_terms.get('state')
    alarm_type = query_terms.get('alarm_type')
    begin_time = query_terms.get('begin_time')
    if begin_time:
        begin_time = datetime.datetime.strptime(begin_time, '%Y-%m-%d')
    end_time = query_terms.get('end_time')
    if end_time:
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')

    # 构造创建时间的查询条件
    query_or = QueryTerms.make_or_query_terms(
        meter__dtu__user__name__icontains=query_box,
        meter__dtu__region__manufacturer__name__icontains=query_box,
        meter__dtu__dtu_no__icontains=query_box,
        meter__address__icontains=query_box,
    )
    query_and = QueryTerms.make_and_query_terms(
        state=state,
        opr_time__gte=begin_time,
        opr_time__lte=end_time,
        alarm_type=alarm_type,
    )

    logs = conf_log_api.find_alarm_log(query_or.get_filters() & query_and.get_filters(), page)

    return transfer_obj_to_dict(logs, ['id', 'meter.dtu.user.name', 'meter.dtu.region.manufacturer.name',
                                       'alarm_type', 'state', 'meter.address', 'meter.dtu.dtu_no'],
                                __transfer_system_log_database_to_display)


def render_action_type_str(msg, data_field, param):
    """
    渲染信息字符串
    :return:
    """
    param_dict = {data: param[data] for data in data_field}
    return msg.format(**param_dict)


def __log_export(log_dict_list, sheet_name, filename, excel_fields):
    """
    将日志导出到EXCEL文件中
    """

    excel = Excel(excel_fields)
    excel.obj_dict_list = log_dict_list
    excel.write(filename, sheet_name)


def systemlog_export(systemlog_ids, filename):
    """
    将系统日志导出到文件中
    :param systemlog_ids:
    :param filename:
    :return:
    """
    prop_list = ['opr_user_name', 'action_type', 'state',  'opr_time']
    name_list = ['操作人员名称', '行为', '状态', '操作日期']
    excel_fields = []
    for index in range(0, len(prop_list)):
        excel_fields.append(ExcelField.require_field(prop_list[index], name_list[index]))

    logs = conf_log_api.find_system_log(Q(id__in=systemlog_ids))
    log_dicts = transfer_obj_to_dict(logs, ['id', 'opr_user.name', 'opr_time', 'action_type', 'state'],
                                     __transfer_system_log_database_to_display)

    __log_export(log_dicts, '系统日志列表', filename, excel_fields)
