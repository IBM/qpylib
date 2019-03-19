# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

__author__ = 'IBM'

import os.path
import sys
import json
import re
from flask import Flask
from flask import send_from_directory, render_template, request
from qpylib import qpylib

app = Flask(__name__)
# Create log here to prevent race condition when importing views
qpylib.create_log()

try:
    qpylib.register_jsonld_endpoints()
except AttributeError:
    qpylib.log("Application's qpylib directory has been detected as outdated. Please consider updating to the latest version.", level='warn')

from app import views

@app.after_request
def obscure_server_header(resp):
    resp.headers['Server'] = 'QRadar App {0}'.format(qpylib.get_app_id())
    return resp

@app.route('/debug')
def debug():
    return 'Pong!'

@app.route('/resources/<path:filename>')
def send_file(filename):
    qpylib.log(" >>> route resources >>>")
    qpylib.log(" filename=" + filename)
    qpylib.log(" app.static_folder=" + app.static_folder)
    qpylib.log(" full file path =" + app.static_folder + '/resources/'+filename )
    return send_from_directory(app.static_folder, 'resources/'+filename)

@app.route('/log_level', methods=['POST'])
def log_level():
    level = request.form['level'].upper()
    levels = ['INFO', 'DEBUG', 'ERROR', 'WARNING', 'CRITICAL']

    if any( level in s for s in levels):
        qpylib.set_log_level(request.form['level'])
    else:
        return 'level parameter missing or unsupported - ' + str (levels), 42
    return 'log level set to ' + level

#Untested or compiled code
@app.route('/react-intl/<path:requested>', methods=['GET'])
def reactIntl(requested):
    def put_in_container( container, key, value ):
        key_parts = key.split(".")

        s = len(key_parts)
        l = 0

        while s > 1:
            part = key_parts[l]

            if not part in container:
                container[part] = {}

            container = container[part]
            s = s-1
            l = l+1

        container[key_parts[l]] = value

    resources = os.path.dirname( os.path.abspath( sys.argv[0] ) ) + "/app/static/resources"

    requested_language = None
    requested_locale = None

    lang_locale = re.compile("[_\\-]").split(requested)

    if len(lang_locale) == 2:
        requested_language = lang_locale[0]
        requested_locale = lang_locale[1]
    else:
        requested_language = requested
        requested_locale = None

    qpylib.log("Requested language {0}, locale {1}".format(requested_language,requested_locale), "DEBUG")

    result = { "locales":[], "messages":{} }
    for f in os.listdir(resources):
        bundle_lang = f.split("_")

        # This will be either application_<lang>.properties, in which case we have 2 parts, or application_<lang>_<locale>.properties, which is 3 parts
        locale = None
        if len(bundle_lang) == 2:
            language = bundle_lang[1].split(".")[0]
        else:
            language = bundle_lang[1]
            locale = bundle_lang[2].split(".")[0]

        qpylib.log("Bundle {0} language {1}, locale {2}".format(f,language,locale), "DEBUG")

        if language == requested_language:
            filepath = os.path.join( resources, f )

            if os.path.isfile(filepath):
                with open(filepath) as thefile:

                    lang = {}

                    for line in thefile:
                        line = line.strip()
                        if len(line) > 0:
                            key_value = line.split("=")
                            put_in_container( lang, key_value[0].strip(), key_value[1].decode('unicode-escape') )

                    if locale is None:
                        result["locales"].append( language )
                    else:
                        result["locales"].append( language + "_" + locale )

                    result["messages"].update(lang)

    return json.dumps(result)

#register the new q_url_for() method for use with Jinja2 templates
app.add_template_global(qpylib.q_url_for, 'q_url_for')
