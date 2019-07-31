# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=unused-argument

from unittest.mock import patch
import os
import pytest
from qpylib import qpylib

GET_MANIFEST_LOCATION = 'qpylib.abstract_qpylib.AbstractQpylib._get_manifest_location'
APP_ROOT_PATH = 'qpylib.abstract_qpylib.AbstractQpylib._root_path'
GET_HOST_HEADER = 'qpylib.live_qpylib.LiveQpylib._get_host_header'
GET_ENDPOINT_URL = 'qpylib.abstract_qpylib.AbstractQpylib._get_endpoint_url'
QTEST_DIR = os.path.dirname(__file__)

@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup():
    with patch('qpylib.abstract_qpylib.AbstractQpylib.log'):
        yield

@pytest.fixture(scope='function', autouse=True)
def clear_manifest_cache():
    with patch('qpylib.abstract_qpylib.cached_manifest', None):
        yield

# ==== get_app_id ====

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/installed.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
def test_get_app_id_returns_value_from_manifest(mock_root_path, mock_get_manifest_location):
    assert qpylib.get_app_id() == 1005

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/pre_install.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
def test_get_app_id_returns_zero_when_field_missing_from_manifest(mock_root_path, mock_get_manifest_location):
    assert qpylib.get_app_id() == 0

# ==== get_app_name ====

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/installed.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
def test_get_app_name_returns_value_from_manifest(mock_root_path, mock_get_manifest_location):
    assert qpylib.get_app_name() == 'Live Manifest'

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/missing_name.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
def test_get_app_name_raises_error_when_field_missing_from_manifest(mock_root_path, mock_get_manifest_location):
    with pytest.raises(KeyError, match='name is a required manifest field'):
        qpylib.get_app_name()

# ==== get_manifest_json ====

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/installed.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
def test_get_manifest_json_no_cache(mock_root_path, mock_get_manifest_location):
    manifest_json = qpylib.get_manifest_json()
    assert manifest_json['name'] == 'Live Manifest'
    assert manifest_json['description'] == 'A sample live manifest'
    assert manifest_json['version'] == '1.0'
    assert manifest_json['uuid'] == 'aaff161f-871a-435c-866b-c65b4ceca959'
    assert manifest_json['app_id'] == 1005
    assert manifest_json['console_ip'] == '9.123.234.101'

# ==== get_store_path ====

def test_get_store_path_with_no_relative_path_returns_slash_store():
    assert qpylib.get_store_path() == '/store'

def test_get_store_path_with_relative_path_appends_relative_path():
    assert qpylib.get_store_path('my/other/directory') == '/store/my/other/directory'

# ==== get_root_path ====

def test_get_root_path_with_no_relative_path_returns_slash():
    assert qpylib.get_root_path() == '/'

def test_get_root_path_with_relative_path_appends_relative_path():
    assert qpylib.get_root_path('my/other/directory') == '/my/other/directory'

# ==== get_app_base_url ====

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/pre_install.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
def test_get_app_base_url_returns_empty_string_when_app_id_missing_from_manifest(mock_root_path, mock_get_manifest_location):
    assert qpylib.get_app_base_url() == ''

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/installed_no_console_ip.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
def test_get_app_base_url_returns_empty_string_when_console_ip_missing_from_manifest(mock_root_path, mock_get_manifest_location):
    assert qpylib.get_app_base_url() == ''

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/installed.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
def test_get_app_base_url_uses_console_ip_when_x_console_host_header_missing(mock_root_path, mock_get_manifest_location):
    assert qpylib.get_app_base_url() == 'https://9.123.234.101/console/plugins/1005/app_proxy'

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/installed.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
@patch(GET_HOST_HEADER, return_value = '9.10.11.12')
def test_get_app_base_url_uses_x_console_host_header_if_present(mock_get_host_header, mock_root_path, mock_get_manifest_location):
    assert qpylib.get_app_base_url() == 'https://9.10.11.12/console/plugins/1005/app_proxy'

# ==== q_url_for ====

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/installed.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
@patch(GET_ENDPOINT_URL, return_value = '/index')
def test_q_url_for(mock_flask_url_for, mock_root_path, mock_get_manifest_location):
    assert qpylib.q_url_for('index') == 'https://9.123.234.101/console/plugins/1005/app_proxy/index'

# ==== get_console_address ====

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/installed.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
def test_get_console_address_returns_value_from_manifest(mock_root_path, mock_get_manifest_location):
    assert qpylib.get_console_address() == "9.123.234.101"

@patch(GET_MANIFEST_LOCATION, return_value = 'manifests/installed_no_console_ip.json')
@patch(APP_ROOT_PATH, return_value = QTEST_DIR)
def test_get_console_address_returns_default_when_field_missing_from_manifest(mock_root_path, mock_get_manifest_location):
    assert qpylib.get_console_address() == '127.0.0.1'
    
