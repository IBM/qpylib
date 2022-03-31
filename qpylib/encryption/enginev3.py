# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from binascii import a2b_hex
from Crypto.Cipher import AES
from Crypto.Protocol import KDF
from Crypto.Util.Padding import unpad

class Enginev3():
    ''' Enginev3 uses a modified version of Enginev2's AES/CFB encryption.
    '''
    # pylint: disable=duplicate-code
    def __init__(self, config, app_uuid):
        ''' config should contain the following fields:
            salt, UUID, ivz, iterations.
        '''
        self.version = 3
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
        decrypted_bytes = unpad(aes.decrypt(encrypted_bytes), AES.block_size)
        return decrypted_bytes.decode('utf-8')

    def _derive_key(self):
        return KDF.PBKDF2(self.app_uuid + self.config['UUID'],
                          self.config['salt'].encode('utf-8'),
                          dkLen=32,
                          count=self.config['iterations'])
