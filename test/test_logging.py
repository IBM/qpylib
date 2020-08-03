# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=redefined-outer-name, unused-argument, invalid-name

from unittest.mock import patch
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler
import os
import pytest
from qpylib import qpylib, log_qpylib

APP_FILE_LOG_FORMAT = '[{0}] - [APP_ID/1001][NOT:{1}] {2}'

MANIFEST_JSON_ROOT_PATH = 'qpylib.app_qpylib.get_root_path'

def manifest_path(manifest_file):
    return os.path.join(os.path.dirname(__file__), 'manifests', manifest_file)

# This fixture avoids reading app id from the manifest.
# Setting default log level threshold is handled by separate fixtures.
@pytest.fixture(scope='module', autouse=True)
def bypass_manifest_lookup():
    with patch('qpylib.app_qpylib.get_app_id') as mock_get_app_id:
        mock_get_app_id.return_value = 1001
        yield

@pytest.fixture(scope='function')
def info_threshold():
    with patch('qpylib.log_qpylib.default_log_level') as mock_default_log_level:
        mock_default_log_level.return_value = logging.INFO
        yield

@pytest.fixture(scope='function')
def debug_threshold():
    with patch('qpylib.log_qpylib.default_log_level') as mock_default_log_level:
        mock_default_log_level.return_value = logging.DEBUG
        yield

@pytest.fixture(scope='function')
def set_console_ip():
    os.environ['QRADAR_CONSOLE_IP'] = '9.123.234.101'
    yield
    del os.environ['QRADAR_CONSOLE_IP']

@pytest.fixture(scope='function')
def set_console_ipv6():
    os.environ['QRADAR_CONSOLE_IP'] = '[9.123.234.101]'
    yield
    del os.environ['QRADAR_CONSOLE_IP']

@pytest.fixture(scope='function')
def env_app_root():
    os.environ['APP_ROOT'] = '/opt/app-root'
    yield
    del os.environ['APP_ROOT']

@pytest.fixture(scope='function', autouse=True)
def reset_globals():
    qpylib.app_qpylib.Q_CACHED_MANIFEST = None
    if qpylib.log_qpylib.QLOGGER != 0:
        qpylib.log_qpylib.QLOGGER.handlers.clear()

# pylint: disable=protected-access
def verify_log_file_content(log_path, expected_lines, not_expected_lines=[]): # pylint: disable=dangerous-default-value
    with open(log_path) as log_file:
        content = log_file.read()
        for line in expected_lines:
            assert APP_FILE_LOG_FORMAT.format(
                line['level'], log_qpylib._map_notification_code(line['level']), line['text']) in content
        for line in not_expected_lines:
            assert APP_FILE_LOG_FORMAT.format(
                line['level'], log_qpylib._map_notification_code(line['level']), line['text']) not in content

def test_log_file_location(env_app_root):
    assert log_qpylib._log_file_location() == '/opt/app-root/store/log/app.log'

def test_log_without_create_raises_error():
    with pytest.raises(RuntimeError, match='You cannot use log before logging has been initialised'):
        qpylib.log('hello')

def test_create_log_without_console_ip_env_var_raises_error(info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        with pytest.raises(KeyError, match='Environment variable QRADAR_CONSOLE_IP is not set'):
            qpylib.create_log()

def check_rotating_file_handler_attrs(handler):
    assert handler.maxBytes == 2097152
    assert handler.backupCount == 5

def test_create_log_with_ipv4(set_console_ip, info_threshold, tmpdir):
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = os.path.join(tmpdir.strpath, 'app.log')
        qpylib.create_log()
    assert len(qpylib.log_qpylib.QLOGGER.handlers) == 2
    for handler in qpylib.log_qpylib.QLOGGER.handlers:
        if isinstance(handler, SysLogHandler):
            assert handler.address[0] == '9.123.234.101'
        if isinstance(handler, RotatingFileHandler):
            check_rotating_file_handler_attrs(handler)

def test_create_log_with_ipv6(set_console_ipv6, info_threshold, tmpdir):
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = os.path.join(tmpdir.strpath, 'app.log')
        qpylib.create_log()
    assert len(qpylib.log_qpylib.QLOGGER.handlers) == 2
    for handler in qpylib.log_qpylib.QLOGGER.handlers:
        if isinstance(handler, SysLogHandler):
            assert handler.address[0] == '9.123.234.101'
        if isinstance(handler, RotatingFileHandler):
            check_rotating_file_handler_attrs(handler)

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_default_log_level_no_level_in_manifest(mock_manifest, set_console_ip):
    assert log_qpylib.default_log_level() == logging.INFO

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('loglevel.json'))
def test_default_log_level_read_from_manifest(mock_manifest, set_console_ip):
    assert log_qpylib.default_log_level() == logging.DEBUG

def test_all_log_levels_with_manifest_info_threshold(set_console_ip, info_threshold, tmpdir):
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
            {'level': 'ERROR', 'text': 'hello exception'}],
                                not_expected_lines=[{'level': 'DEBUG', 'text': 'hello debug'}])

def test_all_log_levels_with_manifest_debug_threshold(set_console_ip, debug_threshold, tmpdir):
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

def test_all_log_levels_with_set_debug_threshold(set_console_ip, info_threshold, tmpdir):
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

def test_all_log_levels_with_set_warning_threshold(set_console_ip, info_threshold, tmpdir):
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
            {'level': 'ERROR', 'text': 'hello exception'}],
                                not_expected_lines=[
                                    {'level': 'DEBUG', 'text': 'hello debug'},
                                    {'level': 'INFO', 'text': 'hello default info'},
                                    {'level': 'INFO', 'text': 'hello info'}])

def test_log_with_bad_level_uses_info(set_console_ip, info_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
        qpylib.log('hello', 'BAD')
        verify_log_file_content(log_path, [{'level': 'INFO', 'text': 'hello'}])

def test_set_log_level_with_bad_level_uses_info(set_console_ip, debug_threshold, tmpdir):
    log_path = os.path.join(tmpdir.strpath, 'app.log')
    with patch('qpylib.log_qpylib._log_file_location') as mock_log_location:
        mock_log_location.return_value = log_path
        qpylib.create_log()
        qpylib.set_log_level('BAD')
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
            {'level': 'ERROR', 'text': 'hello exception'}],
                                not_expected_lines=[{'level': 'DEBUG', 'text': 'hello debug'}])
