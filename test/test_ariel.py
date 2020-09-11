# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import os
import pytest
import responses
from qpylib.ariel import ArielSearch, ArielError

DUMMY_QUERY = 'select stuff from db'
SEARCH_ID = 'fa7a12c4-a3a7-425a-82b3-67d42c33860c'
ARIEL_URL = 'https://myhost.ibm.com/api/ariel/searches'
POST_SEARCH = '{0}?query_expression=select+stuff+from+db'.format(ARIEL_URL)
GET_SEARCH = '{0}/{1}'.format(ARIEL_URL, SEARCH_ID)
GET_RESULTS = '{0}/{1}/results'.format(ARIEL_URL, SEARCH_ID)
DELETE_SEARCH = '{0}/{1}'.format(ARIEL_URL, SEARCH_ID)
CANCEL_SEARCH = '{0}/{1}?status=CANCELLED'.format(ARIEL_URL, SEARCH_ID)

@pytest.fixture(scope='module', autouse=True)
def pre_testing_setup():
    os.environ['QRADAR_APPFW_SDK'] = 'true'
    os.environ['QRADAR_CONSOLE_FQDN'] = 'myhost.ibm.com'
    yield pre_testing_setup
    del os.environ['QRADAR_APPFW_SDK']
    del os.environ['QRADAR_CONSOLE_FQDN']

@responses.activate
def test_search_create_failure():
    responses.add('POST', POST_SEARCH, status=500,
                  json={'message': 'Search creation failed'})
    with pytest.raises(ArielError, match='Search creation failed'):
        ArielSearch().search(DUMMY_QUERY)

@responses.activate
def test_search_create_unexpected_response():
    responses.add('POST', POST_SEARCH, status=500,
                  body='Something bad happened')
    with pytest.raises(ArielError, match='Something bad happened'):
        ArielSearch().search(DUMMY_QUERY)

@responses.activate
def test_search_create_success():
    responses.add('POST', POST_SEARCH, status=201,
                  json={'status': 'WAIT', 'search_id': SEARCH_ID})
    status, search_id = ArielSearch().search(DUMMY_QUERY, api_version='12')
    assert status == 'WAIT'
    assert search_id == SEARCH_ID
    assert responses.calls[0].request.headers['Version'] == '12'

@responses.activate
def test_search_sync_create_failure():
    responses.add('POST', POST_SEARCH, status=500,
                  json={'message': 'Search creation failed'})
    with pytest.raises(ArielError, match='Search creation failed'):
        ArielSearch().search_sync(DUMMY_QUERY)

@responses.activate
def test_search_sync_status_failure():
    responses.add('POST', POST_SEARCH, status=201,
                  json={'status': 'WAIT', 'search_id': SEARCH_ID})
    responses.add('GET', GET_SEARCH, status=500, json={})
    with pytest.raises(ArielError, match='Ariel search {0} could not be retrieved'
                       .format(SEARCH_ID)):
        ArielSearch().search_sync(DUMMY_QUERY)

@responses.activate
def test_search_sync_timeout():
    responses.add('POST', POST_SEARCH, status=201,
                  json={'status': 'WAIT', 'search_id': SEARCH_ID})
    responses.add('GET', GET_SEARCH, status=200,
                  json={'status': 'WAIT', 'record_count': 0})
    with pytest.raises(ArielError, match='Ariel search {0} did not complete within {1}s'
                       .format(SEARCH_ID, 2)):
        ArielSearch().search_sync(DUMMY_QUERY, timeout=2, sleep_interval=2)

@responses.activate
def test_search_sync_error():
    responses.add('POST', POST_SEARCH, status=201,
                  json={'status': 'WAIT', 'search_id': SEARCH_ID})
    responses.add('GET', GET_SEARCH, status=200,
                  json={'status': 'ERROR', 'record_count': 0})
    with pytest.raises(ArielError, match='Ariel search {0} failed'.format(SEARCH_ID)):
        ArielSearch().search_sync(DUMMY_QUERY, timeout=0)

@responses.activate
def test_search_sync_cancelled():
    responses.add('POST', POST_SEARCH, status=201,
                  json={'status': 'WAIT', 'search_id': SEARCH_ID})
    responses.add('GET', GET_SEARCH, status=200,
                  json={'status': 'CANCELED', 'record_count': 0})
    with pytest.raises(ArielError, match='Ariel search {0} failed'.format(SEARCH_ID)):
        ArielSearch().search_sync(DUMMY_QUERY, timeout=0)

@responses.activate
def test_search_sync_completed():
    responses.add('POST', POST_SEARCH, status=201,
                  json={'status': 'WAIT', 'search_id': SEARCH_ID})
    responses.add('GET', GET_SEARCH, status=200,
                  json={'status': 'COMPLETED', 'record_count': 3})
    search_id, record_count = ArielSearch().search_sync(DUMMY_QUERY, timeout=0, api_version='14')
    assert search_id == SEARCH_ID
    assert record_count == 3
    assert responses.calls[0].request.headers['Version'] == '14'

@responses.activate
def test_status_failure():
    responses.add('GET', GET_SEARCH, status=500, json={})
    with pytest.raises(ArielError, match='Ariel search {0} could not be retrieved'
                       .format(SEARCH_ID)):
        ArielSearch().status(SEARCH_ID)

@responses.activate
def test_status_success():
    responses.add('GET', GET_SEARCH, status=200,
                  json={'status': 'COMPLETED', 'record_count': 3})
    status, record_count = ArielSearch().status(SEARCH_ID, api_version='15')
    assert status == 'COMPLETED'
    assert record_count == 3
    assert responses.calls[0].request.headers['Version'] == '15'

@responses.activate
def test_results_failure():
    responses.add('GET', GET_RESULTS, status=500, json={})
    with pytest.raises(ArielError, match='Results for Ariel search {0} could not be retrieved'
                       .format(SEARCH_ID)):
        ArielSearch().results(SEARCH_ID)

def test_results_bad_range_start():
    with pytest.raises(ValueError, match='Invalid range -1 to 3'):
        ArielSearch().results(SEARCH_ID, start=-1, end=3)

def test_results_range_end_before_start():
    with pytest.raises(ValueError, match='Invalid range 10 to 5'):
        ArielSearch().results(SEARCH_ID, start=10, end=5)

@responses.activate
def test_results_no_range():
    responses.add('GET', GET_RESULTS, status=200, json={'result0': 42})
    results_json = ArielSearch().results(SEARCH_ID)
    assert results_json['result0'] == 42
    assert 'Range' not in responses.calls[0].request.headers

@responses.activate
def test_results_range_end_only():
    responses.add('GET', GET_RESULTS, status=200, json={'result0': 42, 'result1': 99})
    results_json = ArielSearch().results(SEARCH_ID, end=1)
    assert results_json['result0'] == 42
    assert results_json['result1'] == 99
    assert responses.calls[0].request.headers['Range'] == 'items=0-1'

@responses.activate
def test_results_range_start_and_end():
    responses.add('GET', GET_RESULTS, status=200, json={'result3': 42, 'result4': 99})
    results_json = ArielSearch().results(SEARCH_ID, start=3, end=4)
    assert results_json['result3'] == 42
    assert results_json['result4'] == 99
    assert responses.calls[0].request.headers['Range'] == 'items=3-4'

@responses.activate
def test_search_delete_failure():
    responses.add('DELETE', DELETE_SEARCH, status=500)
    with pytest.raises(ArielError,
                       match='Ariel search {0} could not be deleted: HTTP 500 was returned'
                       .format(SEARCH_ID)):
        ArielSearch().delete(SEARCH_ID)

@responses.activate
def test_search_delete_success():
    responses.add('DELETE', DELETE_SEARCH, status=202, json={'status': 'COMPLETED'})
    assert ArielSearch().delete(SEARCH_ID) == 'COMPLETED'

@responses.activate
def test_search_cancel_failure():
    responses.add('POST', CANCEL_SEARCH, status=500)
    with pytest.raises(ArielError,
                       match='Ariel search {0} could not be cancelled: HTTP 500 was returned'
                       .format(SEARCH_ID)):
        ArielSearch().cancel(SEARCH_ID)

@responses.activate
def test_search_cancel_success():
    responses.add('POST', CANCEL_SEARCH, status=200, json={'status': 'COMPLETED'})
    assert ArielSearch().cancel(SEARCH_ID) == 'COMPLETED'
