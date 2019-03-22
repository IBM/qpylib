# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import pytest
import responses

from mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'qpylib')))

import qpylib


def delete_sdk_env_var():
    del os.environ['QRADAR_APPFW_SDK']


# Set the env var indicating this is the sdk for duration of tests
@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup(request):
    os.environ['QRADAR_APPFW_SDK'] = 'true'
    with patch('live_qpylib.SysLogHandler') as mock_sys_log_handler:
        mock_sys_log_handler.return_value = mock_sys_log_handler.MockSysLogHandler()
        qpylib.create_log()
    request.addfinalizer(delete_sdk_env_var)


class TestREST:

    @responses.activate
    def test_rest_get_sets_auth_and_console_ip_from_user_input_with_no_config_files(self):
        username = 'test_user'
        password = 'test_pass'

        with responses.RequestsMock() as responses_mock:
            # Need to mock both raw_input and getpass to simulate the user entering details via command line
            with patch('__builtin__.raw_input') as mocked_raw_input:
                with patch('getpass.getpass') as mocked_get_pass:
                    mocked_raw_input.side_effect = ['9.101.234.169', 'n', username, password, 'n']
                    mocked_get_pass.side_effect = ['testing123']

                    responses_mock.add(responses.GET, 'https://9.101.234.169/testing_endpoint',
                                       json={'success': True}, status=200)
                    response = qpylib.REST('GET', 'testing_endpoint', verify='dummycert')
                    assert responses_mock.calls[0].request.url == 'https://9.101.234.169/testing_endpoint'
                    assert 'Basic' in responses_mock.calls[0].request.headers['Authorization']
                    assert response.status_code == 200
