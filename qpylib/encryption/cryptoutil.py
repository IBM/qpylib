# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(key_material, salt, iterations=100000, length=32):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=length,
                     salt=salt,
                     iterations=iterations,
                     backend=default_backend())
    return kdf.derive(key_material)
