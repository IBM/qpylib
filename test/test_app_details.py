# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=unused-argument, redefined-outer-name, invalid-name

from unittest.mock import patch
import os
import pytest
from qpylib import qpylib, app_qpylib

MANIFEST_JSON_ROOT_PATH = 'qpylib.app_qpylib.get_root_path'

def manifest_path(manifest_file):
    return os.path.join(os.path.dirname(__file__), 'manifests', manifest_file)

@pytest.fixture(scope='function', autouse=True)
def clear_manifest_cache():
    with patch('qpylib.app_qpylib.Q_CACHED_MANIFEST', None):
        yield

@pytest.fixture(scope='function')
def env_qradar_console_ip():
    os.environ['QRADAR_CONSOLE_IP'] = '9.123.234.101'
    yield
    del os.environ['QRADAR_CONSOLE_IP']

@pytest.fixture(scope='function')
def env_app_root():
    os.environ['APP_ROOT'] = '/opt/app-root'
    yield
    del os.environ['APP_ROOT']

@pytest.fixture(scope='function')
def env_qradar_app_id():
    os.environ['QRADAR_APP_ID'] = '1005'
    yield
    del os.environ['QRADAR_APP_ID']

@pytest.fixture(scope='function')
def env_qradar_app_id_string():
    os.environ['QRADAR_APP_ID'] = 'qradar_app_id'
    yield
    del os.environ['QRADAR_APP_ID']

# ==== get_app_id ====

def test_get_app_id_returns_value_from_env(env_qradar_app_id):
    assert qpylib.get_app_id() == 1005

def test_get_app_id_returns_zero_when_field_missing_from_env():
    assert qpylib.get_app_id() == 0

def test_get_app_id_raises_error_when_env_field_contains_string(env_qradar_app_id_string):
    with pytest.raises(ValueError, match='Environment variable QRADAR_APP_ID has non-numeric value qradar_app_id'):
        qpylib.get_app_id()

# ==== get_app_name ====

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_get_app_name_returns_value_from_manifest(mock_manifest):
    assert qpylib.get_app_name() == 'Live Manifest'

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('missing_name.json'))
def test_get_app_name_raises_error_when_field_missing_from_manifest(mock_manifest):
    with pytest.raises(KeyError, match='name is a required manifest field'):
        qpylib.get_app_name()

# ==== get_manifest_json ====

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_get_manifest_json_no_cache(mock_manifest):
    manifest_json = qpylib.get_manifest_json()
    assert manifest_json['name'] == 'Live Manifest'
    assert manifest_json['description'] == 'A sample live manifest'
    assert manifest_json['version'] == '1.0'
    assert manifest_json['uuid'] == 'aaff161f-871a-435c-866b-c65b4ceca959'
    assert manifest_json['console_ip'] == '9.123.234.101'

# ==== get_manifest_field_value ====

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_get_manifest_field_value_returns_value_from_manifest(mock_manifest):
    assert qpylib.get_manifest_field_value('version') == '1.0'

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_get_manifest_field_value_returns_default_when_field_missing_from_manifest(mock_manifest):
    assert qpylib.get_manifest_field_value('banana', 'abcd') == 'abcd'

# ==== get_root_path ====

def test_get_root_path_with_env_var_missing():
    with pytest.raises(KeyError, match='Environment variable APP_ROOT is not set'):
        qpylib.get_root_path()

def test_get_root_path_with_no_relative_path(env_app_root):
    assert qpylib.get_root_path() == '/opt/app-root'

def test_get_root_path_with_relative_path(env_app_root):
    assert qpylib.get_root_path('my', 'other', 'directory') == '/opt/app-root/my/other/directory'

# ==== get_store_path ====

def test_get_store_path_with_no_relative_path(env_app_root):
    assert qpylib.get_store_path() == '/opt/app-root/store'

def test_get_store_path_with_relative_path(env_app_root):
    assert qpylib.get_store_path('my', 'other', 'directory') == '/opt/app-root/store/my/other/directory'

# ==== get_log_path ====

def test_get_log_path_with_no_relative_path(env_app_root):
    assert app_qpylib.get_log_path() == '/opt/app-root/store/log'

def test_get_log_path_with_relative_path(env_app_root):
    assert app_qpylib.get_log_path('my', 'logfile') == '/opt/app-root/store/log/my/logfile'

# ==== get_app_base_url ====

def test_get_app_base_url_returns_empty_string_when_app_id_missing_from_env():
    assert qpylib.get_app_base_url() == ''

def test_get_app_base_url_returns_empty_string_when_host_cannot_be_determined(env_qradar_app_id):
    assert qpylib.get_app_base_url() == ''

def test_get_app_base_url_uses_console_ip_when_x_console_host_header_missing(env_qradar_console_ip,
                                                                             env_qradar_app_id):
    assert qpylib.get_app_base_url() == 'https://9.123.234.101/console/plugins/1005/app_proxy'

@patch('qpylib.app_qpylib._get_host_header', return_value='9.10.11.12')
def test_get_app_base_url_uses_x_console_host_header_if_present(mock_get_host_header,
                                                                env_qradar_console_ip,
                                                                env_qradar_app_id):
    assert qpylib.get_app_base_url() == 'https://9.10.11.12/console/plugins/1005/app_proxy'

# ==== q_url_for, get_endpoint_url ====

@patch('qpylib.app_qpylib.get_endpoint_url', return_value='/index')
def test_q_url_for(mock_flask_url_for, env_qradar_console_ip, env_qradar_app_id):
    assert qpylib.q_url_for('index') == 'https://9.123.234.101/console/plugins/1005/app_proxy/index'

def test_get_endpoint_url():
    with pytest.raises(RuntimeError, match='Attempted to generate a URL without the application context'):
        app_qpylib.get_endpoint_url('dummyurl')

# ==== get_console_address ====

def test_get_console_address_with_env_var_set(env_qradar_console_ip):
    assert qpylib.get_console_address() == '9.123.234.101'

def test_get_console_address_with_env_var_missing():
    with pytest.raises(KeyError, match='Environment variable QRADAR_CONSOLE_IP is not set'):
        qpylib.get_console_address()

# ==== get_console_fqdn ====

@pytest.fixture(scope='function')
def env_qradar_console_fqdn():
    os.environ['QRADAR_CONSOLE_FQDN'] = 'myhost.ibm.com'
    yield
    del os.environ['QRADAR_CONSOLE_FQDN']

def test_get_console_fqdn_with_env_var_set(env_qradar_console_fqdn):
    assert qpylib.get_console_fqdn() == 'myhost.ibm.com'

def test_get_console_fqdn_with_env_var_missing():
    with pytest.raises(KeyError, match='Environment variable QRADAR_CONSOLE_FQDN is not set'):
        qpylib.get_console_fqdn()
