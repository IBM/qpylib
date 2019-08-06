# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABCMeta, abstractmethod
from flask import url_for
import json
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler
import requests
import os
from . import asset_qpylib
from . import json_qpylib
from . import offense_qpylib

logger = 0
cached_manifest = None

class AbstractQpylib(object, metaclass=ABCMeta):
    LOGGER_NAME = 'com.ibm.applicationLogger'
    LOGFILE_LOCATION = '/store/log/app.log'
    APP_FILE_LOG_FORMAT = '%(asctime)s [%(module)s.%(funcName)s] [%(threadName)s] [%(levelname)s] - %(message)s'
    APP_CONSOLE_LOG_FORMAT = '%(asctime)s %(module)s.%(funcName)s: %(message)s'

    # ==== Logging ====

    def log(self, message, level='info'):
        log_fn = self._choose_log_fn(level)
        log_fn("[APP_ID/{0}][NOT:{1}] {2}".format(
            self.get_app_id(), self._map_notification_code(level), message))

    def create_log(self):
        global logger
        logger = logging.getLogger(self.LOGGER_NAME)
        self._add_log_handler(logger)

    def set_log_level(self, log_level='INFO'):
        global logger
        logger.setLevel(self._map_log_level(log_level))

    def _add_log_handler(self, loc_logger):
        loc_logger.setLevel(self._map_log_level(self._get_manifest_field_value('log_level', 'info')))

        handler = RotatingFileHandler(self.LOGFILE_LOCATION, maxBytes=2*1024*1024, backupCount=5)
        handler.setFormatter(logging.Formatter(self.APP_FILE_LOG_FORMAT))
        loc_logger.addHandler(handler)

        # Ipv6 address - Strip [] for syslog
        console_ip = self.get_console_address()
        if console_ip.startswith('[') and console_ip.endswith(']'):
            console_ip = console_ip[1:-1]

        syslogHandler = SysLogHandler(address=(console_ip, 514))
        syslogHandler.setFormatter(logging.Formatter(self.APP_CONSOLE_LOG_FORMAT))
        loc_logger.addHandler(syslogHandler)
        return

    def _choose_log_fn(self, level='INFO'):
        global logger
        if logger == 0:
            raise SystemError('You cannot use log before logging has been initialised')
        return {
            'INFO': logger.info,
            'DEBUG': logger.debug,
            'ERROR': logger.error,
            'WARNING': logger.warning,
            'CRITICAL': logger.critical,
            'EXCEPTION': logger.exception,
        }.get(level.upper(), logger.info)

    def _map_notification_code(self, log_level='INFO'):
        return {
            'INFO': "0000006000",
            'DEBUG': "0000006000",
            'ERROR': "0000003000",
            'WARNING': "0000004000",
            'CRITICAL': "0000003000",
        }.get(log_level.upper(), "0000006000")

    def _map_log_level(self, log_level='INFO'):
        return {
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'CRITICAL': logging.CRITICAL,
        }.get(log_level.upper(), logging.INFO)

    # ==== App details ====

    def get_app_id(self):
        return self._get_manifest_field_value('app_id', 0)

    def get_app_name(self):
        return self._get_manifest_field_value('name')

    def get_manifest_json(self):
        global cached_manifest
        if cached_manifest is None:
            full_manifest_location = self.get_root_path(self._get_manifest_location())
            with open(full_manifest_location) as manifest_file:
                cached_manifest = json.load(manifest_file)
        return cached_manifest

    def _get_manifest_location(self):
        return 'manifest.json'

    def _get_manifest_field_value(self, key, default_value=None):
        manifest = self.get_manifest_json()
        if key in manifest.keys():
            return manifest[key]
        if default_value is not None:
            return default_value
        raise KeyError('{0} is a required manifest field'.format(key))

    def get_store_path(self, relative_path):
        if relative_path == '':
            return self.get_root_path('store')
        return os.path.join(self.get_root_path('store'), relative_path)

    def get_root_path(self, relative_path):
        return os.path.join(self._root_path(), relative_path)

    def _root_path(self):
        return '/'

    @abstractmethod
    def get_app_base_url(self):
        pass

    def q_url_for(self, endpoint, **values):
        """
        Wraps the standard Flask url_for() method to include the proxied url
        through Qradar as a prefix to the Flask route name
        """
        url = self.get_app_base_url() + self._get_endpoint_url(endpoint, **values)
        self.log("q_url_for={0}".format(url), 'debug')
        return url

    def _get_endpoint_url(self, endpoint, **values):
        return url_for(endpoint, **values)

    def get_console_address(self):
        return self._get_manifest_field_value('console_ip', '127.0.0.1')

    # ==== REST ====

    @abstractmethod
    def REST(self, rest_type, request_url, headers=None, data=None,
             params=None, json_body=None, version=None, verify=None,
             timeout=60):
        pass

    def _chooseREST(self, rest_type):
        return {
            'GET': requests.get,
            'PUT': requests.put,
            'POST': requests.post,
            'DELETE': requests.delete,
        }.get(rest_type.upper(), self._unsupported_REST)

    def _unsupported_REST(self, *args, **kw_args):
        raise ValueError('Unsupported REST action was requested')

    # ==== JSON ====

    def to_json_dict(self, python_obj, classkey=None):
        """
        Helper function to convert a Python object into a dict
        usable with the JSON REST.
        Recursively converts fields which are also Python objects.
        @param python_obj: Python object to be converted into a dict
        @return dict object containing key:value pairs for the python
        objects fields. Useable with JSON REST.
        """
        if isinstance(python_obj, str):
            return python_obj
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

    def register_jsonld_type(self, context):
        if context is not None:
            jsonld_type = self._extract_type(context)
            self.log("register_jsonld_type {0}".format(str(jsonld_type)), "info")
            json_qpylib.register_jsonld_type(jsonld_type, context)

    def _extract_type(self, argument):
        type_id=None
        if '@context' in argument.keys():
            context=argument['@context']
            if '@type' in context.keys():
                type_id=context['@type']
            if type_id == '@id' and '@id' in context.keys():
                type_id=context['@id']
        return type_id

    def get_offense_rendering(self, offense_id, render_type):
        rendering_fn = self._choose_offense_rendering(render_type)
        return rendering_fn(offense_id)

    def _choose_offense_rendering(self, render_type):
        self.log('_choose_offense_rendering {0}'.format(str(render_type)), 'debug')
        return {
            'HTML': offense_qpylib.get_offense_json_html,
            'JSONLD': offense_qpylib.get_offense_json_ld,
        }.get(render_type.upper(), offense_qpylib.get_offense_json_html)

    def get_asset_rendering(self, asset_id, render_type):
        rendering_fn = self._choose_asset_rendering(render_type)
        return rendering_fn(asset_id)

    def _choose_asset_rendering(self, render_type):
        self.log('_choose_asset_rendering {0}'.format(str(render_type)), 'debug')
        return {
            'HTML': asset_qpylib.get_asset_json_html,
            'JSONLD': asset_qpylib.get_asset_json_ld,
        }.get(render_type.upper(), asset_qpylib.get_asset_json_html)

    def render_json_ld_type(self, jld_type, data, jld_id = None):
        return json_qpylib.render_json_ld_type(jld_type, data, jld_id)

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
                    jsonld_context = self._extract_jsonld_context(argument, 'request_mime_type', 'request_body_type')
                    self.register_jsonld_type(jsonld_context)
                if 'response' in endpoint.keys():
                    argument = endpoint['response']
                    jsonld_context = self._extract_jsonld_context(argument, 'mime_type', 'body_type')
                    self.register_jsonld_type(jsonld_context)

    def _extract_jsonld_context(self, argument, mime_id, context_id):
        if mime_id in argument.keys() and context_id in argument.keys():
            if argument[mime_id] == 'application/json+ld':
                return argument[context_id]
