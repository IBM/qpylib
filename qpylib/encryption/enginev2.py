# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from binascii import a2b_hex
from Crypto.Cipher import AES
from Crypto.Protocol import KDF

class Enginev2():
    ''' Enginev2 is derived from the Encryption class as contained in the
        older qpylib package which was distributed with
          - QRadarAppSDK v1.1.0 and
          - the app base image (CentOS) in 7.3.2+.
        The code has been converted from Python 2 to Python 3.
        The most significant changes in the Python 2 to 3 conversion were the
        addition of encode/decode calls to convert between string and bytes values.
        Also, Crypto packages now come from pycryptodome, not pycrypto.
        Enginev2 uses AES/CFB encryption.
    '''
    # pylint: disable=duplicate-code
    def __init__(self, config, app_uuid):
        ''' config should contain the following fields:
            salt, UUID, ivz, iterations.
        '''
        self.version = 2
        self.config = config
        self.app_uuid = app_uuid

    def decrypt(self):
        aes = AES.new(
            self._derive_key(),
            AES.MODE_CFB,
            self.config['ivz'].encode('utf-8'),
            segment_size=128)
        encrypted_hex_bytes = self.config['secret'].encode('utf-8')
        encrypted_bytes = a2b_hex(encrypted_hex_bytes)
        decrypted_bytes = aes.decrypt(encrypted_bytes)
        clear_text_padded_string = decrypted_bytes.decode('utf-8')
        return self._unpad_string(clear_text_padded_string)

    def _derive_key(self):
        return KDF.PBKDF2(self.app_uuid + self.config['UUID'],
                          self.config['salt'].encode('utf-8'),
                          dkLen=16,
                          count=self.config['iterations'])

    @staticmethod
    def _unpad_string(value):
        while value[-1] == '\x00':
            value = value[:-1]
        return value
