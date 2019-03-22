# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import sys
import os
import pytest
import json
from mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'qpylib')))

import qpylib
import live_qpylib
from encdec import Encryption

mocked_get_store_path_value = 'test_user' + '_e.db'


# For testing purposes, override the logfile location and manifest as /store/log doesn't exist
# Also mock out get_manifest_json to return the test manifest in this directory as /app/manifest doesn't exist
@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup():
    live_qpylib.LOGFILE_LOCATION = 'testing.log'

    with patch('qpylib.LiveQpylib.get_manifest_json') as mocked_get_manifest_method:
        with open(os.path.join(os.path.dirname(__file__), 'test_manifest.json')) as test_manifest:
            mocked_get_manifest_method.return_value = json.load(test_manifest)
        with patch('live_qpylib.SysLogHandler') as mock_sys_log_handler:
            mock_sys_log_handler.return_value = mock_sys_log_handler.MockSysLogHandler()
            qpylib.create_log()
        yield


# Mock out get_store_path to return encryption db in test dir, then delete after each test
@pytest.fixture()
def patch_get_store_path():
    file_path = mocked_get_store_path_value
    with patch('qpylib.get_store_path') as mocked_get_store_path:
        mocked_get_store_path.return_value = mocked_get_store_path_value
        yield
        if os.path.isfile(file_path):
            os.remove(file_path)


@pytest.fixture()
def set_unset_qradar_app_uuid_env_var():
    os.environ['QRADAR_APP_UUID'] = "6599ba78-4896-11e8-842f-0ed5f89f718b"
    yield
    del os.environ['QRADAR_APP_UUID']


class TestEncryptionInstantiation:

    def test_encryption_raises_value_error_on_missing_name_and_user_fields(self):
        with pytest.raises(ValueError) as ex:
            Encryption({})
        assert "Encryption : name and user are mandatory fields!" == str(ex.value)

        with pytest.raises(ValueError) as ex:
            Encryption({"name": "test_name"})
        assert "Encryption : name and user are mandatory fields!" == str(ex.value)

        with pytest.raises(ValueError) as ex:
            Encryption({"user": "test_user"})
        assert "Encryption : name and user are mandatory fields!" == str(ex.value)

    def test_encryption_raises_value_error_on_missing_env_var(self):
        with pytest.raises(KeyError) as ex:
            Encryption({"name": "test_name", "user": "test_user"})
        print ex.value
        assert "'Encryption : QRADAR_APP_UUID not available in environment'" == str(ex.value)

    def test_encrypt_creates_valid_config_on_start(self, set_unset_qradar_app_uuid_env_var, patch_get_store_path):
        Encryption({"name": "test_name", "user": "test_user"})
        assert os.path.isfile(mocked_get_store_path_value)


class TestEncryptionDecryption:

    def test_encryption_returns_false_encrypting_empty_string(self, set_unset_qradar_app_uuid_env_var,
                                                              patch_get_store_path):
        enc = Encryption({"name": "test_name", "user": "test_user"})
        assert enc.encrypt('') is False

    def test_encryption_stores_encrypted_secret_in_config(self, set_unset_qradar_app_uuid_env_var,
                                                          patch_get_store_path):
        enc = Encryption({"name": "test_name", "user": "test_user"})
        # ensure encrypted string does not equal plaintext
        enc_string = enc.encrypt('testing123')
        assert enc_string != 'testing123'

        with open(mocked_get_store_path_value) as db_file:
            file_json = json.load(db_file)
            assert file_json.get('test_name').get('secret') == enc_string

    def test_decrypt_returns_plaintext_after_encryption(self, set_unset_qradar_app_uuid_env_var,
                                                        patch_get_store_path):
        enc = Encryption({"name": "test_name", "user": "test_user"})
        # ensure encrypted string does not equal plaintext
        enc_string = enc.encrypt('testing123')
        assert enc_string != 'testing123'
        assert enc.decrypt() == 'testing123'

    def test_decrypt_returns_blank_string_when_config_missing(self, set_unset_qradar_app_uuid_env_var,
                                                        patch_get_store_path):
        enc = Encryption({"name": "test_name", "user": "test_user"})
        # ensure encrypted string does not equal plaintext
        enc_string = enc.encrypt('testing123')
        assert enc_string != 'testing123'
        os.remove(mocked_get_store_path_value)
        enc = Encryption({"name": "test_name", "user": "test_user"})
        assert enc.decrypt() == ''

    def test_decrypt_returns_incorrect_plaintext_with_altered_salt(self, set_unset_qradar_app_uuid_env_var,
                                                        patch_get_store_path):
        enc = Encryption({"name": "test_name", "user": "test_user"})
        # ensure encrypted string does not equal plaintext
        enc_string = enc.encrypt('testing123')
        assert enc_string != 'testing123'

        with open(mocked_get_store_path_value) as db_file:
            file_json = json.load(db_file)
        file_json['test_name']['salt'] = 'incorrect'
        with open(mocked_get_store_path_value, 'w') as db_file:
            json.dump(file_json, db_file)
        enc = Encryption({"name": "test_name", "user": "test_user"})
        assert enc.decrypt() != 'testing123'
