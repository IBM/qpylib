# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABCMeta, abstractmethod
from flask import url_for
import json
import logging
import requests
import os
from . import asset_qpylib
from . import json_qpylib
from . import offense_qpylib

LOGGER_NAME = 'com.ibm.applicationLogger'
logger = 0
cached_manifest = None

class AbstractQpylib(object, metaclass=ABCMeta):
    @abstractmethod
    def get_app_id(self):
        pass

    @abstractmethod
    def get_app_name(self):
        pass

    @abstractmethod
    def get_manifest_location(self):
        pass

    def get_manifest_json(self):
        global cached_manifest
        if cached_manifest is None:
            full_manifest_location = os.path.join(self.root_path(), self.get_manifest_location())
            with open(full_manifest_location) as manifest_file:
                cached_manifest = json.load(manifest_file)
        return cached_manifest

    def is_manifest_oauth(self):
        manifest = self.get_manifest_json()
        return 'authentication' in manifest.keys()

    def RESTget(self, URL, headers, data=None,
                params=None, json_inst=None, auth=None,
                timeout=60, verify=None):
        self.log("REST get issued to {0} {1}".format(URL, str(params)), "debug")
        return requests.get(URL, params=params,
                            headers=headers, verify=verify, auth=auth,
                            data=data, json=json_inst, timeout=timeout)

    def RESTput(self, URL, headers, data=None,
                params=None, json_inst=None, auth=None,
                timeout=60, verify=None):
        self.log("REST put issued to {0} {1}".format(URL, str(params)), "debug")
        return requests.put(URL, params=params,
                            headers=headers, verify=verify, auth=auth,
                            data=data, json=json_inst, timeout=timeout)

    def RESTpost(self, URL, headers, data=None,
                 params=None, json_inst=None, auth=None,
                 timeout=60, verify=None):
        self.log("REST post issued to {0} {1}".format(URL, str(params)), "debug")
        return requests.post(URL, params=params,
                             headers=headers, verify=verify, auth=auth,
                             data=data, json=json_inst, timeout=timeout)

    def RESTdelete(self, URL, headers, data=None,
                   params=None, json_inst=None, auth=None,
                   timeout=None, verify=None):
        self.log("REST delete issued to {0} {1}".format(URL, str(params)), "debug")
        return requests.delete(URL, params=params,
                               headers=headers, verify=verify, auth=auth,
                               data=data, json=json_inst, timeout=timeout)

    def RESTunsupported(self, URL, headers, data=None,
                        params=None, json_inst=None, auth=None,
                        verify=None, timeout=0):
        self.log("REST unsupported issued to {0} {1}".format(URL, str(params)), "debug")
        raise ValueError('The supplied REST type is not supported')

    def chooseREST(self, RESTtype):
        RESTtype = RESTtype.upper()
        return {
            'GET': self.RESTget,
            'PUT': self.RESTput,
            'POST': self.RESTpost,
            'DELETE': self.RESTdelete,
        }.get(RESTtype, self.RESTunsupported)

    @abstractmethod
    def REST(self, RESTtype, requestURL, headers=None, data=None,
             params=None, json_inst=None, version=None, verify=None,
             timeout=60):
        pass

    def choose_log_level(self, level='INFO'):
        if logger == 0:
            raise SystemError('You cannot call log before logging has been initialised')

        level = level.upper()
        return {
            'INFO': logger.info,
            'DEBUG': logger.debug,
            'ERROR': logger.error,
            'WARNING': logger.warning,
            'CRITICAL': logger.critical,
            'EXCEPTION': logger.exception,
        }.get(level, logger.info)

    def map_log_level(self, log_level='INFO'):
        log_level = log_level.upper()
        return {
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'CRITICAL': logging.CRITICAL,
        }.get(log_level, logging.INFO)

    @abstractmethod
    def add_log_handler(self, loc_logger):
        pass

    def create_log(self):
        global logger
        global LOGGER_NAME
        logger = logging.getLogger(LOGGER_NAME)
        self.add_log_handler(logger)
        self.log("Created log {0}".format(LOGGER_NAME), 'info')

    def set_log_level(self, log_level='INFO'):
        logger.setLevel(self.map_log_level(log_level))

    def log(self, message, level='info'):
        log_fn = self.choose_log_level(level)
        log_fn("127.0.0.1 [APP_ID/{0}][NOT:{1}] {2}".format(
            self.get_app_id(), self.map_notification_code(level), message))

    @abstractmethod
    def get_console_address(self):
        pass

    @abstractmethod
    def root_path(self):
        pass

    def get_root_path(self,relative_path):
        return os.path.join(self.root_path(), relative_path)

    def store_path(self):
        return os.path.join(self.root_path(), 'store')

    def get_store_path(self, relative_path):
        return os.path.join(self.store_path(), relative_path)

    @abstractmethod
    def get_cert_filepath(self, host):
        pass

    def to_json_dict(self, python_obj, classkey=None):
        """
        Helper function to convert a Python object into a dict
        usable with the JSON REST.
        Recursively converts fields which are also Python objects.
        @param python_obj: Python object to be converted into a dict
        @return dict object containing key:value pairs for the python
        objects fields. Useable with JSON REST.
        """
        if isinstance(python_obj, dict):
            data = {}
            for (k, v) in list(python_obj.items()):
                data[k] = self.to_json_dict(v, classkey)
            return data
        elif hasattr(python_obj, "_ast"):
            return self.to_json_dict(python_obj._ast())
        elif hasattr(python_obj, "__iter__"):
            return [self.to_json_dict(v, classkey) for v in python_obj]
        elif hasattr(python_obj, "__dict__"):
            data = dict([(key, self.to_json_dict(value, classkey))
                         for key, value in python_obj.__dict__.items()
                         if not callable(value) and not key.startswith('_')])
            if classkey is not None and hasattr(python_obj, "__class__"):
                data[classkey] = python_obj.__class__.__name__
            return data
        else:
            return python_obj

    @abstractmethod
    def get_app_base_url(self):
        pass

    def q_url_for(self, endpoint, **values):
        """
        Create a method to wrap the standard Flask url_for())method,
        to include the proxied url through Qradar as a prefix to the
        short-name Flask route name
        """
        url = self.get_app_base_url() + url_for(endpoint, **values)
        self.log("q_url_for={0}".format(url), 'debug')
        return url

    def map_notification_code(self, log_level='INFO'):
        log_level = log_level.upper()
        return {
            'INFO': "0000006000",
            'DEBUG': "0000006000",
            'ERROR': "0000003000",
            'WARNING': "0000004000",
            'CRITICAL': "0000003000",
        }.get(log_level, "0000006000")

    def register_jsonld_type(self, context):
        if context is not None:
            jsonld_type = self.extract_type(context)
            self.log("register_jsonld_type {0}".format(str(jsonld_type)), "info")
            json_qpylib.register_jsonld_type(jsonld_type, context)

    def get_jsonld_type(self, jsonld_type):
        self.log("get_jsonld_type {0}".format(str(jsonld_type)), "debug")
        return json_qpylib.get_jsonld_type(jsonld_type)

    def choose_offense_rendering(self, render_type):
        render_type_upper = render_type.upper()
        self.log('choose_offense_rendering {0}'.format(str(render_type_upper)), 'debug')
        return {
            'HTML': offense_qpylib.get_offense_json_html,
            'JSONLD': offense_qpylib.get_offense_json_ld,
        }.get(render_type_upper, offense_qpylib.get_offense_json_html)

    def get_offense_rendering(self, offense_id, render_type):
        rendering_fn = self.choose_offense_rendering(render_type)
        return rendering_fn(offense_id)

    def choose_asset_rendering(self, render_type):
        render_type_upper = render_type.upper()
        self.log('choose_asset_rendering {0}'.format(str(render_type_upper)), 'debug')
        return {
            'HTML': asset_qpylib.get_asset_json_html,
            'JSONLD': asset_qpylib.get_asset_json_ld,
        }.get(render_type_upper, asset_qpylib.get_asset_json_html)

    def get_asset_rendering(self, asset_id, render_type):
        rendering_fn = self.choose_asset_rendering(render_type)
        return rendering_fn(asset_id)

    def extract_jsonld_context(self, argument, mime_id, context_id):
        if mime_id in argument.keys() and context_id in argument.keys():
            if argument[mime_id] == 'application/json+ld':
                return argument[context_id]

    def extract_type(self, argument):
        type_id=None
        if '@context' in argument.keys():
            context=argument['@context']
            if '@type' in context.keys():
                type_id=context['@type']
            if type_id == '@id' and '@id' in context.keys():
                type_id=context['@id']
        return type_id

    def register_jsonld_endpoints(self):
        manifest = self.get_manifest_json()
        services=None
        endpoints=None
        if 'services' in manifest.keys():
            services=manifest['services']

        if services is not None:
            for service in services:
                if 'endpoints' in service.keys():
                    endpoints=service['endpoints']

        if endpoints is not None:
            for endpoint in endpoints:
                jsonld_context = None
                if 'request_mime_type' in endpoint.keys():
                    argument=endpoint
                    jsonld_context = self.extract_jsonld_context(argument, 'request_mime_type', 'request_body_type')
                    self.register_jsonld_type(jsonld_context)
                if 'response' in endpoint.keys():
                    argument = endpoint['response']
                    jsonld_context = self.extract_jsonld_context(argument, 'mime_type', 'body_type')
                    self.register_jsonld_type(jsonld_context)

    def render_json_ld_type(self, jld_type, data, jld_id = None):
        return json_qpylib.render_json_ld_type(jld_type, data, jld_id)

