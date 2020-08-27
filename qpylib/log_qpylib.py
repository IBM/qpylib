# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import logging
from logging.handlers import RotatingFileHandler, SysLogHandler
import re
from . import app_qpylib, util_qpylib

# Log format for local file logging.
# Uses default date/time formatting from logging module.
# Before the logging formatter is created, APPID is substituted with the actual app ID,
# which is constant for all logs generated within an app container.
# Example: 2020-08-19 12:48:11,423 [Thread-4] [INFO] [APP_ID:1005] [NOT:0000006000] hello

APP_FILE_LOG_FORMAT = '%(asctime)s [%(threadName)s] [%(levelname)s] [APP_ID:APPID] [NOT:%(ncode)s] %(message)s'

# Log format for Syslog.
# See https://tools.ietf.org/html/rfc5424 for more details on the following specification:
# SYSLOG-MSG = HEADER SP STRUCTURED-DATA SP MSG
# HEADER = PRI VERSION SP TIMESTAMP SP HOSTNAME SP APPNAME SP PROCID SP MSGID
# PRI is taken care of by SysLogHandler and not included in the log format below.
# VERSION is hard-coded to 1.
# TIMESTAMP in the specification is e.g. 2020-04-12T19:20:50.345678+01:00
#   Seconds fraction is not supported in "time" module, which is what the logging
#   module uses. SYSLOG_LOG_FORMAT uses asctime formatted with SYSLOG_TIME_FORMAT.
# HOSTNAME is set to the container IP address.
# APPNAME is set to a sanitised copy of the app manifest name field.
# PROCID is set to the app ID.
#   HOSTNAME, APPNAME and PROCID are all constants, replaced in the format string with their values.
# MSGID and STRUCTURED-DATA are set to the Syslog nil value '-'.
# Example: <14>1 2020-08-21T14:16:51+0100 192.168.0.15 MyExampleApp 1005 - - [NOT:0000006000] hello

SYSLOG_LOG_FORMAT = '1 %(asctime)s HOSTNAME APPNAME PROCID - - [NOT:%(ncode)s] %(message)s'
SYSLOG_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

# Globals related to logging.Logger instance.
QLOGGER = None
LOG_LEVEL_TO_FUNCTION = None

def create_log():
    global QLOGGER
    QLOGGER = logging.getLogger('com.ibm.applicationLogger')
    QLOGGER.setLevel(_default_log_level())
    QLOGGER.addFilter(NotificationCodeFilter())

    for handler in _generate_handlers():
        QLOGGER.addHandler(handler)

    global LOG_LEVEL_TO_FUNCTION
    LOG_LEVEL_TO_FUNCTION = {
        'DEBUG': QLOGGER.debug,
        'INFO': QLOGGER.info,
        'WARNING': QLOGGER.warning,
        'ERROR': QLOGGER.error,
        'EXCEPTION': QLOGGER.exception,
        'CRITICAL': QLOGGER.critical
    }

def log(message, level):
    global LOG_LEVEL_TO_FUNCTION
    if not LOG_LEVEL_TO_FUNCTION:
        raise RuntimeError('You cannot use log before logging has been initialised')
    log_function = LOG_LEVEL_TO_FUNCTION.get(level.upper())
    if not log_function:
        raise ValueError("Unknown level: '{0}'".format(level))
    log_function(message)

def set_log_level(level='INFO'):
    global QLOGGER
    if not QLOGGER:
        raise RuntimeError('You cannot use set_log_level before logging has been initialised')
    QLOGGER.setLevel(level.upper())

def _default_log_level():
    return app_qpylib.get_manifest_field_value('log_level', 'INFO').upper()

def _log_file_location():
    return app_qpylib.get_log_path('app.log')

def _generate_handlers():
    handlers = []

    app_id = str(app_qpylib.get_app_id())
    handlers.append(_create_file_handler(app_id))

    address = None
    try:
        address = _get_address_for_syslog()
    except KeyError:
        pass
    if address:
        handlers.append(_create_syslog_handler(address, app_id))

    return handlers

def _create_file_handler(app_id):
    handler = RotatingFileHandler(_log_file_location(), maxBytes=2*1024*1024, backupCount=5)
    log_format = APP_FILE_LOG_FORMAT.replace('APPID', app_id)
    handler.setFormatter(logging.Formatter(log_format))
    return handler

def _create_syslog_handler(syslog_address, app_id):
    handler = SysLogHandler(address=syslog_address)
    log_format = _create_syslog_log_format(app_id)
    handler.setFormatter(logging.Formatter(log_format, SYSLOG_TIME_FORMAT))
    return handler

def _get_address_for_syslog():
    console_ip = app_qpylib.get_console_ip()
    if util_qpylib.is_ipv6_address(console_ip):
        console_ip = console_ip[1:-1]
    return (console_ip, 514)

def _create_syslog_log_format(app_id):
    return SYSLOG_LOG_FORMAT.replace('HOSTNAME', util_qpylib.get_container_ip()) \
                            .replace('APPNAME', _create_sanitized_app_name()) \
                            .replace('PROCID', app_id)

def _create_sanitized_app_name():
    ''' Extracts app name from manifest, strips unwanted characters,
        and truncates to max length 48, as per RFC5424.
    '''
    return re.sub(r'\W+', '', app_qpylib.get_app_name())[:48]

class NotificationCodeFilter(logging.Filter):
    ''' Filter which adds a field named ncode to each log record.
        Allows notification code to be specified in log handler
        format strings.
    '''
    # These are standard QRadar codes for identifying log levels.
    Q_INFO_CODE = '0000006000'
    Q_WARNING_CODE = '0000004000'
    Q_ERROR_CODE = '0000003000'

    def filter(self, record):
        record.ncode = self._log_level_to_notification_code.get(
            record.levelname.upper(), self.Q_INFO_CODE)
        return True

    _log_level_to_notification_code = {
        'DEBUG': Q_INFO_CODE,
        'INFO': Q_INFO_CODE,
        'WARNING': Q_WARNING_CODE,
        'ERROR': Q_ERROR_CODE,
        'CRITICAL': Q_ERROR_CODE
    }
