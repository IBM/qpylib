# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=unused-argument

from flask import Flask
import json
from unittest.mock import patch
import os
import pytest
from qpylib import qpylib
import responses
from werkzeug import http

@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup():
    with open(os.path.join(os.path.dirname(__file__), 'test_manifest.json')) as test_manifest:
        manifest_json = json.load(test_manifest)
    with patch('qpylib.abstract_qpylib.AbstractQpylib.log'):
        with patch('qpylib.live_qpylib.LiveQpylib.get_manifest_json') as mocked_get_manifest_json:
            mocked_get_manifest_json.return_value = manifest_json
            yield

class TestLiveRest:
    
    @pytest.fixture()
    def env_sec_admin_token(self):
        os.environ['SEC_ADMIN_TOKEN'] = '12345-testing-12345-testing'
        yield
        del os.environ['SEC_ADMIN_TOKEN']
    
    @pytest.fixture()
    def env_qradar_console_fqdn(self):
        os.environ['QRADAR_CONSOLE_FQDN'] = '9.101.234.169'
        yield
        del os.environ['QRADAR_CONSOLE_FQDN']
    
    @responses.activate
    def test_rest_uses_env_vars_when_set(self, env_sec_admin_token, env_qradar_console_fqdn):
        with responses.RequestsMock() as responses_mock:
            responses_mock.add('GET', 'https://9.101.234.169/testing_endpoint',
                               json={'success': True}, status=200)
            response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert')
            assert responses_mock.calls[0].request.headers['SEC'] == '12345-testing-12345-testing'
            assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'
            assert response.status_code == 200
    
    @responses.activate
    def test_rest_uses_sec_cookie_when_env_var_not_set(self, env_qradar_console_fqdn):
        test_sec_cookie_value = 'seccookie-12345-seccookie'
        cookie = http.dump_cookie("SEC", test_sec_cookie_value)
        app = Flask(__name__)
        with responses.RequestsMock() as responses_mock:
            with app.test_request_context(headers={"COOKIE": cookie}):
                responses_mock.add('GET', 'https://9.101.234.169/testing_endpoint',
                                   json={'success': True}, status=200)
                response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert')
                assert responses_mock.calls[0].request.headers['SEC'] == test_sec_cookie_value
                assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'
                assert response.status_code == 200
    
    @responses.activate
    def test_rest_uses_manifest_console_ip_when_env_var_not_set(self):
        with responses.RequestsMock() as responses_mock:
            responses_mock.add('GET', 'https://9.123.321.101/testing_endpoint',
                               json={'success': True}, status=200)
            response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert')
            assert response.status_code == 200
            assert responses_mock.calls[0].request.url == 'https://9.123.321.101/testing_endpoint'
