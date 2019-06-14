# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from binascii import a2b_hex, b2a_hex
import json
import os
import string
import uuid
from . import qpylib

from Crypto.Random import random
from Crypto.Cipher import AES
from Crypto.Protocol import KDF

# The encryption class is now version aware.
# EACH BREAKING CHANGE IN THE CRYPTOGRAPHIC METHODS SHOULD INCREMENT THE VERSION
# This enables better error handling for users. Users can also query the
# engine version to make decisions on how to handle secrets
class Encryption(object):
    engine_version = 3
    def __init__(self, data):
        if 'name' not in data or 'user' not in data or data['name'] == '' or data['user'] == '':
            raise ValueError("Encryption : name and user are mandatory fields!")
        self.APP_UUID_ENV_VARIABLE = 'QRADAR_APP_UUID'
        if self.APP_UUID_ENV_VARIABLE not in os.environ:
            raise KeyError("Encryption : {0} not available in environment".format(self.APP_UUID_ENV_VARIABLE))
        self.name = data['name']
        self.user_id = data['user']
        self.app_uuid = os.environ.get(self.APP_UUID_ENV_VARIABLE)
        self.config_path = qpylib.get_store_path(str(self.user_id) + '_e.db')
        self.config = {}
        self.__load_config()

    def __init_config(self):
        """ Generates crypto config values and saves them to a file """
        self.config[self.name] = {}
        self.config[self.name]['salt'] = self.__generate_random()
        self.config[self.name]['UUID'] = self.__generate_token()
        self.config[self.name]['ivz'] = self.__generate_random()
        self.config[self.name]['iterations'] = 100000
        self.__save_config()

    def __load_config(self):
        """ Loads config file from disk or creates the file if it doesn't exist """
        try:
            with open(self.config_path) as config_file:
                self.config = json.load(config_file)
                if self.name not in self.config:
                    self.__init_config()

        except IOError:
            qpylib.log('encdec : __load_config : Encryption config file does not exist, creating')
            self.__init_config()

        except Exception as error:  # pylint: disable=W0703
            qpylib.log('encdec : __load_config : Error reading Encryption config file : {0}'.format(str(error)))
            self.__init_config()

    def __save_config(self):
        """ Writes the config object to a file on disk """
        try:
            with open(self.config_path, 'w') as config_file:
                config_file.write(json.dumps(self.config))

        except Exception as error:  # pylint: disable=W0703
            qpylib.log('encdec : __save_config : Error saving Encryption config file: {0}'.format(str(error)))

    def __generate_token(self):
        """ Generates a UUID to be used as reference_data map name. """
        token = str(uuid.uuid4())
        if len(self.config) > 0:
            for name in self.config:
                if 'UUID' in self.config[name] and token == str(self.config[name]['UUID']):
                    token = self.__generate_token()
        return token

    def __generate_random(self):
        """ Returns a string containing a random hash that uses letters, digits and special characters """
        random_hash = ''.join(
            (
                random.choice(string.ascii_letters + string.digits + string.punctuation)
            )
            for _ in range(16)
        )
        return random_hash

    def __derive_key(self):
        """ Generates derived key using stored config """
        return KDF.PBKDF2(self.app_uuid + self.config[self.name]['UUID'],
                          self.config[self.name]['salt'].encode('utf-8'),
                          dkLen=32, #32 bytes = 256 bits, max AES key length
                          count=self.config[self.name]['iterations'])

    def __encrypt_string(self, clear_text_string):
        """ Returns a string containing an encrypted copy of clear_text_string """
        aes = AES.new(
            self.__derive_key(),
            AES.MODE_CFB,
            self.config[self.name]['ivz'].encode('utf-8'),
            segment_size=128)
        clear_text_padded_string = self.__pad_string(clear_text_string)
        encrypted_bytes = aes.encrypt(clear_text_padded_string.encode("utf8"))
        encrypted_hex_bytes = b2a_hex(encrypted_bytes).rstrip()
        return encrypted_hex_bytes.decode('utf-8')

    def __decrypt_string(self, encrypted_string):
        """ Returns a string containing a decrypted copy of encrypted_string.
            encrypted_string must be the result of a previous call to encrypt(). """
        aes = AES.new(
            self.__derive_key(),
            AES.MODE_CFB,
            self.config[self.name]['ivz'].encode('utf-8'),
            segment_size=128)
        encrypted_hex_bytes = encrypted_string.encode('utf-8')
        encrypted_bytes = a2b_hex(encrypted_hex_bytes)
        decrypted_bytes = aes.decrypt(encrypted_bytes)
        clear_text_padded_string = decrypted_bytes.decode('utf-8')
        return self.__unpad_string(clear_text_padded_string)

    def __pad_string(self, value):
        """ Adds padding to the string so that the resulting length is a multiple of 16 """
        length = len(value)
        pad_size = 16 - (length % 16)
        return value.ljust(length + pad_size, '\x00')

    def __unpad_string(self, value):
        """ Removes the added padding from the string """
        while value[-1] == '\x00':
            value = value[:-1]
        return value

    def encrypt(self, clear_text):
        """ Encrypts a clear text secret """
        if clear_text.strip(' \t\n\r') == '':
            qpylib.log('encdec : encrypt : Unable to encrypt an empty string')
            return str('')

        try:
            self.config[self.name]['version'] = Encryption.engine_version
            self.config[self.name]['secret'] = self.__encrypt_string(clear_text)
            self.__save_config()
            return self.config[self.name]['secret']

        except Exception as error:  # pylint: disable=W0703
            qpylib.log('encdec : encrypt : Failed to encrypt secret: {0}'.format(error))
            return str('')

    def decrypt(self):
        """ Decrypts and returns the previously-encrypted secret"""
        if 'secret' not in self.config[self.name]:
            raise ValueError("Encryption : no secret to decrypt")

        if self.config[self.name].get('version') != Encryption.engine_version:
            raise ValueError("Encryption : secret engine mismatch. Secret was stored with version {}, attempted to decrypt with version {}.".format(self.config[self.name].get('version') , Encryption.engine_version))

        try:
            return self.__decrypt_string(self.config[self.name]['secret'])

        except Exception as error:  # pylint: disable=W0703
            qpylib.log('encdec : decrypt : Failed to decrypt secret : {0}'.format(error))
            return str('')
