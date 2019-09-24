# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import os

def is_sdk():
    return os.getenv('QRADAR_APPFW_SDK', 'no').lower() == 'true'

def is_ipv6_address(ip_address):
    return ip_address.startswith('[') and ip_address.endswith(']')
