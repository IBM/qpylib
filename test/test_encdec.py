# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=redefined-outer-name, unused-argument, invalid-name

import json
import os
import shutil
from unittest.mock import patch
import pytest
from qpylib.encdec import Encryption, EncryptionError

QUSER_DB_STORE = 'quser_e.db'

class DummyEngine():
    def __init__(self, config, app_uuid):
        self.config = config
        self.app_uuid = app_uuid

    @staticmethod
    def encrypt(clear_text_string):
        raise ValueError('Encryption failed')

# Use this fixture for tests that don't depend on reading an existing
# config file from disk. Avoids having to use tmpdir.
@pytest.fixture()
def patch_get_store_path():
    with patch('qpylib.qpylib.get_store_path') as mock_get_store_path:
        mock_get_store_path.return_value = QUSER_DB_STORE
        yield
        if os.path.isfile(QUSER_DB_STORE):
            os.remove(QUSER_DB_STORE)

# Use this for tests that use an actual config file from the encdec_db directory.
def copy_dbstore(dbstore_file_name, target_dir):
    dbstore_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     'encdec_db', dbstore_file_name)
    shutil.copy(dbstore_file_path, target_dir)

@pytest.fixture()
def uuid_env_var():
    os.environ['QRADAR_APP_UUID'] = '82c9bca4-7f1c-4a38-8011-d8e1742105b0'
    yield
    del os.environ['QRADAR_APP_UUID']

def test_init_raises_error_on_missing_data_fields():
    with pytest.raises(EncryptionError, match='You must supply name and user strings'):
        Encryption({})

def test_init_raises_error_on_missing_name_field():
    with pytest.raises(EncryptionError, match='You must supply name and user strings'):
        Encryption({'user': 'quser'})

def test_init_raises_error_on_missing_user_field():
    with pytest.raises(EncryptionError, match='You must supply name and user strings'):
        Encryption({'name': 'secret_thing'})

def test_init_raises_error_on_empty_name_field():
    with pytest.raises(EncryptionError, match='Supplied name and user cannot be empty'):
        Encryption({'name': '', 'user': 'quser'})

def test_init_raises_error_on_empty_user_field():
    with pytest.raises(EncryptionError, match='Supplied name and user cannot be empty'):
        Encryption({'name': 'secret_thing', 'user': ''})

def test_init_raises_error_on_whitespace_name_field():
    with pytest.raises(EncryptionError, match='Supplied name and user cannot be empty'):
        Encryption({'name': '   ', 'user': 'quser'})

def test_init_raises_error_on_whitespace_user_field():
    with pytest.raises(EncryptionError, match='Supplied name and user cannot be empty'):
        Encryption({'name': 'secret_thing', 'user': '     '})

def test_init_raises_error_on_missing_uuid_env_var():
    with pytest.raises(EncryptionError, match='Environment variable QRADAR_APP_UUID is missing'):
        Encryption({'name': 'secret_thing', 'user': 'quser'})

def test_init_raises_error_on_invalid_config_file_json(uuid_env_var, tmpdir):
    db_store = 'bad_content_e.db'
    db_store_path = os.path.join(tmpdir.strpath, db_store)
    with open(db_store_path, 'w') as db_file:
        db_file.write('{invalid json}')
    with patch('qpylib.qpylib.get_store_path') as mock_get_store_path:
        mock_get_store_path.return_value = db_store_path
        with pytest.raises(EncryptionError, match='Unable to load config store'):
            Encryption({'name': 'secret_thing', 'user': 'bad_content'})

def test_init_creates_empty_config_when_config_db_missing(uuid_env_var, patch_get_store_path):
    enc = Encryption({'name': 'secret_thing', 'user': 'mystery_user'})
    assert not enc.config

def test_decrypt_raises_error_when_config_empty(uuid_env_var, patch_get_store_path):
    enc = Encryption({'name': 'secret_thing', 'user': 'mystery_user'})
    with pytest.raises(EncryptionError, match='No config found for name secret_thing'):
        enc.decrypt()

def test_decrypt_raises_error_when_secret_not_in_config_db(uuid_env_var, tmpdir):
    db_store = 'missing_secret_e.db'
    db_store_path = os.path.join(tmpdir.strpath, db_store)
    with open(db_store_path, 'w') as db_file:
        db_file.write('{"secret_thing": {"version": 3}}')
    with patch('qpylib.qpylib.get_store_path') as mock_get_store_path:
        mock_get_store_path.return_value = db_store_path
        enc = Encryption({'name': 'secret_thing', 'user': 'missing_secret'})
        with pytest.raises(EncryptionError, match='No secret found for name secret_thing'):
            enc.decrypt()

def test_decrypt_raises_error_on_invalid_config_engine_version(uuid_env_var, tmpdir):
    db_store = 'bad_engine_version_e.db'
    db_store_path = os.path.join(tmpdir.strpath, db_store)
    with open(db_store_path, 'w') as db_file:
        db_file.write('{"secret_thing": {"version": 1, "secret": "522ae11b6b2b88cb1bb16adea76f7b96"}}')
    with patch('qpylib.qpylib.get_store_path') as mock_get_store_path:
        mock_get_store_path.return_value = db_store_path
        enc = Encryption({'name': 'secret_thing', 'user': 'bad_engine_version'})
        with pytest.raises(EncryptionError,
                           match='Config for name secret_thing contains invalid engine version 1'):
            enc.decrypt()

def test_decrypt_raises_error_on_decryption_failure(uuid_env_var, tmpdir):
    db_store = 'badsecret_e.db'
    copy_dbstore(db_store, tmpdir.strpath)
    with patch('qpylib.qpylib.get_store_path') as mock_get_store_path:
        mock_get_store_path.return_value = os.path.join(tmpdir.strpath, db_store)
        enc = Encryption({'name': 'secret_thing', 'user': 'badsecret'})
        with pytest.raises(EncryptionError,
                           match='Failed to decrypt secret for name secret_thing: InvalidToken'):
            enc.decrypt()

def test_encrypt_raises_error_on_encryption_failure(uuid_env_var, patch_get_store_path):
    enc = Encryption({'name': 'secret_thing', 'user': 'quser'})
    enc.encrypt('mypassword')
    with patch('qpylib.encdec.Encryption.latest_engine_class') as mock_latest_engine:
        mock_latest_engine.return_value = DummyEngine
        with pytest.raises(EncryptionError,
                           match='Failed to encrypt secret for name secret_thing: ValueError'):
            enc.encrypt('mypassword')

def test_encrypt_stores_encrypted_secret(uuid_env_var, patch_get_store_path):
    enc = Encryption({'name': 'secret_thing', 'user': 'quser'})
    enc_string = enc.encrypt('testing123')
    assert enc_string != 'testing123'
    with open(QUSER_DB_STORE) as db_file:
        store_json = json.load(db_file)
    assert store_json['secret_thing']['secret'] == enc_string

def test_decrypt_returns_original_value_after_encryption(uuid_env_var, patch_get_store_path):
    enc = Encryption({'name': 'secret_thing', 'user': 'quser'})
    enc_string = enc.encrypt('testing123')
    assert enc_string != 'testing123'
    assert enc.decrypt() == 'testing123'

def test_init_strips_leading_and_trailing_whitespace(uuid_env_var, patch_get_store_path):
    enc = Encryption({'name': '  secret_thing  ', 'user': '  quser    '})
    enc_string = enc.encrypt('testing123')
    with open(QUSER_DB_STORE) as db_file:
        store_json = json.load(db_file)
    assert store_json['secret_thing']['secret'] == enc_string

@pytest.fixture()
def v2_uuid_env_var():
    os.environ['QRADAR_APP_UUID'] = 'a1b2c3d4-4896-11e8-842f-0ed5f89f718b'
    yield
    del os.environ['QRADAR_APP_UUID']

def test_decrypt_handles_enginev2_secrets(v2_uuid_env_var, tmpdir):
    db_store = 'v2user_e.db'
    copy_dbstore(db_store, tmpdir.strpath)
    with patch('qpylib.qpylib.get_store_path') as mock_get_store_path:
        mock_get_store_path.return_value = os.path.join(tmpdir.strpath, db_store)
        mykey = Encryption({'name': 'mykey', 'user': 'v2user'})
        assert mykey.decrypt() == '12345678'
        mytoken = Encryption({'name': 'mytoken', 'user': 'v2user'})
        assert mytoken.decrypt() == 'abcdefghij'

def test_decrypt_v2_secret_reencrypts_with_latest_engine(v2_uuid_env_var, tmpdir):
    db_store = 'v2user_e.db'
    copy_dbstore(db_store, tmpdir.strpath)
    with patch('qpylib.qpylib.get_store_path') as mock_get_store_path:
        db_store_path = os.path.join(tmpdir.strpath, db_store)
        mock_get_store_path.return_value = db_store_path
        mytoken = Encryption({'name': 'mytoken', 'user': 'v2user'})
        assert 'version' not in mytoken.config['mytoken']
        assert mytoken.decrypt() == 'abcdefghij'
        # DB config for 'mytoken' has now been updated with latest engine version details.
        mytoken2 = Encryption({'name': 'mytoken', 'user': 'v2user'})
        assert mytoken2.config['mytoken']['version'] == Encryption.latest_engine_version
        assert mytoken2.decrypt() == 'abcdefghij'
        with open(db_store_path) as db_file:
            store_json = json.load(db_file)
        assert store_json['mytoken']['version'] == Encryption.latest_engine_version

@pytest.fixture()
def v3_uuid_env_var():
    os.environ['QRADAR_APP_UUID'] = '5b7e8085-ca96-41e1-8e4b-2983f0d595b8'
    yield
    del os.environ['QRADAR_APP_UUID']

def test_decrypt_handles_enginev3_secrets(v3_uuid_env_var, tmpdir):
    db_store = 'v3user_e.db'
    copy_dbstore(db_store, tmpdir.strpath)
    with patch('qpylib.qpylib.get_store_path') as mock_get_store_path:
        mock_get_store_path.return_value = os.path.join(tmpdir.strpath, db_store)
        mykey = Encryption({'name': 'mykey', 'user': 'v3user'})
        assert mykey.decrypt() == '12345678'
        mytoken = Encryption({'name': 'mytoken', 'user': 'v3user'})
        assert mytoken.decrypt() == 'abcdefghij'

def test_decrypt_v3_secret_reencrypts_with_latest_engine(v3_uuid_env_var, tmpdir):
    db_store = 'v3user_e.db'
    copy_dbstore(db_store, tmpdir.strpath)
    with patch('qpylib.qpylib.get_store_path') as mock_get_store_path:
        db_store_path = os.path.join(tmpdir.strpath, db_store)
        mock_get_store_path.return_value = db_store_path
        mytoken = Encryption({'name': 'mytoken', 'user': 'v3user'})
        assert mytoken.config['mytoken']['version'] == 3
        assert mytoken.decrypt() == 'abcdefghij'
        # DB config for 'mytoken' has now been updated with latest engine version details.
        mytoken2 = Encryption({'name': 'mytoken', 'user': 'v3user'})
        assert mytoken2.config['mytoken']['version'] == Encryption.latest_engine_version
        assert mytoken2.decrypt() == 'abcdefghij'
        with open(db_store_path) as db_file:
            store_json = json.load(db_file)
        assert store_json['mytoken']['version'] == Encryption.latest_engine_version

def test_encrypt_raises_error_when_config_db_not_writable(uuid_env_var, tmpdir):
    db_store = QUSER_DB_STORE
    db_store_path = os.path.join(tmpdir.strpath, db_store)
    with patch('qpylib.qpylib.get_store_path') as mock_get_store_path:
        mock_get_store_path.return_value = db_store_path
        enc = Encryption({'name': 'secret_thing', 'user': 'quser'})
        enc.encrypt('xyz')
        os.chmod(db_store_path, 0o400)
        with pytest.raises(EncryptionError, match='Unable to save config'):
            enc.encrypt('xyz')

def test_encrypt_decrypt_null_char(uuid_env_var, patch_get_store_path):
    enc = Encryption({'name': 'secret_thing', 'user': 'quser'})
    enc.encrypt('\x00')
    assert enc.decrypt() == '\x00'

def test_encrypt_decrypt_empty_string(uuid_env_var, patch_get_store_path):
    enc = Encryption({'name': 'secret_thing', 'user': 'quser'})
    enc.encrypt('')
    assert enc.decrypt() == ''

def test_encrypt_decrypt_whitespace(uuid_env_var, patch_get_store_path):
    enc = Encryption({'name': 'secret_thing', 'user': 'quser'})
    assert enc.encrypt('  \n \t ')
    assert enc.decrypt() == '  \n \t '
