# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=redefined-outer-name, unused-argument, invalid-name, protected-access

from unittest.mock import patch
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler
import os
import pytest
from qpylib import qpylib, log_qpylib, app_qpylib

@pytest.fixture(scope='function', autouse=True)
def reset_globals():
    app_qpylib.Q_CACHED_MANIFEST = None
    if log_qpylib.QLOGGER:
        log_qpylib.QLOGGER.handlers.clear()
    log_qpylib.QLOGGER = None
    log_qpylib.LOG_LEVEL_TO_FUNCTION = None

@pytest.fixture(scope='module', autouse=True)
def set_env_vars():
    os.environ['QRADAR_APP_ID'] = '1001'
    os.environ['APP_ROOT'] = '/opt/app-root'
    yield
    del os.environ['QRADAR_APP_ID']
    del os.environ['APP_ROOT']

@pytest.fixture(scope='function')
def set_console_ip():
    os.environ['QRADAR_CONSOLE_IP'] = '9.123.234.101'
    yield
    del os.environ['QRADAR_CONSOLE_IP']

@pytest.fixture(scope='function')
def set_app_uuid():
    os.environ['QRADAR_APP_UUID'] = 'd9830bbb-5958-4e42-acc8-0e7ac5182c0a'
    yield
    del os.environ['QRADAR_APP_UUID']

# Threshold fixtures are used to control logger.setLevel in create_log().
@pytest.fixture(scope='function')
def info_threshold():
    with patch('qpylib.log_qpylib._default_log_level') as mock_default_log_level:
        mock_default_log_level.return_value = logging.INFO
        yield

@pytest.fixture(scope='function')
def debug_threshold():
    with patch('qpylib.log_qpylib._default_log_level') as mock_default_log_level:
        mock_default_log_level.return_value = logging.DEBUG
        yield

# ==== _log_file_location ====

def test_log_file_location():
    assert log_qpylib._log_file_location() == '/opt/app-root/store/log/app.log'

# ==== _default_log_level ====

MANIFEST_JSON_ROOT_PATH = 'qpylib.app_qpylib.get_root_path'

def manifest_path(manifest_file):
    return os.path.join(os.path.dirname(__file__), 'manifests', manifest_file)

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_default_log_level_no_level_in_manifest_returns_info(mock_manifest):
    assert log_qpylib._default_log_level() == 'INFO'

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('loglevel.json'))
def test_default_log_level_read_from_manifest(mock_manifest):
    assert log_qpylib._default_log_level() == 'DEBUG'

# ==== _get_address_for_syslog ====

def test_get_address_for_syslog_ipv4():
    with patch('qpylib.app_qpylib.get_console_ip') as mock_console_ip:
        mock_console_ip.return_value = '9.123.234.101'
        address = log_qpylib._get_address_for_syslog()
    assert address[0] == '9.123.234.101'
    assert address[1] == 514

def test_get_address_for_syslog_ipv6():
    with patch('qpylib.app_qpylib.get_console_ip') as mock_console_ip:
        mock_console_ip.return_value = '[2001:db8:85a3:8d3:1319:8a2e:370:7348]'
        address = log_qpylib._get_address_for_syslog()
    assert address[0] == '2001:db8:85a3:8d3:1319:8a2e:370:7348'
    assert address[1] == 514

# ==== _create_sanitized_app_name ====

GET_APP_NAME = 'qpylib.app_qpylib.get_app_name'

@patch(GET_APP_NAME, return_value='abcz_ABCZ (1234567890) !@£$%^&*+-={}[]:";|\\<>,.?/`~')
def test_create_sanitized_app_name_strips_invalid_chars(mock_get_app_name):
    assert log_qpylib._create_sanitized_app_name() == 'abcz_ABCZ1234567890'

@patch(GET_APP_NAME, return_value='MyAppNameIsVeryLongSoThatICanMakeThisTestSucceedByeBye')
def test_create_sanitized_app_name_truncates_to_48_chars(mock_get_app_name):
    assert log_qpylib._create_sanitized_app_name() == \
        'MyAppNameIsVeryLongSoThatICanMakeThisTestSucceed'

# ==== create_log ====

def test_create_log_without_console_ip_skips_syslog_handler(set_app_uuid, info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
    assert len(log_qpylib.QLOGGER.handlers) == 1
    assert isinstance(log_qpylib.QLOGGER.handlers[0], RotatingFileHandler)

def test_create_log_without_console_ip_skips_syslog_handler_syslog_on(set_app_uuid, info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log(True)
    assert len(log_qpylib.QLOGGER.handlers) == 1
    assert isinstance(log_qpylib.QLOGGER.handlers[0], RotatingFileHandler)

def test_create_log_without_console_ip_skips_syslog_handler_syslog_off(set_app_uuid, info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log(False)
    assert len(log_qpylib.QLOGGER.handlers) == 1
    assert isinstance(log_qpylib.QLOGGER.handlers[0], RotatingFileHandler)

def test_create_log_without_qradar_app_uuid_skips_syslog_handler(set_console_ip, info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
    assert len(log_qpylib.QLOGGER.handlers) == 1
    assert isinstance(log_qpylib.QLOGGER.handlers[0], RotatingFileHandler)

def test_create_log_without_qradar_app_uuid_skips_syslog_handler_syslog_on(set_console_ip, info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log(True)
    assert len(log_qpylib.QLOGGER.handlers) == 1
    assert isinstance(log_qpylib.QLOGGER.handlers[0], RotatingFileHandler)

def test_create_log_without_qradar_app_uuid_skips_syslog_handler_syslog_off(set_console_ip, info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log(False)
    assert len(log_qpylib.QLOGGER.handlers) == 1
    assert isinstance(log_qpylib.QLOGGER.handlers[0], RotatingFileHandler)

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_create_log_all_handlers(mock_manifest, set_console_ip, set_app_uuid,
                                 info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
    assert log_qpylib.QLOGGER.getEffectiveLevel() == logging.INFO
    assert len(log_qpylib.QLOGGER.handlers) == 2
    for handler in log_qpylib.QLOGGER.handlers:
        if isinstance(handler, SysLogHandler):
            check_syslog_handler_attrs(handler)
        if isinstance(handler, RotatingFileHandler):
            check_rotating_file_handler_attrs(handler, log_path)

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_create_log_all_handlers_syslog_on(mock_manifest, set_console_ip, set_app_uuid,
                                           info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log(True)
    assert log_qpylib.QLOGGER.getEffectiveLevel() == logging.INFO
    assert len(log_qpylib.QLOGGER.handlers) == 2
    for handler in log_qpylib.QLOGGER.handlers:
        if isinstance(handler, SysLogHandler):
            check_syslog_handler_attrs(handler)
        if isinstance(handler, RotatingFileHandler):
            check_rotating_file_handler_attrs(handler, log_path)

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_create_log_handlers_syslog_off(mock_manifest, set_console_ip, set_app_uuid,
                                        info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log(False)
    assert log_qpylib.QLOGGER.getEffectiveLevel() == logging.INFO
    assert len(log_qpylib.QLOGGER.handlers) == 1
    for handler in log_qpylib.QLOGGER.handlers:
        if isinstance(handler, RotatingFileHandler):
            check_rotating_file_handler_attrs(handler, log_path)

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_create_log_called_twice(mock_manifest, set_console_ip, set_app_uuid,
                                 info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
        qpylib.create_log()
    assert len(log_qpylib.QLOGGER.handlers) == 2

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_create_log_called_twice_syslog_on(mock_manifest, set_console_ip, set_app_uuid,
                                           info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log(True)
        qpylib.create_log(True)
    assert len(log_qpylib.QLOGGER.handlers) == 2

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_create_log_called_twice_syslog_off(mock_manifest, set_console_ip, set_app_uuid,
                                            info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log(False)
        qpylib.create_log(False)
    assert len(log_qpylib.QLOGGER.handlers) == 1

def check_rotating_file_handler_attrs(handler, log_path):
    assert handler.baseFilename == log_path
    assert handler.maxBytes == 2097152
    assert handler.backupCount == 5
    assert handler.formatter._fmt == \
        '%(asctime)s [%(threadName)s] [%(levelname)s] [APP_ID:1001] [NOT:%(ncode)s] %(message)s'

def check_syslog_handler_attrs(handler):
    assert handler.address[0] == '9.123.234.101'
    assert handler.address[1] == 514
    assert handler.formatter._fmt == \
        '1 %(asctime)s 015fbd9fdd86b30e LiveManifest 1001 - - [NOT:%(ncode)s] %(message)s'
    assert handler.formatter.datefmt == log_qpylib.SYSLOG_TIME_FORMAT

# ==== set_log_level ====

def test_set_log_level_without_create_raises_error():
    with pytest.raises(RuntimeError, match='You cannot use set_log_level before logging has been initialised'):
        qpylib.set_log_level('DEBUG')

def test_set_log_level_with_bad_level_raises_error(info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
        with pytest.raises(ValueError, match="Unknown level: 'BAD'"):
            qpylib.set_log_level('BAD')

def test_set_log_level_sets_correct_level(info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
    qpylib.set_log_level('DEBUG')
    assert log_qpylib.QLOGGER.getEffectiveLevel() == logging.DEBUG

# ==== log ====

def test_log_without_create_raises_error():
    with pytest.raises(RuntimeError, match='You cannot use log before logging has been initialised'):
        qpylib.log('hello')

APP_FILE_LOG_FORMAT = '[{0}] [APP_ID:1001] [NOT:{1}] {2}'

def level_to_code(level):
    return log_qpylib.NotificationCodeFilter._log_level_to_notification_code.get(level)

# pylint: disable=dangerous-default-value
def verify_log_file_content(log_path, expected_lines, not_expected_lines=[]):
    with open(log_path) as log_file:
        content = log_file.read()
        for line in expected_lines:
            assert APP_FILE_LOG_FORMAT.format(
                line['level'], level_to_code(line['level']), line['text']) in content
        for line in not_expected_lines:
            assert APP_FILE_LOG_FORMAT.format(
                line['level'], level_to_code(line['level']), line['text']) not in content

# Verification of log content is not possible for SysLogHandler, so all of the
# following tests don't set QRADAR_CONSOLE_IP and only check RotatingFileHandler output.

def test_log_with_bad_level_raises_error(info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
        with pytest.raises(ValueError, match="Unknown level: 'BAD'"):
            qpylib.log('hello', 'BAD')

def test_all_log_levels_with_manifest_info_threshold(info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
        qpylib.log('hello debug', 'DEBUG')
        qpylib.log('hello default info')
        qpylib.log('hello info', 'INFO')
        qpylib.log('hello warning', 'WARNING')
        qpylib.log('hello error', 'ERROR')
        qpylib.log('hello critical', 'CRITICAL')
        qpylib.log('hello exception', 'EXCEPTION')
    verify_log_file_content(log_path, [
        {'level': 'INFO', 'text': 'hello default info'},
        {'level': 'INFO', 'text': 'hello info'},
        {'level': 'WARNING', 'text': 'hello warning'},
        {'level': 'ERROR', 'text': 'hello error'},
        {'level': 'CRITICAL', 'text': 'hello critical'},
        {'level': 'ERROR', 'text': 'hello exception'}], \
        not_expected_lines=[{'level': 'DEBUG', 'text': 'hello debug'}])

def test_all_log_levels_with_manifest_debug_threshold(debug_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
        qpylib.log('hello debug', 'DEBUG')
        qpylib.log('hello default info')
        qpylib.log('hello info', 'INFO')
        qpylib.log('hello warning', 'WARNING')
        qpylib.log('hello error', 'ERROR')
        qpylib.log('hello critical', 'CRITICAL')
        qpylib.log('hello exception', 'EXCEPTION')
    verify_log_file_content(log_path, [
        {'level': 'DEBUG', 'text': 'hello debug'},
        {'level': 'INFO', 'text': 'hello default info'},
        {'level': 'INFO', 'text': 'hello info'},
        {'level': 'WARNING', 'text': 'hello warning'},
        {'level': 'ERROR', 'text': 'hello error'},
        {'level': 'CRITICAL', 'text': 'hello critical'},
        {'level': 'ERROR', 'text': 'hello exception'}])

def test_all_log_levels_with_set_debug_threshold(info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
        qpylib.set_log_level('DEBUG')
        qpylib.log('hello debug', 'DEBUG')
        qpylib.log('hello default info')
        qpylib.log('hello info', 'INFO')
        qpylib.log('hello warning', 'WARNING')
        qpylib.log('hello error', 'ERROR')
        qpylib.log('hello critical', 'CRITICAL')
        qpylib.log('hello exception', 'EXCEPTION')
    verify_log_file_content(log_path, [
        {'level': 'DEBUG', 'text': 'hello debug'},
        {'level': 'INFO', 'text': 'hello default info'},
        {'level': 'INFO', 'text': 'hello info'},
        {'level': 'WARNING', 'text': 'hello warning'},
        {'level': 'ERROR', 'text': 'hello error'},
        {'level': 'CRITICAL', 'text': 'hello critical'},
        {'level': 'ERROR', 'text': 'hello exception'}])

def test_all_log_levels_with_set_warning_threshold(info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
        qpylib.set_log_level('WARNING')
        qpylib.log('hello debug', 'DEBUG')
        qpylib.log('hello default info')
        qpylib.log('hello info', 'INFO')
        qpylib.log('hello warning', 'WARNING')
        qpylib.log('hello error', 'ERROR')
        qpylib.log('hello critical', 'CRITICAL')
        qpylib.log('hello exception', 'EXCEPTION')
    verify_log_file_content(log_path, [
        {'level': 'WARNING', 'text': 'hello warning'},
        {'level': 'ERROR', 'text': 'hello error'},
        {'level': 'CRITICAL', 'text': 'hello critical'},
        {'level': 'ERROR', 'text': 'hello exception'}], \
        not_expected_lines=[
            {'level': 'DEBUG', 'text': 'hello debug'},
            {'level': 'INFO', 'text': 'hello default info'},
            {'level': 'INFO', 'text': 'hello info'}])
