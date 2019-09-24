# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os
from logging.handlers import RotatingFileHandler, SysLogHandler
from . import app_qpylib
from . import util_qpylib

APP_FILE_LOG_FORMAT = '%(asctime)s [%(module)s.%(funcName)s] [%(threadName)s] [%(levelname)s] - %(message)s'
APP_CONSOLE_LOG_FORMAT = '%(asctime)s %(module)s.%(funcName)s: %(message)s'

qlogger = 0
    
def log(message, level):
    log_fn = _choose_log_fn(level)
    log_fn("[APP_ID/{0}][NOT:{1}] {2}".format(
           app_qpylib.get_app_id(), _map_notification_code(level), message))

def create_log():
    global qlogger
    qlogger = logging.getLogger('com.ibm.applicationLogger')
    qlogger.setLevel(default_log_level())

    handler = RotatingFileHandler(_log_file_location(), maxBytes=2*1024*1024, backupCount=5)
    handler.setFormatter(logging.Formatter(APP_FILE_LOG_FORMAT))
    qlogger.addHandler(handler)

    if not util_qpylib.is_sdk():
        console_ip = app_qpylib.get_console_ip()
        if util_qpylib.is_ipv6_address(console_ip):
            console_ip = console_ip[1:-1]
        syslogHandler = SysLogHandler(address=(console_ip, 514))
        syslogHandler.setFormatter(logging.Formatter(APP_CONSOLE_LOG_FORMAT))
        qlogger.addHandler(syslogHandler)

def set_log_level(level='INFO'):
    global qlogger
    qlogger.setLevel(_map_log_level(level))

def default_log_level():
    return _map_log_level(app_qpylib.get_manifest_field_value('log_level', 'INFO'))

def _log_file_location():
    return os.path.join(app_qpylib.get_store_path('log'), 'app.log')

def _choose_log_fn(level):
    global qlogger
    if qlogger == 0:
        raise RuntimeError('You cannot use log before logging has been initialised')
    return {
        'INFO': qlogger.info,
        'DEBUG': qlogger.debug,
        'WARNING': qlogger.warning,
        'ERROR': qlogger.error,
        'CRITICAL': qlogger.critical
    }.get(level.upper(), qlogger.info)

def _map_notification_code(level):
    return {
        'INFO': "0000006000",
        'DEBUG': "0000006000",
        'WARNING': "0000004000",
        'ERROR': "0000003000",
        'CRITICAL': "0000003000"
    }.get(level.upper(), "0000006000")

def _map_log_level(level):
    return {
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }.get(level.upper(), logging.INFO)
