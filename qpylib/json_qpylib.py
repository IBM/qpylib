# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import json
from . import app_qpylib

# A dictionary of jsonld context types mapped to the type name
jsonld_types = {}

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
                argument=endpoint
                jsonld_context = _extract_jsonld_context(argument, 'request_mime_type', 'request_body_type')
                register_jsonld_type_from_context(jsonld_context)
            if 'response' in endpoint.keys():
                argument = endpoint['response']
                jsonld_context = _extract_jsonld_context(argument, 'mime_type', 'body_type')
                register_jsonld_type_from_context(jsonld_context)

def _extract_jsonld_context(argument, mime_id, context_id):
    if mime_id in argument.keys() and context_id in argument.keys():
        if argument[mime_id] == 'application/json+ld':
            return argument[context_id]

def register_jsonld_type_from_context(context):
    if context is not None:
        jsonld_type = _extract_type(context)
        register_jsonld_type(jsonld_type, context)

def register_jsonld_type(jsonld_type, context):
    global jsonld_types
    jsonld_types[str(jsonld_type)] = context

def get_jsonld_type(jsonld_type):
    global jsonld_types
    if jsonld_type in jsonld_types.keys():
        return jsonld_types[str(jsonld_type)]
    else:
        raise ValueError('json ld key has not been registered')

def _extract_type(argument):
    type_id=None
    if '@context' in argument.keys():
        context=argument['@context']
        if '@type' in context.keys():
            type_id=context['@type']
        if type_id == '@id' and '@id' in context.keys():
            type_id=context['@id']
    return type_id

def render_json_ld_type(jld_type, data, jld_id = None):
    jld_context = get_jsonld_type(jld_type)
    json_dict = {}
    for json_key in data:
        json_dict[json_key] = data[json_key]

    json_dict['@context'] = jld_context['@context']
    json_dict['@type'] = jld_type
    if jld_id is not None:
        json_dict['@type'] = jld_type

    return json.dumps(json_dict, sort_keys=True)

def json_ld(jld_context, jld_id, jld_type, name, description, data):
    return json.dumps({'@context': jld_context, '@id': jld_id, '@type': jld_type, 'name': name,
                       'description': description, 'data': data}, sort_keys=True)

def json_html(html):
    return json.dumps({'html': html})

def to_json_dict(python_obj, classkey=None):
    if isinstance(python_obj, str):
        return python_obj
    if isinstance(python_obj, dict):
        data = {}
        for (k, v) in list(python_obj.items()):
            data[k] = to_json_dict(v, classkey)
        return data
    elif hasattr(python_obj, "_ast"):
        return to_json_dict(python_obj._ast())
    elif hasattr(python_obj, "__iter__"):
        return [to_json_dict(v, classkey) for v in python_obj]
    elif hasattr(python_obj, "__dict__"):
        data = dict([(key, to_json_dict(value, classkey))
                     for key, value in python_obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(python_obj, "__class__"):
            data[classkey] = python_obj.__class__.__name__
        return data
    else:
        return python_obj
