# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import json
from . import app_qpylib

JSONLD_TYPES = {}
KEY_CONTEXT = '@context'
KEY_TYPE = '@type'
KEY_ID = '@id'

def register_jsonld_endpoints():
    try:
        services = app_qpylib.get_manifest_json()['services']
    except KeyError:
        return

    for service in services:
        try:
            endpoints = service['endpoints']
        except KeyError:
            continue
        for endpoint in endpoints:
            _extract_and_register_jsonld_context(endpoint, 'request_mime_type', 'request_body_type')
            try:
                _extract_and_register_jsonld_context(endpoint['response'], 'mime_type', 'body_type')
            except KeyError:
                pass

def _extract_and_register_jsonld_context(endpoint_direction, mime_id, body_id):
    try:
        if endpoint_direction[mime_id] == 'application/json+ld':
            register_jsonld_type_from_context(endpoint_direction[body_id])
    except KeyError:
        pass

def register_jsonld_type(jsonld_type, context):
    JSONLD_TYPES[str(jsonld_type)] = context

def register_jsonld_type_from_context(context):
    jsonld_type = _extract_type_from_context(context)
    if jsonld_type:
        register_jsonld_type(jsonld_type, context)

def _extract_type_from_context(context):
    if KEY_CONTEXT in context.keys():
        at_context = context[KEY_CONTEXT]
        if KEY_TYPE in at_context.keys():
            if at_context[KEY_TYPE] == KEY_ID and KEY_ID in at_context.keys():
                return at_context[KEY_ID]
            return at_context[KEY_TYPE]
    return None

def get_jsonld_type(jsonld_type):
    try:
        return JSONLD_TYPES[str(jsonld_type)]
    except KeyError:
        raise ValueError('JSON-LD type {0} has not been registered'.format(str(jsonld_type)))

def render_jsonld_type(jld_type, data, jld_id=None):
    jld_context = get_jsonld_type(jld_type)
    json_dict = {KEY_CONTEXT: jld_context[KEY_CONTEXT], KEY_TYPE: jld_type}
    if jld_id:
        json_dict[KEY_ID] = jld_id
    for json_key in data:
        json_dict[json_key] = data[json_key]
    return json.dumps(json_dict, sort_keys=True)

# pylint: disable=too-many-arguments
def json_ld(jld_context, jld_id, jld_type, name, description, data):
    return json.dumps({KEY_CONTEXT: jld_context, KEY_ID: jld_id, KEY_TYPE: jld_type, 'name': name,
                       'description': description, 'data': data}, sort_keys=True)

def json_html(html):
    return json.dumps({'html': html})

def to_json_dict(python_obj, classkey=None):
    if isinstance(python_obj, str):
        return python_obj
    if isinstance(python_obj, dict):
        data = {}
        for (k, val) in list(python_obj.items()):
            data[k] = to_json_dict(val, classkey)
        return data
    if hasattr(python_obj, "__iter__"):
        return [to_json_dict(v, classkey) for v in python_obj]
    # pylint: disable=consider-using-dict-comprehension
    if hasattr(python_obj, "__dict__"):
        data = dict([(key, to_json_dict(value, classkey))
                     for key, value in python_obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(python_obj, "__class__"):
            data[classkey] = python_obj.__class__.__name__
        return data
    return python_obj
