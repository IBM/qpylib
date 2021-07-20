# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=redefined-outer-name, unused-argument

import os
import pytest
from qpylib import util_qpylib

@pytest.fixture(scope='function')
def set_env_vars():
    os.environ['QRADAR_APPFW_SDK'] = 'true'
    yield
    del os.environ['QRADAR_APPFW_SDK']

def test_is_sdk_with_env_not_set():
    assert not util_qpylib.is_sdk()

def test_is_sdk_with_env_set(set_env_vars):
    assert util_qpylib.is_sdk()
