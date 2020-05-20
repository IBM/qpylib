# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=redefined-outer-name, unused-argument, invalid-name

import os
import pytest
import responses
from qpylib import qpylib

@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup():
    os.environ['QRADAR_APPFW_SDK'] = 'true'
    os.environ['SEC_ADMIN_TOKEN'] = '12345-testing-12345-testing'
    yield pre_testing_setup
    del os.environ['QRADAR_APPFW_SDK']
    del os.environ['SEC_ADMIN_TOKEN']

@pytest.fixture()
def env_qradar_console_fqdn():
    os.environ['QRADAR_CONSOLE_FQDN'] = 'myhost.ibm.com'
    yield
    del os.environ['QRADAR_CONSOLE_FQDN']

@responses.activate
def test_rest_uses_input_and_env_values(env_qradar_console_fqdn):
    responses.add('GET', 'https://myhost.ibm.com/testing_endpoint',
                  json={'success': True}, status=200)

    response = qpylib.REST('GET', 'testing_endpoint', version='12', headers={'Host': '127.0.0.1'})
    assert response.status_code == 200
    assert responses.calls[0].request.method == 'GET'
    assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'
    assert responses.calls[0].request.headers['Version'] == '12'
    assert responses.calls[0].request.headers['Host'] == '127.0.0.1'
    assert responses.calls[0].request.headers['SEC'] == '12345-testing-12345-testing'

@responses.activate
def test_rest_fails_when_fqdn_env_var_not_set():
    with pytest.raises(KeyError, match='Environment variable QRADAR_CONSOLE_FQDN is not set'):
        qpylib.REST('GET', 'testing_endpoint', headers={'Host': '127.0.0.1'})

@responses.activate
def test_rest_allows_post(env_qradar_console_fqdn):
    responses.add('POST', 'https://myhost.ibm.com/testing_endpoint', status=201)
    response = qpylib.REST('POST', 'testing_endpoint', headers={'Host': '127.0.0.1'})
    assert response.status_code == 201
    assert responses.calls[0].request.method == 'POST'
    assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'

@responses.activate
def test_rest_allows_put(env_qradar_console_fqdn):
    responses.add('PUT', 'https://myhost.ibm.com/testing_endpoint', status=201)
    response = qpylib.REST('PUT', 'testing_endpoint', headers={'Host': '127.0.0.1'})
    assert response.status_code == 201
    assert responses.calls[0].request.method == 'PUT'
    assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'

@responses.activate
def test_rest_allows_delete(env_qradar_console_fqdn):
    responses.add('DELETE', 'https://myhost.ibm.com/testing_endpoint', status=204)
    response = qpylib.REST('DELETE', 'testing_endpoint', headers={'Host': '127.0.0.1'})
    assert response.status_code == 204
    assert responses.calls[0].request.method == 'DELETE'
    assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'

def test_rest_rejects_unsupported_method(env_qradar_console_fqdn):
    with pytest.raises(ValueError, match='Unsupported REST action was requested'):
        qpylib.REST('PATCH', 'testing_endpoint', headers={'Host': '127.0.0.1'})
