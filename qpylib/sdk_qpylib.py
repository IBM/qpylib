# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from .abstract_qpylib import AbstractQpylib
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import getpass
import json
import os
import requests
import socket
import ssl
import sys
import unicodedata
from OpenSSL.crypto import dump_certificate, FILETYPE_PEM
from OpenSSL.SSL import (Context, Connection)
from OpenSSL.SSL import SSLv23_METHOD

api_auth_user = 0
api_auth_password = 0
consoleIP = 0

class SdkQpylib(AbstractQpylib):
    DEV_AUTH_FILE = ".qradar_appfw.auth"
    DEV_CONSOLE_FILE = ".qradar_appfw.console"
    CONSOLE_CERT_FILE = ".qradar_appfw.console_cert.{0}.pem"
    YES_OPTIONS = ("y", "yes")
    VAULT_PORT = 9381
    ROOT_PEM_URL = 'http://{0}:{1}/vault-qrd_ca.pem'
    INTERMEDIATE_PEM_URL = 'http://{0}:{1}/vault-qrd_ca_int.pem'

    # ==== App details ====

    def get_app_base_url(self):
        return "http://localhost:5000"

    def get_console_address(self):
        global consoleIP
        home = os.path.expanduser("~")
        console_file_path = os.path.join(home, self.DEV_CONSOLE_FILE)
        if os.path.isfile(console_file_path):
            print("Loading console details from file: {0}".format(str(console_file_path)))
            sys.stdout.flush()
            with open(console_file_path) as consolefile:
                console_json = json.load(consolefile)
            consoleIP = console_json["console"]
        else:
            if consoleIP == 0:
                console_data = {}
                print("What is the IP of QRadar console required to make this API call:")
                sys.stdout.flush()
                consoleIP = input()
                console_data['console'] = consoleIP
                print("Do you want to store the console IP at {0}?".format(console_file_path))
                print("[y/n]:")
                sys.stdout.flush()
                do_store = input()
                if do_store in self.YES_OPTIONS:
                    with open(console_file_path, 'w+') as console_file:
                        json.dump(console_data, console_file)
        return consoleIP

    # ==== REST ====

    def REST(self, rest_type, request_url, headers=None, data=None, params=None,
             json_body=None, version=None, verify=None, timeout=60):
        if headers is None:
            headers={}
        if version is not None:
            headers['Version'] = version
        auth = self._get_api_auth()
        consoleAddress = self.get_console_address()
        fullURL = "https://" + str(consoleAddress) + "/" + str(request_url)
        rest_func = self._chooseREST(rest_type)
        if not isinstance(verify, str):
            verify = self._get_cert_filepath(consoleAddress)
        return rest_func(fullURL, headers=headers, data=data, auth=auth, params=params,
                         json=json_body, timeout=timeout, verify=verify)

    def _get_api_auth(self):
        auth = None
        global api_auth_user
        global api_auth_password
        home = os.path.expanduser("~")
        auth_file_path = os.path.join(home, self.DEV_AUTH_FILE)
        if os.path.isfile(auth_file_path):
            print("Loading user details from file: {0}".format(auth_file_path))
            sys.stdout.flush()
            with open(auth_file_path) as authfile:
                auth_json = json.load(authfile)
                auth = (auth_json["user"], auth_json["password"])
        else:
            auth_data = {}
            consoleAddress = self.get_console_address()
            print("QRadar credentials for {0} are required to make this API call".format(consoleAddress))
            if api_auth_user == 0:
                print("User:")
                sys.stdout.flush()
                api_auth_user = input()
            if api_auth_password == 0:
                api_auth_password = getpass.getpass("Password:")
                auth_data['user'] = api_auth_user
                auth_data['password'] = api_auth_password
                print("Store credentials credentials at: {0}".format(auth_file_path))
                print("WARNING: credentials will be stored in clear.")
                print("[y/n]:")
                sys.stdout.flush()
                do_store = input()
                if do_store in self.YES_OPTIONS:
                    with open(auth_file_path, 'w+') as auth_file:
                        json.dump(auth_data, auth_file)
            auth = (api_auth_user, api_auth_password)
        print("Using Auth: " + str(auth))
        return auth

    def _get_cert_filepath(self, host):
        console_cert_file_path = os.path.join(os.path.expanduser("~"), self.CONSOLE_CERT_FILE.format(host))

        if os.path.isfile(console_cert_file_path + ".ignore"):
            return False

        if os.path.isfile(console_cert_file_path):
            try:
                with open(console_cert_file_path) as pem_file:
                    pem_text = pem_file.read()
                    x509.load_pem_x509_certificate(pem_text.encode(), default_backend())
                print("Using console cert from file: {0}".format(str(console_cert_file_path)))
                sys.stdout.flush()
                return console_cert_file_path

            except ValueError:
                print("Removing invalid console cert file {0}".format(str(console_cert_file_path)))
                sys.stdout.flush()
                os.remove(console_cert_file_path)

        self._store_cert_from_server(host, console_cert_file_path)
        return console_cert_file_path

    # If unable to connect to server, this function raises a socket error.
    def _store_cert_from_server(self, host, console_cert_file_path):
        # Try to get the root and intermediate certs introduced in 7.3.2.
        # If that fails fall back to the pre-7.3.2 cert.
        use_pre_732_cert = False
        try:
            pem_data = requests.get(url = self.ROOT_PEM_URL.format(host, self.VAULT_PORT)).text
            pem_text = self._normalize_pem_data(pem_data)
            intermediate_pem_data = requests.get(url = self.INTERMEDIATE_PEM_URL.format(host, self.VAULT_PORT)).text
            intermediate_pem_text = self._normalize_pem_data(intermediate_pem_data)
        except requests.ConnectionError:
            use_pre_732_cert = True
            pem_data = ssl.get_server_certificate((host, 443))
            pem_text = self._normalize_pem_data(pem_data)
            
        print('')
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('Server {0} is unknown, do you want to trust it?'.format(host))
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('')
        self._display_pem_cert_details(pem_text)
        print("Do you trust this certificate [y/n]: ")
        sys.stdout.flush()

        do_store = input().strip().lower()
        if do_store not in self.YES_OPTIONS:
            print("Not storing cert file for {0}. Aborting request.".format(host))
            sys.stdout.flush()
            raise ValueError("Certificate was rejected")

        print("Storing cert file to {0}".format(console_cert_file_path))
        sys.stdout.flush()

        if use_pre_732_cert:
            with open(console_cert_file_path, 'w') as cert_file:
                self._dump_all_certs(cert_file, host)
        else:
            with open(console_cert_file_path, "a") as cert_file:
                cert_file.write(pem_text.decode())
                cert_file.write(intermediate_pem_text.decode())

    def _dump_all_certs(self, cert_file, address):
        # This will also include intermediate certs
        context = Context(SSLv23_METHOD)
        context.set_default_verify_paths()
        client = socket.socket()
        client.connect((address, 443))
        clientSSL = Connection(context, client)
        clientSSL.set_connect_state()
        clientSSL.do_handshake()
        chains = clientSSL.get_peer_cert_chain()
        for chain in chains:
            cert_file.write(dump_certificate(FILETYPE_PEM, chain).decode())

    _name_fields = [
        'OID_COMMON_NAME',
        'OID_COUNTRY_NAME',
        'OID_DOMAIN_COMPONENT',
        'OID_DN_QUALIFIER',
        'OID_EMAIL_ADDRESS',
        'OID_GENERATION_QUALIFIER',
        'OID_GIVEN_NAME',
        'OID_LOCALITY_NAME',
        'OID_ORGANIZATIONAL_UNIT_NAME',
        'OID_ORGANIZATION_NAME',
        'OID_PSEUDONYM',
        'OID_SERIAL_NUMBER',
        'OID_STATE_OR_PROVINCE_NAME',
        'OID_SURNAME',
        'OID_TITLE'
    ]

    def _display_pem_cert_details(self, pem_text):
        pem_cert = x509.load_pem_x509_certificate(pem_text, default_backend())
        print('********************')
        print('Certificate details:')
        print('********************')
        print('Version: {}'.format(pem_cert.version))
        print('SHA-256 Fingerprint:', end=' ')
        print(':'.join(format(b, '02x') for b in pem_cert.fingerprint(hashes.SHA256())))
        print('SHA-1 Fingerprint:', end=' ')
        print(':'.join(format(b, '02x') for b in pem_cert.fingerprint(hashes.SHA1())))
        print('Serial Number: {}'.format(pem_cert.serial_number))
        print('Not valid before: {}'.format(pem_cert.not_valid_before))
        print('Not valid after: {}'.format(pem_cert.not_valid_after))
        print('Signature Hash Algorithm: {}'.format(pem_cert.signature_algorithm_oid._name))

        print('Issuer:')
        for attr in self._name_fields:
            oid = getattr(x509, attr.upper())
            issuer = pem_cert.issuer
            info = issuer.get_attributes_for_oid(oid)
            if (info):
                print("    {}: {}".format(attr, info[0].value))

        print('Subject:')
        for attr in self._name_fields:
            oid = getattr(x509, attr.upper())
            subject = pem_cert.subject
            info = subject.get_attributes_for_oid(oid)
            if (info):
                print("    {}: {}".format(attr, info[0].value))

        for ext in pem_cert.extensions:
            try:
                print('Extension: Name :', ext.oid._name)
                print('    Critical :', ext.critical)
                print('    Value :', ext.value)
            except UnicodeEncodeError:
                pass

        print('Signature:\n   ', end=' ')
        print(":".join(format(b, '02x') for b in pem_cert.signature))
        print('TBS Cert Signature:\n   ', end=' ')
        print(":".join(format(b, '02x') for b in pem_cert.tbs_certificate_bytes))
        print('')

    def _normalize_pem_data(self, pem_data):
        return unicodedata.normalize('NFKD', pem_data).encode('ascii', 'ignore')
