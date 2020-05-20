# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=unused-argument, redefined-outer-name, invalid-name

from unittest.mock import patch
import os
import pytest
from qpylib import qpylib

GET_MANIFEST_JSON = 'qpylib.app_qpylib.get_root_path'

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

# ==== get_app_id ====

@patch(GET_MANIFEST_JSON, return_value=manifest_path('installed.json'))
def test_get_app_id_returns_value_from_manifest(mock_manifest):
    assert qpylib.get_app_id() == 1005

@patch(GET_MANIFEST_JSON, return_value=manifest_path('pre_install.json'))
def test_get_app_id_returns_zero_when_field_missing_from_manifest(mock_manifest):
    assert qpylib.get_app_id() == 0

# ==== get_app_name ====

@patch(GET_MANIFEST_JSON, return_value=manifest_path('installed.json'))
def test_get_app_name_returns_value_from_manifest(mock_manifest):
    assert qpylib.get_app_name() == 'Live Manifest'

@patch(GET_MANIFEST_JSON, return_value=manifest_path('missing_name.json'))
def test_get_app_name_raises_error_when_field_missing_from_manifest(mock_manifest):
    with pytest.raises(KeyError, match='name is a required manifest field'):
        qpylib.get_app_name()

# ==== get_manifest_json ====

@patch(GET_MANIFEST_JSON, return_value=manifest_path('installed.json'))
def test_get_manifest_json_no_cache(mock_manifest):
    manifest_json = qpylib.get_manifest_json()
    assert manifest_json['name'] == 'Live Manifest'
    assert manifest_json['description'] == 'A sample live manifest'
    assert manifest_json['version'] == '1.0'
    assert manifest_json['uuid'] == 'aaff161f-871a-435c-866b-c65b4ceca959'
    assert manifest_json['app_id'] == 1005
    assert manifest_json['console_ip'] == '9.123.234.101'

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

# ==== get_app_base_url ====

@patch(GET_MANIFEST_JSON, return_value=manifest_path('pre_install.json'))
def test_get_app_base_url_returns_empty_string_when_app_id_missing_from_manifest(mock_manifest):
    assert qpylib.get_app_base_url() == ''

@patch(GET_MANIFEST_JSON, return_value=manifest_path('installed_no_console_ip.json'))
def test_get_app_base_url_returns_empty_string_when_host_cannot_be_determined(mock_manifest):
    assert qpylib.get_app_base_url() == ''

@patch(GET_MANIFEST_JSON, return_value=manifest_path('installed_no_console_ip.json'))
def test_get_app_base_url_uses_console_ip_when_x_console_host_header_missing(mock_manifest,
                                                                             env_qradar_console_ip):
    assert qpylib.get_app_base_url() == 'https://9.123.234.101/console/plugins/1007/app_proxy'

@patch(GET_MANIFEST_JSON, return_value=manifest_path('installed_no_console_ip.json'))
@patch('qpylib.app_qpylib._get_host_header', return_value='9.10.11.12')
def test_get_app_base_url_uses_x_console_host_header_if_present(mock_get_host_header, mock_manifest,
                                                                env_qradar_console_ip):
    assert qpylib.get_app_base_url() == 'https://9.10.11.12/console/plugins/1007/app_proxy'

# ==== q_url_for ====

@patch(GET_MANIFEST_JSON, return_value=manifest_path('installed.json'))
@patch('qpylib.app_qpylib.get_endpoint_url', return_value='/index')
def test_q_url_for(mock_flask_url_for, mock_manifest, env_qradar_console_ip):
    assert qpylib.q_url_for('index') == 'https://9.123.234.101/console/plugins/1005/app_proxy/index'

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
