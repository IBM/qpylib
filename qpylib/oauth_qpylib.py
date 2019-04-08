# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import os
import requests
import subprocess

Q_OAUTH_SERVICE_URL = 'http://qoauth.service.consul:{0}/token?grant_type=client_credentials&client_id={1}&client_secret={2}'

oauth_token = ''

def get_env_variable(variable_name):
    try:
        return str(os.environ[variable_name])
    except KeyError:
        return ''

def get_qoauth_port():
    p = subprocess.Popen(['/service_port_locator.py', 'qoauth.service.consul'], stdout=subprocess.PIPE)
    return str(p.communicate()[0]).strip()

def get_client_id():
    return get_env_variable('CLIENT_ID')

def get_client_secret():
    return get_env_variable('CLIENT_SECRET')

def request_oauth_token():
    url = Q_OAUTH_SERVICE_URL.format(get_qoauth_port(), get_client_id(), get_client_secret())
    response = requests.get(url, verify=False)
    return response.json()['access_token']

def get_oauth_token(renew_token=False):
    global oauth_token
    if renew_token or not oauth_token:
        oauth_token = request_oauth_token()
    return oauth_token

def add_oauth_header(headers, renew_token=False):
    headers['Authorization'] = 'Bearer ' + get_oauth_token(renew_token)
