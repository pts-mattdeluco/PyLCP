from nose.tools import eq_
from requests import adapters, models


class MockRequestAdapter(adapters.BaseAdapter):
    """
    A requests Transport Adapter which echo the request instead of making actual
    HTTP calls.

    Provides methods for asserting various properties of the request.
    """
    def __init__(self, *args, **kwargs):
        self.last_request = None
        self.last_request_kwargs = None

    def send(self, request, **kwargs):
        self.last_request = request
        self.last_request_kwargs = kwargs

        response = models.Response()
        response.request = request
        response.connection = self
        response.status_code = 200
        response.reason = 'OK'
        response.headers = {
            'Content-Type': 'application/json',
            'location': request.url,
        }
        response._content = bytes(request.body)
        return response

    def close(self):
        pass  # no connection to close

    def assert_request_properties(self, **expected_properties):
        for property_name, expected_value in expected_properties.items():
            actual_value = getattr(self.last_request, property_name)
            message = '{} did not match. Expected: {}, actual: {}'.format(property_name, expected_value, actual_value)
            eq_(actual_value, expected_value, message)

    def assert_headers_present(self, expected_headers):
        for header_name, expected_value in expected_headers.items():
            actual_value = self.last_request.headers.get(header_name)
            message = 'Header {} did not match. Expected: {}, actual: {}'.format(
                header_name,
                expected_value,
                actual_value,
            )
            eq_(actual_value, expected_value, message)
