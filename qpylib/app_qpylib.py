# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
from flask import request, url_for

Q_CACHED_MANIFEST = None

def get_app_id():
    app_id = os.getenv('QRADAR_APP_ID', '0')
    try:
        return int(app_id)
    except ValueError:
        raise ValueError('Environment variable QRADAR_APP_ID has non-numeric value {0}'.format(app_id))

def get_app_name():
    return get_manifest_field_value('name')

def get_manifest_json():
    global Q_CACHED_MANIFEST
    if Q_CACHED_MANIFEST is None:
        full_manifest_location = get_root_path('manifest.json')
        with open(full_manifest_location) as manifest_file:
            Q_CACHED_MANIFEST = json.load(manifest_file)
    return Q_CACHED_MANIFEST

def get_manifest_field_value(key, default_value=None):
    manifest = get_manifest_json()
    if key in manifest.keys():
        return manifest[key]
    if default_value is not None:
        return default_value
    raise KeyError('{0} is a required manifest field'.format(key))

def get_root_path(*path_entries):
    return _build_path(*path_entries)

def get_store_path(*path_entries):
    return _build_path('store', *path_entries)

def get_log_path(*path_entries):
    return _build_path('store', 'log', *path_entries)

def _build_path(*path_entries):
    return os.path.join(get_env_var('APP_ROOT'), *path_entries)

def get_endpoint_url(endpoint, **values):
    return url_for(endpoint, **values)

def get_console_ip():
    return get_env_var('QRADAR_CONSOLE_IP')

def get_console_fqdn():
    return get_env_var('QRADAR_CONSOLE_FQDN')

def get_env_var(key):
    value = os.getenv(key)
    if value is None:
        raise KeyError('Environment variable {0} is not set'.format(key))
    return value

def get_app_base_url():
    """
    Gets the full url that will proxy an app request to its plugin servlet.
    If any of the information required for building the proxy is missing
    then an empty string is returned.
    """
    app_id = get_app_id()
    if app_id == 0:
        return ''

    host = _get_host()
    if host is None:
        return ''

    return "https://{0}/console/plugins/{1}/app_proxy".format(host, app_id)

def _get_host():
    try:
        host = _get_host_header()
    except: # pylint: disable=W0702
        host = None

    if host is None:
        try:
            host = get_console_ip()
        except KeyError:
            return None

    return host

def _get_host_header():
    return request.headers.get('X-Console-Host')
