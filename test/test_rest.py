# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=redefined-outer-name, unused-argument

from flask import Flask
from unittest.mock import patch
import os
import pytest
from qpylib import qpylib
import responses
from werkzeug import http

@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup():
    with patch('qpylib.abstract_qpylib.AbstractQpylib.log'):
        with patch('qpylib.live_qpylib.LiveQpylib._root_path') as mock_root_path:
            mock_root_path.return_value = os.path.dirname(__file__)
            with patch('qpylib.live_qpylib.LiveQpylib._get_manifest_location') as mock_get_manifest_location:
                mock_get_manifest_location.return_value = 'manifests/installed.json'
                yield

@pytest.fixture()
def env_sec_admin_token():
    os.environ['SEC_ADMIN_TOKEN'] = '12345-testing-12345-testing'
    yield
    del os.environ['SEC_ADMIN_TOKEN']

@pytest.fixture()
def env_qradar_console_fqdn():
    os.environ['QRADAR_CONSOLE_FQDN'] = '9.101.234.169'
    yield
    del os.environ['QRADAR_CONSOLE_FQDN']

@responses.activate
def test_rest_uses_env_vars_when_set(env_sec_admin_token, env_qradar_console_fqdn):
    with responses.RequestsMock() as responses_mock:
        responses_mock.add('GET', 'https://9.101.234.169/testing_endpoint', status=200)
        response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert')
        assert response.status_code == 200
        assert responses_mock.calls[0].request.method == 'GET'
        assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'
        assert responses_mock.calls[0].request.headers['SEC'] == '12345-testing-12345-testing'

@responses.activate
def test_rest_uses_sec_cookie_when_env_var_not_set(env_qradar_console_fqdn):
    test_sec_cookie_value = 'seccookie-12345-seccookie'
    cookie = http.dump_cookie("SEC", test_sec_cookie_value)
    app = Flask(__name__)
    with responses.RequestsMock() as responses_mock:
        with app.test_request_context(headers={"COOKIE": cookie}):
            responses_mock.add('GET', 'https://9.101.234.169/testing_endpoint', status=200)
            response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert')
            assert response.status_code == 200
            assert responses_mock.calls[0].request.method == 'GET'
            assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'
            assert responses_mock.calls[0].request.headers['SEC'] == test_sec_cookie_value

@responses.activate
def test_rest_uses_manifest_console_ip_when_env_var_not_set():
    with responses.RequestsMock() as responses_mock:
        responses_mock.add('GET', 'https://9.123.321.101/testing_endpoint', status=200)
        response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert')
        assert response.status_code == 200
        assert responses_mock.calls[0].request.method == 'GET'
        assert responses_mock.calls[0].request.url == 'https://9.123.321.101/testing_endpoint'

@responses.activate
def test_rest_sets_version_header(env_qradar_console_fqdn):
    with responses.RequestsMock() as responses_mock:
        responses_mock.add('GET', 'https://9.101.234.169/testing_endpoint', status=200)
        response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert', version='12')
        assert response.status_code == 200
        assert responses_mock.calls[0].request.method == 'GET'
        assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'
        assert responses_mock.calls[0].request.headers['Version'] == '12'

@responses.activate
def test_rest_allows_post(env_qradar_console_fqdn):
    with responses.RequestsMock() as responses_mock:
        responses_mock.add('POST', 'https://9.101.234.169/testing_endpoint', status=201)
        response = qpylib.REST('POST', 'testing_endpoint', verify='dummycert')
        assert response.status_code == 201
        assert responses_mock.calls[0].request.method == 'POST'
        assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'

@responses.activate
def test_rest_allows_put(env_qradar_console_fqdn):
    with responses.RequestsMock() as responses_mock:
        responses_mock.add('PUT', 'https://9.101.234.169/testing_endpoint', status=201)
        response = qpylib.REST('PUT', 'testing_endpoint', verify='dummycert')
        assert response.status_code == 201
        assert responses_mock.calls[0].request.method == 'PUT'
        assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'

@responses.activate
def test_rest_allows_delete(env_qradar_console_fqdn):
    with responses.RequestsMock() as responses_mock:
        responses_mock.add('DELETE', 'https://9.101.234.169/testing_endpoint', status=204)
        response = qpylib.REST('DELETE', 'testing_endpoint', verify='dummycert')
        assert response.status_code == 204
        assert responses_mock.calls[0].request.method == 'DELETE'
        assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'

def test_rest_rejects_unsupported_method(env_qradar_console_fqdn):
    with pytest.raises(ValueError, match='Unsupported REST action was requested'):
        qpylib.REST('PATCH', 'testing_endpoint', verify='dummycert')
