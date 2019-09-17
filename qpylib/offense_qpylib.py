# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from . import qpylib
from . import json_qpylib

# Context location yet to be finalised
JSON_LD_CONTEXT = 'http://qradar/context/location'

def get_offense_url(offense_id):
    return 'api/siem/offenses/{0}'.format(offense_id)

def get_offense_url_full(offense_id):
    return 'https://{0}/{1}'.format(qpylib.get_console_fqdn(), get_offense_url(offense_id))

def get_offense_json(offense_id):
    response = qpylib.REST('get', get_offense_url(offense_id))
    if response.status_code != 200:
        raise ValueError('Could not retrieve offense with id {0}'.format(offense_id))
    return response.json()

def get_offense_html_example(offense_json):
    return ('<table><tbody>' +
            '<tr><td>Offense ID</td><td>' + str(offense_json['id']) + '</td></tr>' +
            '<tr><td>Source IP</td><td>' + offense_json['offense_source'] + '</td></tr>' +
            '<tr><td>Severity</td><td>' + str(offense_json['severity']) + '</td></tr>' +
            '</tbody></table>')

def get_offense_html_header(offense_id):
    html_header = '<div class="gridHeader" id="' + offense_id + 'gridheaderdiv" style="clear:both;">'
    html_header += '<div class="heading" id="' + offense_id + 'headingdiv">' + qpylib.get_app_name() + '</div>'
    html_header += '</div>'
    return html_header

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

def get_offense_json_html(offense_id, generate_html = None, generate_heading = True):
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
