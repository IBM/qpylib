# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from .abstract_qpylib import AbstractQpylib

class SdkQpylib(AbstractQpylib):

    # ==== App details ====

    def get_app_base_url(self):
        return "http://localhost:5000"

    # ==== REST ====

    def REST(self, rest_type, request_url, headers=None, data=None, params=None,
             json_body=None, version=None, verify=None, timeout=60):
        if headers is None:
            headers={}
        if version is not None:
            headers['Version'] = version
        consoleAddress = self.get_console_address()
        fullURL = "https://" + str(consoleAddress) + "/" + str(request_url)
        rest_func = self._chooseREST(rest_type)
        if not isinstance(verify, str):
            # To be completed
            #verify = self._get_cert_filepath(consoleAddress)
            verify = False
        return rest_func(fullURL, headers=headers, data=data, params=params,
                         json=json_body, timeout=timeout, verify=verify)
