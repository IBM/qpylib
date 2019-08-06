# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=unused-argument

from unittest.mock import patch
import os
import pytest
from qpylib import qpylib
import responses

@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup():
    os.environ['QRADAR_APPFW_SDK'] = 'true'
    with patch('qpylib.abstract_qpylib.AbstractQpylib.log'):
        yield pre_testing_setup
        del os.environ['QRADAR_APPFW_SDK']

@responses.activate
@patch('qpylib.abstract_qpylib.AbstractQpylib.get_console_address', return_value = '9.101.234.169')
def test_rest_uses_input_values(mock_console_address):
    responses.add('GET', 'https://9.101.234.169/testing_endpoint',
                       json={'success': True}, status=200)

    response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert')
    assert responses.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'
    assert response.status_code == 200
