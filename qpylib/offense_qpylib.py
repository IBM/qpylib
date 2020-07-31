# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from . import app_qpylib
from . import json_qpylib
# pylint: disable=cyclic-import
from . import qpylib

# Context location yet to be finalised
JSON_LD_CONTEXT = 'https://qradar/context/location'
OFFENSE_HEADER_TEMPLATE = ('<div class="gridHeader" id="{0}gridheaderdiv" style="clear:both;">'
                           '<div class="heading" id="{0}headingdiv">{1}</div>'
                           '</div>')
OFFENSE_ROW_TEMPLATE = '<tr><td>{0}</td><td>{1}</td></tr>'

def get_offense_url(offense_id):
    return 'api/siem/offenses/{0}'.format(offense_id)

def get_offense_url_full(offense_id):
    return 'https://{0}/{1}'.format(app_qpylib.get_console_fqdn(), get_offense_url(offense_id))

def get_offense_json(offense_id):
    response = qpylib.REST('get', get_offense_url(offense_id))
    if response.status_code != 200:
        raise ValueError('Could not retrieve offense with id {0}'.format(offense_id))
    return response.json()

def get_offense_rendering(offense_id, render_type):
    rendering_fn = _choose_offense_rendering(render_type)
    return rendering_fn(offense_id)

def _choose_offense_rendering(render_type):
    return {
        'HTML': get_offense_json_html,
        'JSONLD': get_offense_json_ld,
    }.get(render_type.upper(), get_offense_json_html)

def get_offense_json_ld(offense_id):
    offense_json = get_offense_json(offense_id)
    return json_qpylib.json_ld(JSON_LD_CONTEXT,
                               get_offense_url_full(offense_id),
                               'offense',
                               'Offense details',
                               'Offense details for id ' + str(offense_id),
                               offense_json)

def get_offense_json_html(offense_id, generate_html=None, generate_heading=True):
    offense_html = ''
    if generate_heading:
        offense_html = get_offense_html_header(offense_id)
    offense_json = get_offense_json(offense_id)
    if generate_html is None:
        offense_html += get_offense_html_example(offense_json)
    else:
        offense_html += generate_html(offense_json)
    offense_html += '<br/>'
    return json_qpylib.json_html(offense_html)

def get_offense_html_example(offense_json):
    return ('<table><tbody>' +
            OFFENSE_ROW_TEMPLATE.format('Offense ID', str(offense_json['id'])) +
            OFFENSE_ROW_TEMPLATE.format('Source IP', offense_json['offense_source']) +
            OFFENSE_ROW_TEMPLATE.format('Severity', str(offense_json['severity'])) +
            '</tbody></table>')

def get_offense_html_header(offense_id):
    return OFFENSE_HEADER_TEMPLATE.format(offense_id, app_qpylib.get_app_name())
