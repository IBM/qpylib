# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=unused-argument

import os
from unittest.mock import patch
import pytest
from qpylib import qpylib, json_qpylib

MANIFEST_JSON_ROOT_PATH = 'qpylib.app_qpylib.get_root_path'

def manifest_path(manifest_file):
    return os.path.join(os.path.dirname(__file__), 'manifests', manifest_file)

@pytest.fixture(scope='function', autouse=True)
def reset_globals():
    json_qpylib.JSONLD_TYPES = {}
    qpylib.app_qpylib.Q_CACHED_MANIFEST = None

def test_register_jsonld_type_where_type_is_id():
    context = {json_qpylib.KEY_CONTEXT: {json_qpylib.KEY_TYPE: json_qpylib.KEY_ID,
                                         json_qpylib.KEY_ID: 'some-id'}}
    qpylib.register_jsonld_type(context)
    assert len(json_qpylib.JSONLD_TYPES) == 1
    assert json_qpylib.JSONLD_TYPES['some-id'][json_qpylib.KEY_CONTEXT][json_qpylib.KEY_ID] == 'some-id'

def test_register_jsonld_type_where_type_is_not_id():
    context = {json_qpylib.KEY_CONTEXT: {json_qpylib.KEY_TYPE: 'mytype', json_qpylib.KEY_ID: 'some-id'}}
    qpylib.register_jsonld_type(context)
    assert len(json_qpylib.JSONLD_TYPES) == 1
    assert json_qpylib.JSONLD_TYPES['mytype'][json_qpylib.KEY_CONTEXT][json_qpylib.KEY_ID] == 'some-id'

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('installed.json'))
def test_register_jsonld_endpoints_no_services(mock_manifest):
    qpylib.register_jsonld_endpoints()
    assert len(json_qpylib.JSONLD_TYPES) == 0

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('services.json'))
def test_register_jsonld_endpoints(mock_manifest):
    qpylib.register_jsonld_endpoints()
    assert len(json_qpylib.JSONLD_TYPES) == 2
    assert json_qpylib.JSONLD_TYPES['type1'][json_qpylib.KEY_CONTEXT][json_qpylib.KEY_ID] == 'id1'
    assert json_qpylib.JSONLD_TYPES['id2'][json_qpylib.KEY_CONTEXT][json_qpylib.KEY_ID] == 'id2'

def test_render_jsonld_type_no_keys_registered():
    with pytest.raises(ValueError, match='JSON-LD type dummytype has not been registered'):
        qpylib.render_jsonld_type('dummytype', {})

@patch(MANIFEST_JSON_ROOT_PATH, return_value=manifest_path('services.json'))
def test_render_jsonld_type(mock_manifest):
    qpylib.register_jsonld_endpoints()
    assert qpylib.render_jsonld_type('type1', {'mykey': 'myval', 'k1': 'v1'}, 'newid') == \
        ('{"@context": {"@id": "id1", "@type": "type1"}, "@id": "newid", "@type": "type1", '
         '"k1": "v1", "mykey": "myval"}')

def test_string_to_json_dict():
    assert qpylib.to_json_dict('string') == 'string'

def test_dict_to_json_dict():
    new_dict = qpylib.to_json_dict({'k1': 'v1', 'k2': 2, 'k3': [2, 4, 6]})
    assert new_dict['k1'] == 'v1'
    assert new_dict['k2'] == 2
    assert new_dict['k3'][2] == 6

# pylint: disable=too-few-public-methods
class MyClass():
    def __init__(self, thing):
        self.version = 3
        self.thing = thing

def test_class_to_json_dict():
    new_dict = qpylib.to_json_dict(MyClass('banana'), classkey='theclassname')
    assert new_dict['theclassname'] == 'MyClass'
    assert new_dict['version'] == 3
    assert new_dict['thing'] == 'banana'
