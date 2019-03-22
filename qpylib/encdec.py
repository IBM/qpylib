#!/bin/python

# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import os
import json
import random
import string
import binascii
import qpylib

from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Protocol import KDF

class Encryption(object):

    """ Encryption Logic """

    def __init__(self, data):
        self.IKM_ENV_VARIABLE = 'QRADAR_APP_UUID'
        if 'name' not in data or 'user' not in data \
                or data['name'] == '' or data['user'] == '':
            raise ValueError("Encryption : name and user are mandatory fields!")
        if self.IKM_ENV_VARIABLE not in os.environ:
            raise KeyError("Encryption : {0} not available in environment".format(str(self.IKM_ENV_VARIABLE)))
        self.ikm = os.environ.get(self.IKM_ENV_VARIABLE)
        self.name = data['name']
        self.user_id = data['user']
        self.config_path = qpylib.get_store_path(str(self.user_id) + '_e.db')
        self.config = {}
        self.__load_conf()

    def __init_config(self):
        """ Generates salt, initvector and iterations to be used and saves them to a config file"""
        self.config[self.name] = {}
        self.config[self.name]['salt'] = self.__generate_random()
        self.config[self.name]['UUID'] = self.__generate_token()
        self.config[self.name]['ivz'] = self.__generate_random()
        self.config[self.name]['iterations'] = random.randint(1500, 2000)
        self.__save()

    def __load_conf(self):
        """ Loads config file from the disk to get needed hashes
            if config doesnt exists creates it.
        """
        try:
            with open(self.config_path) as config_file:
                self.config = json.load(config_file)
                if self.name not in self.config:
                    self.__init_config()

        except IOError, error:
            qpylib.log('encdec : __load_conf : Encryption conf file : {0} does not exist, creating'.format(str(error)))            
            self.__init_config()

        except Exception, error:  # pylint: disable=W0703
            qpylib.log('encdec : __load_conf : Error reading Encryption conf file {0}'.format(str(error)))            
            self.__init_config()

    def __save(self):
        """ Saves the config object to a file on disk """
        try:
            with open(self.config_path, 'w') as config_file:
                config_file.write(json.dumps(self.config))

        except IOError, error:
            qpylib.log(
                'encdec : __save : Error saving Encryption conf file: {0}'.format(error))

        except Exception, error:  # pylint: disable=W0703
            qpylib.log('encdec : __load_conf : \
            Error Saving Encrypted Encryption conf file {0}'.format(str(error)))

    def __generate_token(self):
        """ Generates a MD5 Token to be used as UUID at reference_data map name. """
        newMd5 = MD5.new(self.__generate_random()).hexdigest()
        if len(self.config) > 0:
            for name in self.config:
                if 'UUID' in self.config[name] and str(newMd5) == str(self.config[name]['UUID']):
                    newMd5 = self.__generate_token()
        return newMd5

    def __generate_random(self):
        """ Generates a random hash with letters, digits and special characters """
        random_hash = ''.join(
            (
                random.choice(
                    string.letters +
                    string.digits +
                    string.punctuation
                )
            )
            for x in range(16)
        )
        return random_hash

    def __encrypt_string(self, clear_text):
        """ Encrypts a string """
        aes = AES.new(
            self.__generate_derived_key(),
            AES.MODE_CFB,
            self.config[self.name]['ivz'],
            segment_size=128)
        padded_text = self.__pad_string(clear_text)
        encrypted_text = aes.encrypt(padded_text)
        return binascii.b2a_hex(encrypted_text).rstrip()

    def __decrypt_string(self, encrypted_text):
        """ Decrypts a string """
        aes = AES.new(
            self.__generate_derived_key(),
            AES.MODE_CFB,
            self.config[self.name]['ivz'],
            segment_size=128)
        encrypted_text_bytes = binascii.a2b_hex(encrypted_text)
        padded_text = aes.decrypt(encrypted_text_bytes)
        decrypted_text = self.__unpad_string(padded_text)
        return decrypted_text

    def __pad_string(self, value):
        """ Adds padding to the string """
        length = len(value)
        pad_size = 16 - (length % 16)
        return value.ljust(length + pad_size, '\x00')

    def __unpad_string(self, value):
        """ Removes the added padding from the string """
        while value[-1] == '\x00':
            value = value[:-1]
        return value

    def __generate_derived_key(self):
        """
            generate derived key using initial keying material and salt
        """
        return KDF.PBKDF2(self.ikm + self.config[self.name]['UUID'], self.config[self.name]['salt'], dkLen=16,
                          count=self.config[self.name]['iterations'])

    def encrypt(self, clear_text):
        """ Encrypts a clear text secret """
        if clear_text.strip(' \t\n\r') == '':
            qpylib.log('encDec : encrypt : Unable to encrypt an empty string aborting...')
            return False
        try:
            self.config[self.name]['secret'] = self.__encrypt_string(clear_text)
            self.__save()
            return self.config[self.name]['secret']

        except Exception, error:  # pylint: disable=W0703
            qpylib.log('encDec : encrypt : Failed to encrypt secret: {0}'.format(error))

            return str('')

    def decrypt(self):
        """ Decrypts a encrypted text"""
        try:
            if 'secret' not in self.config[self.name]:
                raise ValueError("Encryption : decrypt, no secret to decrypt")

            return self.__decrypt_string(self.config[self.name]['secret'])
			
        except Exception, error:  # pylint: disable=W0703
            if 'secret' in self.config[self.name]:
                secret=self.config[self.name]['secret']
            else:
                secret=''
            qpylib.log('encDec : decrypt : Failed to decrypt {0}: {1}'.format(secret,error))
			
            return str('')
