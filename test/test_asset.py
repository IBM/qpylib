# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=unused-argument, redefined-outer-name, duplicate-code

import os
import pytest
from qpylib import qpylib, asset_qpylib

@pytest.fixture()
def env_qradar_console_fqdn():
    os.environ['QRADAR_CONSOLE_FQDN'] = 'myhost.ibm.com'
    yield
    del os.environ['QRADAR_CONSOLE_FQDN']

def test_get_asset_url():
    assert asset_qpylib.get_asset_url(1234) == 'api/asset_model/assets/1234'

def test_get_asset_url_full(env_qradar_console_fqdn):
    assert asset_qpylib.get_asset_url_full(1234) == 'https://myhost.ibm.com/api/asset_model/assets/1234'

def test_get_asset_json():
    assert asset_qpylib.get_asset_json(1234)['id'] == 1234

def test_get_asset_rendering_html():
    assert qpylib.get_asset_rendering(1234, 'HTML') == \
        '{"html": "<table><tbody><tr><td>Asset ID</td><td>1234</td></tr></tbody></table>"}'

def generate_custom_html(asset_json):
    return '<p>' + str(asset_json['id']) + '</p>'

def test_get_asset_json_html_custom():
    assert asset_qpylib.get_asset_json_html(1234, generate_html=generate_custom_html) == \
        '{"html": "<p>1234</p>"}'

def test_get_asset_rendering_jsonld(env_qradar_console_fqdn):
    assert qpylib.get_asset_rendering(1234, 'JSONLD') == \
        ('{"@context": "https://qradar/context/location", '
         '"@id": "https://myhost.ibm.com/api/asset_model/assets/1234", '
         '"@type": "asset", '
         '"data": {"id": 1234}, '
         '"description": "Asset details for id 1234", '
         '"name": "Asset details"}')
