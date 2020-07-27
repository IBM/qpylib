# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import json
from . import app_qpylib

# A dictionary of jsonld context types mapped to the type name
JSONLD_TYPES = {}

KEY_CONTEXT = '@context'
KEY_TYPE = '@type'
KEY_ID = '@id'

def register_jsonld_endpoints():
    manifest = app_qpylib.get_manifest_json()

    services = None
    if 'services' in manifest.keys():
        services = manifest['services']
    if services is None:
        return

    for service in services:
        endpoints = None
        if 'endpoints' in service.keys():
            endpoints = service['endpoints']
        if endpoints is None:
            continue
        for endpoint in endpoints:
            jsonld_context = None
            if 'request_mime_type' in endpoint.keys():
                argument = endpoint
                jsonld_context = _extract_jsonld_context(argument, 'request_mime_type', 'request_body_type')
                register_jsonld_type_from_context(jsonld_context)
            if 'response' in endpoint.keys():
                argument = endpoint['response']
                jsonld_context = _extract_jsonld_context(argument, 'mime_type', 'body_type')
                register_jsonld_type_from_context(jsonld_context)

def _extract_jsonld_context(argument, mime_id, context_id):
    if (mime_id in argument.keys() and
            context_id in argument.keys() and
            argument[mime_id] == 'application/json+ld'):
        return argument[context_id]
    return None

def register_jsonld_type_from_context(context):
    if context is not None:
        jsonld_type = _extract_type(context)
        register_jsonld_type(jsonld_type, context)

def register_jsonld_type(jsonld_type, context):
    global JSONLD_TYPES
    JSONLD_TYPES[str(jsonld_type)] = context

def get_jsonld_type(jsonld_type):
    global JSONLD_TYPES
    if jsonld_type in JSONLD_TYPES.keys():
        return JSONLD_TYPES[str(jsonld_type)]
    raise ValueError('json ld key has not been registered')

def _extract_type(argument):
    type_id = None
    if KEY_CONTEXT in argument.keys():
        context = argument[KEY_CONTEXT]
        if KEY_TYPE in context.keys():
            type_id = context[KEY_TYPE]
        if type_id == KEY_ID and KEY_ID in context.keys():
            type_id = context[KEY_ID]
    return type_id

def render_json_ld_type(jld_type, data, jld_id=None):
    jld_context = get_jsonld_type(jld_type)
    json_dict = {}
    for json_key in data:
        json_dict[json_key] = data[json_key]

    json_dict[KEY_CONTEXT] = jld_context[KEY_CONTEXT]
    json_dict[KEY_TYPE] = jld_type
    if jld_id is not None:
        json_dict[KEY_TYPE] = jld_type

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
