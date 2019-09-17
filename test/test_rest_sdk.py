# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import os
import pytest
from qpylib import qpylib
import responses

@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup():
    os.environ['QRADAR_APPFW_SDK'] = 'true'
    os.environ['QRADAR_CONSOLE_FQDN'] = 'myhost.ibm.com'
    yield pre_testing_setup
    del os.environ['QRADAR_APPFW_SDK']
    del os.environ['QRADAR_CONSOLE_FQDN']

@responses.activate
def test_rest_uses_input_values():
    responses.add('GET', 'https://myhost.ibm.com/testing_endpoint',
                  json={'success': True}, status=200)

    response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert')
    assert responses.calls[0].request.url == 'https://myhost.ibm.com/testing_endpoint'
    assert response.status_code == 200
