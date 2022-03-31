# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from . import app_qpylib
from . import asset_qpylib
from . import json_qpylib
from . import log_qpylib
from . import offense_qpylib
from . import rest_qpylib
# This is needed to allow accessing util_qpylib from the parent qpylib module
from . import util_qpylib # pylint: disable=unused-import

# ==== Logging ====

def create_log(syslog_enabled=True):
    ''' Initialises logging.
        Threshold log level is set to the value of the "log_level" field
        in the app manifest.json, or INFO if that field is absent.
        Creates a file log handler which directs logs to store/log/app.log.
        Creates a Syslog handler, but only if syslog_enabled is True and
        environment variables QRADAR_CONSOLE_IP and QRADAR_APP_UUID are
        both set.
        Must be called before any call to log() or set_log_level().
        Raises ValueError if the manifest threshold log level is invalid.
    '''
    log_qpylib.create_log(syslog_enabled)

def log(message, level='INFO'):
    ''' Logs a message at the given level, which defaults to INFO.
        Level values: DEBUG, INFO, WARNING, ERROR, EXCEPTION, CRITICAL.
        EXCEPTION is ERROR plus extra exception details.
        Raises RuntimeError if logging was not previously initialised
        by a call to qpylib.create_log().
        Raises ValueError if level is invalid.
    '''
    log_qpylib.log(message, level)

def set_log_level(level):
    ''' Sets the threshold log level.
        Level values: DEBUG, INFO, WARNING, ERROR, CRITICAL.
        Raises RuntimeError if logging was not previously initialised
        by a call to qpylib.create_log().
        Raises ValueError if level is invalid.
    '''
    log_qpylib.set_log_level(level)

# ==== App details ====

def get_app_id():
    ''' Returns the QRADAR_APP_ID value from the app container environment,
        or 0 if QRADAR_APP_ID is not set.
    '''
    return app_qpylib.get_app_id()

def get_app_name():
    ''' Returns the "name" value from the app manifest.
        Raises KeyError if "name" is not in the manifest.
    '''
    return app_qpylib.get_app_name()

def get_manifest_json():
    ''' Returns the content of the app manifest as a Python object. '''
    return app_qpylib.get_manifest_json()

def get_manifest_field_value(key, default_value=None):
    ''' Returns the value of "key" from the app manifest.
        If "key" is not in the manifest and default_value
        was supplied, default_value is returned.
        Raises KeyError if "key" is not in the manifest and
        no default_value was supplied.
    '''
    return app_qpylib.get_manifest_field_value(key, default_value)

def get_root_path(*path_entries):
    ''' Returns the app's root path, joined with path_entries if supplied.
        The app's root path is the location of the app directory and
        manifest.json file.
        Raises KeyError if environment variable APP_ROOT is not set.
    '''
    return app_qpylib.get_root_path(*path_entries)

def get_store_path(*path_entries):
    ''' Returns the app's store path, joined with path_entries if supplied.
        Raises KeyError if environment variable APP_ROOT is not set.
    '''
    return app_qpylib.get_store_path(*path_entries)

def get_app_base_url():
    """ Returns the QRadar app proxy prefix. """
    return app_qpylib.get_app_base_url()

def q_url_for(endpoint, **values):
    """ Returns the QRadar app proxy prefix joined to the Flask endpoint url. """
    return get_app_base_url() + app_qpylib.get_endpoint_url(endpoint, **values)

def get_console_address():
    ''' Returns the QRadar console IP address.
        Raises KeyError if environment variable QRADAR_CONSOLE_IP is not set.
    '''
    return app_qpylib.get_console_ip()

def get_console_fqdn():
    ''' Returns the QRadar console fully-qualified domain name.
        Raises KeyError if environment variable QRADAR_CONSOLE_FQDN is not set.
    '''
    return app_qpylib.get_console_fqdn()

# ==== REST ====

# pylint: disable=invalid-name, too-many-arguments
def REST(rest_action, request_url, version=None, headers=None, data=None,
         params=None, json_body=None, verify=True, timeout=60, **kwargs):
    ''' Invokes a rest_action request to request_url using the Python requests module.
        Returns a requests.Response object.
        Raises ValueError if rest_action is not one of GET, PUT, POST, DELETE.
    '''
    return rest_qpylib.rest(rest_action, request_url, version, headers, data,
                            params, json_body, verify, timeout, **kwargs)

# ==== JSON ====

def to_json_dict(python_obj, classkey=None):
    """ Converts a Python object into a dict usable with the REST function.
        Recursively converts fields which are also Python objects.
    """
    return json_qpylib.to_json_dict(python_obj, classkey)

def register_jsonld_endpoints():
    ''' Registers JSON-LD endpoints from the app manifest. '''
    json_qpylib.register_jsonld_endpoints()

def register_jsonld_type(context):
    ''' Registers a JSON-LD endpoint from the given context. '''
    json_qpylib.register_jsonld_type_from_context(context)

def get_offense_rendering(offense_id, render_type):
    ''' Returns an offense, rendered according to render_type.
        render_type is HTML or JSONLD.
    '''
    return offense_qpylib.get_offense_rendering(offense_id, render_type)

def get_asset_rendering(asset_id, render_type):
    ''' Returns an asset, rendered according to render_type.
        render_type is HTML or JSONLD.
    '''
    return asset_qpylib.get_asset_rendering(asset_id, render_type)

def render_jsonld_type(jld_type, data, jld_id=None):
    ''' Returns a JSON-LD type value rendered as a JSON-formatted string. '''
    return json_qpylib.render_jsonld_type(jld_type, data, jld_id)
