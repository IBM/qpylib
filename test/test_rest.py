# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=redefined-outer-name, unused-argument, invalid-name

import os
from unittest.mock import patch
from flask import Flask
import pytest
import responses
from werkzeug import http
from qpylib import qpylib

@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup():
    with patch('qpylib.app_qpylib.get_root_path') as mock_manifest:
        mock_manifest.return_value = os.path.join(os.path.dirname(__file__), 'manifests', 'installed.json')
        yield

@pytest.fixture()
def env_sec_admin_token():
    os.environ['SEC_ADMIN_TOKEN'] = '12345-testing-12345-testing'
    yield
    del os.environ['SEC_ADMIN_TOKEN']

@pytest.fixture()
def env_qradar_console_fqdn():
    os.environ['QRADAR_CONSOLE_FQDN'] = 'myhost.ibm.com'
    yield
    del os.environ['QRADAR_CONSOLE_FQDN']

@pytest.fixture()
def env_qradar_rest_proxy():
    os.environ['QRADAR_REST_PROXY'] = 'socks5h://localhost:1080'
    yield
    del os.environ['QRADAR_REST_PROXY']

@responses.activate
def test_rest_uses_env_vars_when_set(env_sec_admin_token, env_qradar_console_fqdn, env_qradar_rest_proxy):
    responses.add('GET', 'https://myhost.ibm.com/testing_endpoint', status=200)
    response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert', headers={'Host': '127.0.0.1'})
    assert response.status_code == 200
    assert responses.calls[0].request.method == 'GET'
    assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'
    assert responses.calls[0].request.headers['SEC'] == '12345-testing-12345-testing'

@responses.activate
def test_rest_uses_sec_cookie_when_env_var_not_set(env_qradar_console_fqdn):
    test_sec_cookie_value = 'seccookie-12345-seccookie'
    cookie = http.dump_cookie("SEC", test_sec_cookie_value)
    app = Flask(__name__)
    with app.test_request_context(headers={"COOKIE": cookie}):
        responses.add('GET', 'https://myhost.ibm.com/testing_endpoint', status=200)
        response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert', headers={'Host': '127.0.0.1'})
        assert response.status_code == 200
        assert responses.calls[0].request.method == 'GET'
        assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'
        assert responses.calls[0].request.headers['SEC'] == test_sec_cookie_value

@responses.activate
def test_rest_uses_csrf_cookie_when_set(env_qradar_console_fqdn):
    test_csrf_cookie_value = '1234567890abcdef'
    cookie = http.dump_cookie("QRadarCSRF", test_csrf_cookie_value)
    app = Flask(__name__)
    with app.test_request_context(headers={"COOKIE": cookie}):
        responses.add('GET', 'https://myhost.ibm.com/testing_endpoint', status=200)
        response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert', headers={'Host': '127.0.0.1'})
        assert response.status_code == 200
        assert responses.calls[0].request.method == 'GET'
        assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'
        assert responses.calls[0].request.headers['QRadarCSRF'] == test_csrf_cookie_value

@responses.activate
def test_rest_fails_when_fqdn_env_var_not_set():
    with pytest.raises(KeyError, match='Environment variable QRADAR_CONSOLE_FQDN is not set'):
        qpylib.REST('GET', 'testing_endpoint', verify='dummycert', headers={'Host': '127.0.0.1'})

@responses.activate
def test_rest_sets_version_header(env_qradar_console_fqdn):
    responses.add('GET', 'https://myhost.ibm.com/testing_endpoint', status=200)
    response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert', version='12', headers={'Host': '127.0.0.1'})
    assert response.status_code == 200
    assert responses.calls[0].request.method == 'GET'
    assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'
    assert responses.calls[0].request.headers['Version'] == '12'

@responses.activate
def test_rest_allows_post(env_qradar_console_fqdn):
    responses.add('POST', 'https://myhost.ibm.com/testing_endpoint', status=201)
    response = qpylib.REST('POST', 'testing_endpoint', verify='dummycert', headers={'Host': '127.0.0.1'})
    assert response.status_code == 201
    assert responses.calls[0].request.method == 'POST'
    assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'

@responses.activate
def test_rest_allows_put(env_qradar_console_fqdn):
    responses.add('PUT', 'https://myhost.ibm.com/testing_endpoint', status=201)
    response = qpylib.REST('PUT', 'testing_endpoint', verify='dummycert', headers={'Host': '127.0.0.1'})
    assert response.status_code == 201
    assert responses.calls[0].request.method == 'PUT'
    assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'

@responses.activate
def test_rest_allows_delete(env_qradar_console_fqdn):
    responses.add('DELETE', 'https://myhost.ibm.com/testing_endpoint', status=204)
    response = qpylib.REST('DELETE', 'testing_endpoint', verify='dummycert', headers={'Host': '127.0.0.1'})
    assert response.status_code == 204
    assert responses.calls[0].request.method == 'DELETE'
    assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'

def test_rest_rejects_unsupported_method(env_qradar_console_fqdn):
    with pytest.raises(ValueError, match='Unsupported REST action was requested'):
        qpylib.REST('PATCH', 'testing_endpoint', verify='dummycert', headers={'Host': '127.0.0.1'})
