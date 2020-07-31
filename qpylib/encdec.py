# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=broad-except

import json
import os
from qpylib import qpylib
from qpylib.encryption.enginev2 import Enginev2
from qpylib.encryption.enginev3 import Enginev3
from qpylib.encryption.enginev4 import Enginev4

class EncryptionError(Exception):
    ''' All errors encountered by Encryption are reported via this class '''

class Encryption():
    ''' Convenience functions for managing encrypted data items.

        The first incarnation of encdec was distributed as a stand-alone module,
        not part of qpylib. It is no longer supported. In retrospect, that version
        has been designated as v1, and engine versions here start at v2.

        Developer information
        ---------------------
        If the encryption algorithm needs to be changed, follow these steps:
          - Create a new engine version class in qpylib.encryption.
          - In the previous engine version class, remove all encryption-related
            functions, leaving only decryption-related code.
          - Update the engines dictionary below.
    '''
    engines = {2: Enginev2, 3: Enginev3, 4: Enginev4}
    latest_engine_version = max(engines)

    def __init__(self, data):
        ''' data is an object containing two non-empty strings:
            'name': a label for the item you want to encrypt.
            'user': a user identifier that is used to create a store file to hold
                    the encrypted item and accompanying configuration. A user's
                    store file can hold multiple encrypted items.
        '''
        try:
            self.name = str(data['name']).strip()
            self.user_id = str(data['user']).strip()
        except (KeyError, TypeError):
            raise EncryptionError('You must supply name and user strings')

        if not self.name or not self.user_id:
            raise EncryptionError('Supplied name and user cannot be empty')

        self.app_uuid = os.environ.get('QRADAR_APP_UUID')

        if not self.app_uuid:
            raise EncryptionError('Environment variable QRADAR_APP_UUID is missing')

        self.config_store_path = qpylib.get_store_path('{0}_e.db'.format(self.user_id))

        if os.path.isfile(self.config_store_path):
            self.config = self._read_config()
        else:
            self.config = {}

    def encrypt(self, clear_text):
        ''' Encrypts clear_text using the latest engine version.
            Stores the encrypted value using the data provided to the init function,
            i.e. in a store file named 'user'_e.db under label 'name'.
            Returns the encrypted value.
        '''
        self._reset_config_if_required()
        engine = self.latest_engine_class()(self.config[self.name], self.app_uuid)

        try:
            encrypted_secret = engine.encrypt(clear_text)
        except Exception as error:
            raise EncryptionError('Failed to encrypt secret for name {0}: {1}'
                                  .format(self.name, type(error).__name__))

        self.config[self.name]['secret'] = encrypted_secret
        self._save_config()
        return encrypted_secret

    def decrypt(self):
        ''' Decrypts the item with label 'name' from store file named 'user'_e.db
            (see init function), using the appropriate engine version.
            If the item was originally encrypted using an older engine version,
            it is re-encrypted using the latest engine, and the store file content
            for the item is replaced.
            Returns the decrypted value.
        '''
        if self.name not in self.config:
            raise EncryptionError('No config found for name {0}'.format(self.name))

        if 'secret' not in self.config[self.name]:
            raise EncryptionError('No secret found for name {0}'.format(self.name))

        engine = self._choose_engine()
        try:
            secret = engine.decrypt()
        except Exception as error:
            raise EncryptionError('Failed to decrypt secret for name {0}: {1}'
                                  .format(self.name, type(error).__name__))

        if engine.version != Encryption.latest_engine_version:
            self.encrypt(secret)

        return secret

    @staticmethod
    def latest_engine_class():
        return Encryption.engines[Encryption.latest_engine_version]

    def _choose_engine(self):
        # If no version is present in the config we default to engine v2.
        try:
            engine_version = self.config[self.name]['version']
        except KeyError:
            engine_version = 2

        try:
            engine = Encryption.engines[engine_version]
        except KeyError:
            raise EncryptionError('Config for name {0} contains invalid engine version {1}'
                                  .format(self.name, engine_version))
        return engine(self.config[self.name], self.app_uuid)

    def _reset_config_if_required(self):
        # Keep current config if it has an engine version that is the latest,
        # otherwise reset to latest engine config.
        reset_required = False
        try:
            if self.config[self.name]['version'] != Encryption.latest_engine_version:
                reset_required = True
        except KeyError:
            reset_required = True
        if reset_required:
            self.config[self.name] = self.latest_engine_class().generate_config()

    def _read_config(self):
        try:
            with open(self.config_store_path) as config_file:
                return json.load(config_file)
        except Exception as error:
            raise EncryptionError('Unable to load config store {0}: {1}'
                                  .format(self.config_store_path, error))

    def _save_config(self):
        try:
            with open(self.config_store_path, 'w') as config_file:
                config_file.write(json.dumps(self.config))
        except Exception as error:
            raise EncryptionError('Unable to save config to {0}: {1}'
                                  .format(self.config_store_path, error))
