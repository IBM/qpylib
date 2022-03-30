# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=unused-argument, redefined-outer-name, duplicate-code

import json
import os
from unittest.mock import patch
import pytest
import responses
from qpylib import qpylib, offense_qpylib

@pytest.fixture()
def env_qradar_console_fqdn():
    os.environ['QRADAR_CONSOLE_FQDN'] = 'myhost.ibm.com'
    yield
    del os.environ['QRADAR_CONSOLE_FQDN']

def mock_offense_response(offense_id):
    responses.add(responses.GET, 'https://myhost.ibm.com/api/siem/offenses/' + str(offense_id),
                  content_type='application/json', status=200,
                  json={'id': 1234, 'offense_source': '9.10.11.12', 'severity': 2})

def test_get_offense_url():
    assert offense_qpylib.get_offense_url(1234) == 'api/siem/offenses/1234'

def test_get_offense_url_full(env_qradar_console_fqdn):
    assert offense_qpylib.get_offense_url_full(1234) == 'https://myhost.ibm.com/api/siem/offenses/1234'

@responses.activate
def test_get_offense_json_rest_failure(env_qradar_console_fqdn):
    responses.add(responses.GET, 'https://myhost.ibm.com/api/siem/offenses/1234', status=500)
    with pytest.raises(ValueError, match='Could not retrieve offense with id 1234'):
        offense_qpylib.get_offense_json(1234)

@responses.activate
def test_get_offense_json(env_qradar_console_fqdn):
    mock_offense_response(1234)
    offense_json = offense_qpylib.get_offense_json(1234)
    assert offense_json['id'] == 1234
    assert offense_json['offense_source'] == '9.10.11.12'
    assert offense_json['severity'] == 2

@responses.activate
@patch('qpylib.app_qpylib.get_app_name', return_value='myapp')
def test_get_offense_rendering_html(mock_get_app_name, env_qradar_console_fqdn):
    mock_offense_response(1234)
    heading_html = offense_qpylib.OFFENSE_HEADER_TEMPLATE.format(1234, 'myapp')
    table_html = ('<table><tbody>' +
                  offense_qpylib.OFFENSE_ROW_TEMPLATE.format('Offense ID', 1234) +
                  offense_qpylib.OFFENSE_ROW_TEMPLATE.format('Source IP', '9.10.11.12') +
                  offense_qpylib.OFFENSE_ROW_TEMPLATE.format('Severity', 2) +
                  '</tbody></table>')
    html = heading_html + table_html + '<br/>'
    assert qpylib.get_offense_rendering(1234, 'HTML') == json.dumps({'html': html})

def generate_custom_html(offense_json):
    return '<p>' + str(offense_json['id']) + '</p>'

@responses.activate
@patch('qpylib.app_qpylib.get_app_name', return_value='myapp')
def test_get_offense_json_html_custom(mock_get_app_name, env_qradar_console_fqdn):
    mock_offense_response(1234)
    rendering = offense_qpylib.get_offense_json_html(1234, generate_html=generate_custom_html,
                                                     generate_heading=False)
    assert rendering == json.dumps({'html': '<p>1234</p><br/>'})

@responses.activate
def test_get_offense_rendering_jsonld(env_qradar_console_fqdn):
    mock_offense_response(1234)
    assert qpylib.get_offense_rendering(1234, 'JSONLD') == \
        ('{"@context": "https://qradar/context/location", '
         '"@id": "https://myhost.ibm.com/api/siem/offenses/1234", '
         '"@type": "offense", '
         '"data": {"id": 1234, "offense_source": "9.10.11.12", "severity": 2}, '
         '"description": "Offense details for id 1234", '
         '"name": "Offense details"}')
