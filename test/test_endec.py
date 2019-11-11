# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=redefined-outer-name, unused-argument

import json
from unittest.mock import patch
import os
import pytest
from qpylib.encdec import Encryption

DB_STORE = 'test_user_e.db'


@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup():
    with patch('qpylib.abstract_qpylib.AbstractQpylib.log'):
        yield

# Mock out get_store_path to return encryption db in test dir, then delete after each test
@pytest.fixture()
def patch_get_store_path():
    file_path = DB_STORE
    with patch('qpylib.qpylib.get_store_path') as mocked_get_store_path:
        mocked_get_store_path.return_value = DB_STORE
        yield
        if os.path.isfile(file_path):
            os.remove(file_path)

@pytest.fixture()
def repeatable_encrypt():
    e = Encryption({"name": "test_name", "user": "test_user"})
    e.config["test_name"]['salt'] = 'Lk&RBjmg,22Xcs`!'
    e.config["test_name"]['UUID'] = '6599ba78-4896-11e8-842f-0ed5f89f718b'
    e.config["test_name"]['ivz'] = 'AXN(=,ix7=s,e}g\\'
    e.config["test_name"]['iterations'] = 100000
    return e

@pytest.fixture()
def set_unset_qradar_app_uuid_env_var():
    os.environ['QRADAR_APP_UUID'] = "6599ba78-4896-11e8-842f-0ed5f89f718b"
    yield
    del os.environ['QRADAR_APP_UUID']

def test_encryption_raises_value_error_on_missing_name_and_user_fields():
    with pytest.raises(ValueError) as ex:
        Encryption({})
    assert "Encryption : name and user are mandatory fields!" == str(ex.value)

    with pytest.raises(ValueError) as ex:
        Encryption({"name": "test_name"})
    assert "Encryption : name and user are mandatory fields!" == str(ex.value)

    with pytest.raises(ValueError) as ex:
        Encryption({"user": "test_user"})
    assert "Encryption : name and user are mandatory fields!" == str(ex.value)

def test_encryption_raises_value_error_on_missing_env_var():
    with pytest.raises(KeyError) as ex:
        Encryption({"name": "test_name", "user": "test_user"})
    assert "'Encryption : QRADAR_APP_UUID not available in environment'" == str(ex.value)

def test_encrypt_creates_valid_config_on_start(set_unset_qradar_app_uuid_env_var, patch_get_store_path):
    Encryption({"name": "test_name", "user": "test_user"})
    assert os.path.isfile(DB_STORE)

def test_encryption_returns_empty_string_encrypting_empty_string(set_unset_qradar_app_uuid_env_var,
                                                                 patch_get_store_path):
    enc = Encryption({"name": "test_name", "user": "test_user"})
    assert enc.encrypt('') == ''

def test_encryption_stores_encrypted_secret_in_config(set_unset_qradar_app_uuid_env_var,
                                                      patch_get_store_path):
    enc = Encryption({"name": "test_name", "user": "test_user"})
    enc_string = enc.encrypt('testing123')
    assert enc_string != 'testing123'

    with open(DB_STORE) as db_file:
        file_json = json.load(db_file)
        assert file_json.get('test_name').get('secret') == enc_string

def test_decrypt_returns_plaintext_after_encryption(set_unset_qradar_app_uuid_env_var,
                                                    patch_get_store_path):
    enc = Encryption({"name": "test_name", "user": "test_user"})
    enc_string = enc.encrypt('testing123')
    assert enc_string != 'testing123'
    assert enc.decrypt() == 'testing123'

def test_decrypt_raises_error_when_config_missing(set_unset_qradar_app_uuid_env_var,
                                                  patch_get_store_path):
    enc = Encryption({"name": "test_name", "user": "test_user"})
    enc_string = enc.encrypt('testing123')
    assert enc_string != 'testing123'
    os.remove(DB_STORE)
    enc = Encryption({"name": "test_name", "user": "test_user"})
    with pytest.raises(ValueError) as ex:
        enc.decrypt()
    assert "Encryption : no secret to decrypt" == str(ex.value)

def test_decrypt_returns_incorrect_plaintext_with_altered_salt(set_unset_qradar_app_uuid_env_var,
                                                               patch_get_store_path):
    enc = Encryption({"name": "test_name", "user": "test_user"})
    enc_string = enc.encrypt('testing123')
    assert enc_string != 'testing123'

    with open(DB_STORE) as db_file:
        file_json = json.load(db_file)
    file_json['test_name']['salt'] = 'incorrect'
    with open(DB_STORE, 'w') as db_file:
        json.dump(file_json, db_file)
    enc = Encryption({"name": "test_name", "user": "test_user"})
    assert enc.decrypt() != 'testing123'

def test_decrypt_raise_value_error_on_engine_version_mismatch(set_unset_qradar_app_uuid_env_var,
                                                               patch_get_store_path):
    enc = Encryption({"name": "test_name", "user": "test_user"})
    enc_string = enc.encrypt('testing123')
    assert enc_string != 'testing123'

    with open(DB_STORE) as db_file:
        file_json = json.load(db_file)
    file_json['test_name']['version'] = -1
    with open(DB_STORE, 'w') as db_file:
        json.dump(file_json, db_file)
    enc = Encryption({"name": "test_name", "user": "test_user"})
    with pytest.raises(ValueError) as ex:
        enc.decrypt()
    assert "Encryption : secret engine mismatch." in str(ex.value)

def test_encrypt_decrypt_null_char(set_unset_qradar_app_uuid_env_var,
                                   patch_get_store_path, repeatable_encrypt):
    enc_string = repeatable_encrypt.encrypt('\x00')
    assert enc_string == 'cd09251dde83002c7d426a3d065a89bb'
    dec_string = repeatable_encrypt.decrypt()
    assert dec_string == '\x00'
