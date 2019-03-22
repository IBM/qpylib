# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import pytest
import json
import responses
from flask import Flask
from mock import patch
from werkzeug import http

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'qpylib')))

import qpylib
import live_qpylib
app = Flask(__name__)


# For testing purposes, override the logfile location and manifest as /store/log doesn't exist
# Also mock out get_manifest_json to return the test manifest in this directory as /app/manifest doesn't exist
@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup():
    live_qpylib.LOGFILE_LOCATION = 'testing.log'

    with patch('qpylib.LiveQpylib.get_manifest_json') as mocked_get_manifest_method:
        with open(os.path.join(os.path.dirname(__file__), 'test_manifest.json')) as test_manifest:
            mocked_get_manifest_method.return_value = json.load(test_manifest)
        with patch('live_qpylib.SysLogHandler') as mock_sys_log_handler:
            mock_sys_log_handler.return_value = mock_sys_log_handler.MockSysLogHandler()
            qpylib.create_log()
        yield


class TestREST:
    @pytest.fixture()
    def set_unset_sec_admin_token_env_var(self):
        os.environ['SEC_ADMIN_TOKEN'] = '12345-testing-12345-testing'
        yield
        del os.environ['SEC_ADMIN_TOKEN']

    @pytest.fixture()
    def set_unset_fqdn_env_var(self):
        os.environ['QRADAR_CONSOLE_FQDN'] = '9.101.234.169'
        yield
        del os.environ['QRADAR_CONSOLE_FQDN']

    @responses.activate
    def test_rest_get_sets_sec_token_to_sec_admin_token_if_present_in_env(self, set_unset_sec_admin_token_env_var,
                                                                          set_unset_fqdn_env_var):
        with responses.RequestsMock() as responses_mock:
            responses_mock.add(responses.GET, 'https://9.101.234.169/testing_endpoint',
                               json={'success': True}, status=200)
            response = qpylib.REST('GET', 'testing_endpoint')
            assert responses_mock.calls[0].request.headers['SEC'] == '12345-testing-12345-testing'
            assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'
            assert response.status_code == 200

    @responses.activate
    def test_rest_get_sets_sec_token_to_cookie_sec_if_no_sec_admin_token_env_var(self, set_unset_fqdn_env_var):
        test_sec_cookie_value = 'seccookie-12345-seccookie'
        cookie = http.dump_cookie("SEC", test_sec_cookie_value)
        with responses.RequestsMock() as responses_mock:
            with app.test_request_context(headers={"COOKIE": cookie}):
                responses_mock.add(responses.GET, 'https://9.101.234.169/testing_endpoint',
                                   json={'success': True}, status=200)
                response = qpylib.REST('GET', 'testing_endpoint')
                assert responses_mock.calls[0].request.headers['SEC'] == test_sec_cookie_value
                assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'
                assert response.status_code == 200

    @responses.activate
    def test_rest_get_uses_manifest_console_ip_if_no_fqdn_env_var(self):
        with responses.RequestsMock() as responses_mock:
            responses_mock.add(responses.GET, 'https://9.123.321.101/testing_endpoint',
                               json={'success': True}, status=200)
            response = qpylib.REST('GET', 'testing_endpoint')
            assert response.status_code == 200
            assert responses_mock.calls[0].request.url == 'https://9.123.321.101/testing_endpoint'
