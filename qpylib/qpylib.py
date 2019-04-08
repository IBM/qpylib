# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import os
from .live_qpylib import LiveQpylib
from .sdk_qpylib import SdkQpylib

# ===== SDK specifics =====

def is_sdk():
    sdk_env = os.getenv('QRADAR_APPFW_SDK', 'no').lower() == 'true'
    return sdk_env

def strategy():
    if is_sdk():
        return SdkQpylib()
    return LiveQpylib()

# ===== User Utils qpylib =====

def log(message, level='info'):
    strategy().log(message, level)

def create_log():
    strategy().create_log()

def set_log_level(log_level='info'):
    strategy().set_log_level(log_level)

def get_store_path(relative_path=""):
    return strategy().get_store_path(relative_path)

def get_root_path(relative_path=""):
    return strategy().get_root_path(relative_path)

def REST(RESTtype, requestURL, headers=None, data=None, params=None,
         json=None, version=None, verify=None, timeout=60):
    return strategy().REST(RESTtype, requestURL, headers, data=data,
                           params=params, json_inst=json,
                           version=version, verify=verify,
                           timeout=timeout)

def get_app_base_url():
    return strategy().get_app_base_url()

def q_url_for(endpoint, **values):
    return strategy().q_url_for(endpoint, **values)

def to_json_dict(python_obj):
    return strategy().to_json_dict(python_obj)

def get_console_address():
    return strategy().get_console_address()

def get_app_id():
    return strategy().get_app_id()

def get_app_name():
    return strategy().get_app_name()

def register_jsonld_type(context):
    return strategy().register_jsonld_type(context)

def get_cert_filepath(host):
    return strategy().get_cert_filepath(host)

# ==== Rendering Utils ====

def get_offense_rendering(offense_id, render_type):
    return strategy().get_offense_rendering(offense_id, render_type)

def get_asset_rendering(asset_id, render_type):
    return strategy().get_asset_rendering(asset_id, render_type)

def render_json_ld_type(jld_type, data, jld_id = None):
    return strategy().render_json_ld_type(jld_type, data, jld_id)

def register_jsonld_endpoints():
    return strategy().register_jsonld_endpoints()
