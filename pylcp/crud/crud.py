"""Loyalty domain objects for LCP services

The domain objects derived from LCPResource can be used for basic CRUD
operations to support internal services.

"""
import httplib

import requests
import simplejson as json


class LCPResource(object):
    """Base class for loyalty domain objects for LCP services

    When defining new domain objects, overrides of __init__ and create must call
    the superclass implementations to ensure that the common id and url properties
    are correctly initialized.
    """
    def __init__(self, response=None):
        self.json = None
        self.response = response
        self._url = None

        if response is not None:
            if response.status_code != httplib.NO_CONTENT:
                self.json = response.json()
                try:
                    self._url = self._self_link()
                except KeyError:
                    pass
            if 'location' in response.headers:
                self._url = response.headers['location']

    @property
    def id(self):
        """The resource ID which is the part of the URL that uniquely identifies the resource"""
        return self.url.split('/')[-1]

    @property
    def url(self):
        return self._url

    def _self_link(self):
        return self.json['links']['self']['href']

    def __getitem__(self, key):
        return self.json[key]

    def __setitem__(self, key, value):
        self.json[key] = value


class LCP(object):

    """Cruds are responsible for translating CRUD operations into http
    requests (method, url-path, querystring, payload) and interpreting http
    responses (success vs failure).
    :param http_client: Must be of be a subclass of requests.Session

    """

    def __init__(self, http_client):
        self.http_client = http_client

    @property
    def resource_class(self):
        return LCPResource

    def create(self, url, payload):
        return self._resource_from_http('post', url, payload)

    def read(self, url):
        return self._resource_from_http('get', url)

    def update(self, url, payload):
        return self._resource_from_http('put', url, payload)

    def delete(self, url):
        return self._resource_from_http('delete', url)

    def search(self, url, params=None):
        return self._resource_from_http('get', url, params=params)

    def _resource_from_http(self, method, url, payload=None, params=None):
        response = None

        try:
            response = self._http_method(method)(url, data=payload, params=params)
            response.raise_for_status()
        except requests.RequestException:
            raise CRUDError(url, method, response, payload, params)
        return self.resource_class(response)

    def _http_method(self, method):
        return getattr(self.http_client, method.lower())


class CRUDError(Exception):
    def __init__(self, cls, url, operation, response, request_payload=None, request_parameters=None):
        formatted_payload = self._format_dictionary('Request', request_payload)
        formatted_parameters = self._format_dictionary('Request Parameters', request_parameters)

        super(CRUDError, self).__init__(
            "{cls} returned {status_code}.\n"
            "Operation: {operation}\n"
            "Correlation ID: {cid}\n"
            "URL: {url}\n"
            "{formatted_parameters}"
            "{formatted_payload}"
            "Response: {response}".format(
                cls=cls.__name__,
                url=url,
                formatted_parameters=formatted_parameters,
                operation=operation,
                status_code=response.status_code,
                cid=response.headers.get('pts-lcp-cid', 'none'),
                formatted_payload=formatted_payload,
                response=response.text,
            ))

    def _format_dictionary(self, label, dict_to_format):
        formatted_dictionary = ''
        if dict_to_format is not None:
            formatted_dictionary = '{}: {}\n'.format(label, json.dumps(dict_to_format, indent=2, sort_keys=True))
        return formatted_dictionary
