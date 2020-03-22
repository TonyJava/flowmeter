# coding=utf-8
import datetime
import json

from flowmeter.celery_task.api import alarm_task
from flowmeter.common.const import RoleType
from flowmeter.config.api import log as conf_log_api
from flowmeter.config.api import alarm_log_reader as conf_reader_api
from flowmeter.config.api import cache as conf_cache_api
from flowmeter.config.api import meter as conf_meter_api
from flowmeter.config.const import SENSOR_ERROR_FLAG_TRUE, VALVE_ERROR_FLAG_TRUE, OWE_STATE_TRUE, VALVE_STATE_OPEN
from flowmeter.config.db.log_table import OprLog, AlarmLog
from flowmeter.common.api.validators import param_check, WhiteListCheck, StrCheck
from flowmeter.applications.core import log as core
from flowmeter.config.db.log_table import SystemLog


def find_logs_by_query_terms(query_terms, page=None):
    """
    :param page: 分页对象
    :param query_terms:
    :return: 查询到的操作日志列表
    """

    optional_dict = {
        "begin_time": str,
        "end_time": str,
        "username": str,
        "state": WhiteListCheck.check_opr_state,
        "opr_type": WhiteListCheck.check_opr_type,
    }
    param_check(query_terms, must_dict={}, optional_dict=optional_dict)

    logs = core.find_logs_by_query_terms(query_terms, page)

    return logs


def find_system_logs_by_query_terms(query_terms, page=None):
    """
    :param page: 分页对象
    :param query_terms:
    :return: 查询到的系统日志列表
    """

    optional_dict = {
        "begin_time": str,
        "end_time": str,
        "state": WhiteListCheck.check_opr_state,
        "query_box": StrCheck.check_action_type,
    }
    param_check(query_terms, must_dict={}, optional_dict=optional_dict)

    logs = core.find_system_logs_by_query_terms(query_terms, page)

    return logs


def find_alarm_logs_by_query_terms(query_terms, page=None):
    """
    :param page: 分页对象
    :param query_terms:
    :return: 查询到的警报日志列表
    """

    optional_dict = {
        "begin_time": str,
        "end_time": str,
        "query_box": str,
        "alarm_type": WhiteListCheck.check_alarm_type,
        "state": WhiteListCheck.check_opr_state,
    }
    param_check(query_terms, optional_dict=optional_dict)

    logs = core.find_alarm_logs_by_query_terms(query_terms, page)

    return logs


def update_logs_success_state(log_ids):

    conf_log_api.update_opr_logs_state(log_ids, OprLog.SUCCESS_STATE)


def del_opr_logs(opr_log_ids):
    """
    删除操作日志
    :param opr_log_ids:
    :return:
    """
    conf_log_api.del_opr_logs(opr_log_ids)


def del_system_logs(opr_log_ids):
    """
    删除系统日志
    :param opr_log_ids:
    :return:
    """
    conf_log_api.del_system_logs(opr_log_ids)


def del_alarm_logs(opr_log_ids):
    """
    删除警报日志
    :param opr_log_ids:
    :return:
    """
    conf_log_api.del_alarm_logs(opr_log_ids)


def add_system_log(log_dict):
    must_dict = {
        'action_type': StrCheck.check_action_type,
        'opr_user_id': int,
        'opr_time': datetime.datetime,
        'state': WhiteListCheck.check_opr_state,
    }
    optional_dict = {
        "msg": StrCheck.check_msg,
    }
    param_check(log_dict, must_dict, optional_dict)

    conf_log_api.add_system_log(log_dict)


def systemlog_export(systemlog_ids, filename):
    """
    将系统日志导出到文件中
    :param systemlog_ids:
    :param filename:
    :return:
    """
    StrCheck.check_not_null(filename)
    core.systemlog_export(systemlog_ids, filename)


def alarmlog_export(alarmlog_ids, filename):
    """
    将警报日志导出到文件中
    :param alarmlog_ids:
    :param filename:
    :return:
    """
    StrCheck.check_not_null(filename)
    core.alarmlog_export(alarmlog_ids, filename)


def oprlog_export(oprlog_ids, filename):
    """
    将警报日志导出到文件中
    :param oprlog_ids:
    :param filename:
    :return:
    """
    StrCheck.check_not_null(filename)
    core.oprlog_export(oprlog_ids, filename)


def read_alarm_log(alarm_log_id):
    """
    标记用户已经读过的警报
    :param alarm_log_id:
    :return:
    """
    conf_reader_api.read_alarm(alarm_log_id)


def render_msg(alarm_log, role_type):

    if role_type == RoleType.ADMIN:
        return "供气商：{}，DTU用户：{}，DTU编号：{}，发生了：{}！".\
            format(alarm_log.meter.dtu.region.manufacturer.name, alarm_log.meter.dtu.user.name,
                   alarm_log.meter.dtu.dtu_no, alarm_log.get_display_alarm_type())
    elif role_type == RoleType.MANUFACTURER:
        return "DTU用户：{}，DTU编号：{}，发生了：{}！". \
            format(alarm_log.meter.dtu.user.name,
                   alarm_log.meter.dtu.dtu_no, alarm_log.get_display_alarm_type())
    elif role_type == RoleType.DTU_USER:
        return "DTU编号：{}，发生了：{}！". \
            format(alarm_log.meter.dtu.dtu_no, alarm_log.get_display_alarm_type())


def check_and_send_alarm(meter_id, data, status=None):
    """
    检查并发送警报
    :param meter_id:
    :param data:
    :param status:
    :return:
    """
    if 'surplus_gas' in data.keys():
        if data['surplus_gas'] < conf_meter_api.get_meter_surplus_gas_limits(meter_id):
            log_dict = {'alarm_type': AlarmLog.ALARM_EXCEED_LIMIT, 'meter_id': meter_id,
                        'opr_time': datetime.datetime.now()}
            # 异步执行
            alarm_task.send_alarm.delay(log_dict)

    if status and isinstance(status, dict):
        sensor_state = status.get('sensor_state')
        if sensor_state and sensor_state == SENSOR_ERROR_FLAG_TRUE:
            log_dict = {'alarm_type': AlarmLog.ALARM_SENSOR_ERROR, 'meter_id': meter_id,
                        'opr_time': datetime.datetime.now()}
            # 异步执行
            alarm_task.send_alarm.delay(log_dict)

        valve_error_flag = status.get('valve_error_flag')
        if valve_error_flag and valve_error_flag == VALVE_ERROR_FLAG_TRUE:
            log_dict = {'alarm_type': AlarmLog.ALARM_VALVE_ERROR, 'meter_id': meter_id,
                        'opr_time': datetime.datetime.now()}
            # 异步执行
            alarm_task.send_alarm.delay(log_dict)

        owe_state = status.get('owe_state')
        valve_state = status.get('valve_state')
        if owe_state and valve_state and owe_state == OWE_STATE_TRUE and valve_state == VALVE_STATE_OPEN:
            log_dict = {'alarm_type': AlarmLog.ALARM_SUB_VALVE, 'meter_id': meter_id,
                        'opr_time': datetime.datetime.now()}
            # 异步执行
            alarm_task.send_alarm.delay(log_dict)

