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

class TestSdkRest:

    @responses.activate
    @patch('qpylib.sdk_qpylib.SdkQpylib.get_console_address', return_value = '9.101.234.169')
    @patch('qpylib.sdk_qpylib.SdkQpylib.get_api_auth', return_value = ('testuser', 'testing123'))
    def test_rest_uses_input_values(self, mock_api_auth, mock_console_address):
        with responses.RequestsMock() as responses_mock:
            responses_mock.add('GET', 'https://9.101.234.169/testing_endpoint',
                               json={'success': True}, status=200)

            response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert')
            assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'
            assert 'Basic' in responses_mock.calls[0].request.headers['Authorization']
            assert response.status_code == 200
