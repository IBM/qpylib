# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import time
from . import qpylib

class ArielError(Exception):
    ''' All Ariel errors are reported via this class.
          message: explanation of the error.
          aql: the AQL query, if applicable.
    '''
    def __init__(self, message, aql=None):
        super().__init__(message)
        self.message = message
        self.aql = aql

    def __str__(self):
        return self.message

class ArielSearch():
    ''' Convenience functions for executing Ariel searches using the QRadar REST API. '''

    SEARCHES_ENDPOINT = 'api/ariel/searches'
    SEARCH_ENDPOINT = SEARCHES_ENDPOINT + '/{0}'
    RESULTS_ENDPOINT = SEARCH_ENDPOINT + '/results'

    def search(self, query, api_version='latest'):
        ''' Initiates an asynchronous Ariel search.
              query: AQL query to execute.
              api_version: QRadar API version to use, defaults to latest.
            Returns a tuple containing search status and search ID.
            Raises ArielError if the search could not be created.
        '''
        response = qpylib.REST('POST', ArielSearch.SEARCHES_ENDPOINT,
                               headers=self._build_headers(api_version),
                               params={'query_expression': query})
        if response.status_code != 201:
            try:
                message = response.json()['message']
            except (ValueError, KeyError):
                message = response.text
            raise ArielError(message, aql=query)
        response_json = response.json()
        return (response_json['status'], response_json['search_id'])

    def search_sync(self, query, timeout=60, sleep_interval=10, api_version='latest'):
        ''' Initiates a synchronous Ariel search.
              query: AQL query to execute.
              timeout: number of seconds to wait for search to complete.
              sleep_interval: number of seconds to sleep before retrying status check.
              api_version: QRadar API version to use, defaults to latest.
            Returns a tuple containing search ID and record count.
            Raises ArielError if any of these occur:
              search could not be created.
              search was cancelled or resulted in an error.
              search did not complete within the timeout.
        '''
        response = self.search(query, api_version)
        end_time = time.time() + timeout
        search_id = response[1]

        while True:
            status, record_count = self.status(search_id, api_version)
            if status == 'COMPLETED':
                return (search_id, record_count)
            if status in ('CANCELED', 'ERROR'):
                raise ArielError('Ariel search {0} failed: {1}'.format(search_id, status),
                                 aql=query)
            if time.time() < end_time:
                time.sleep(sleep_interval)
                continue
            raise ArielError('Ariel search {0} did not complete within {1}s'
                             .format(search_id, timeout), aql=query)

    def status(self, search_id, api_version='latest'):
        ''' Retrieves status information for a search.
              search_id: Ariel search ID.
              api_version: QRadar API version to use, defaults to latest.
            Returns a tuple containing search status and record count.
            Raises ArielError if the status information could not be retrieved.
        '''
        response = qpylib.REST('GET', ArielSearch.SEARCH_ENDPOINT.format(search_id),
                               headers=self._build_headers(api_version))
        if response.status_code != 200:
            raise ArielError('Ariel search {0} could not be retrieved: {1}'
                             .format(search_id, response.content))
        response_json = response.json()
        return (response_json['status'], response_json['record_count'])

    def results(self, search_id, start=0, end=0, api_version='latest'):
        ''' Retrieves the results of an Ariel search.
              search_id: Ariel search ID.
              start, end: range of records to return.
              api_version: QRadar API version to use, defaults to latest.
            Raises ValueError if start/end range is not valid.
            Raises ArielError if results could not be retrieved.
        '''
        if (start < 0) or (start > end):
            raise ValueError('Invalid range {0} to {1}'.format(start, end))
        headers = self._build_headers(api_version)
        if start > 0 or end > 0:
            headers['Range'] = 'items={0}-{1}'.format(start, end)
        response = qpylib.REST('GET', ArielSearch.RESULTS_ENDPOINT.format(search_id),
                               headers=headers)
        if response.status_code != 200:
            raise ArielError('Results for Ariel search {0} could not be retrieved: {1}'
                             .format(search_id, response.content))
        return response.json()

    def delete(self, search_id, api_version='latest'):
        ''' Deletes a previous Ariel search.
              search_id: Ariel search ID
              api_version: QRadar API version to use, defaults to latest.
            Returns search status.
            Raises ArielError if the search could not be deleted.
        '''
        response = qpylib.REST('DELETE', ArielSearch.SEARCH_ENDPOINT.format(search_id),
                               headers=self._build_headers(api_version))
        if response.status_code != 202:
            raise ArielError('Ariel search {0} could not be deleted: HTTP {1} was returned'
                             .format(search_id, response.status_code))
        return response.json()['status']

    def cancel(self, search_id, api_version='latest'):
        ''' Cancels an ongoing Ariel search.
              search_id: Ariel search ID.
              api_version: QRadar API version to use, defaults to latest.
            Returns search status.
            Raises ArielError if the search could not be cancelled.
        '''
        response = qpylib.REST('POST', ArielSearch.SEARCH_ENDPOINT.format(search_id),
                               headers=self._build_headers(api_version),
                               params={'status': 'CANCELLED'})
        if response.status_code != 200:
            raise ArielError('Ariel search {0} could not be cancelled: HTTP {1} was returned'
                             .format(search_id, response.status_code))
        return response.json()['status']

    @staticmethod
    def _build_headers(api_version):
        headers = {'Accept': 'application/json'}
        if api_version != 'latest':
            headers['Version'] = api_version
        return headers
