import json
import logging
import copy

import requests


from pylcp.mac import generate_authorization_header_value
import pylcp.url


logger = logging.getLogger(__name__)
request_logger = logging.getLogger(__name__ + '.request')
response_logger = logging.getLogger(__name__ + '.response')


def format_headers(headers):
    return '\n'.join(
        "{}: {}".format(k, v) for k, v in headers.items())


def prettify_alleged_json(text):
    try:
        return json.dumps(json.loads(text), sort_keys=True, indent=2)
    except:
        return text


def mask_credit_card_number(credit_card_number):
    if credit_card_number is None:
        return None

    credit_card_number = str(credit_card_number)

    return "X" * (len(credit_card_number) - 4) + credit_card_number[-4:]


def mask_sensitive_data(data):

    if not data:
        return
    if isinstance(data, basestring):
        try:
            data = json.loads(data)
        except ValueError:
            return data
        return json.dumps(mask_sensitive_data(data))

    copied_data = copy.deepcopy(data)
    if 'billingInfo' in copied_data:
        if 'cardNumber' in copied_data['billingInfo']:
            card_number = copied_data['billingInfo']['cardNumber']
            copied_data['billingInfo']['cardNumber'] = mask_credit_card_number(card_number)
        if 'securityCode' in copied_data['billingInfo']:
            copied_data['billingInfo']['securityCode'] = 'XXX'
    if 'password' in copied_data:
        copied_data['password'] = 'XXX'
    return copied_data


class Client(object):

    def __init__(self, base_url, key_id=None, shared_secret=None):
        self.key_id = key_id
        self.shared_secret = shared_secret
        self.base_url = base_url

    def post(self, url, **kwargs):
        kwargs.setdefault('headers', {'Content-Type': 'application/json'})
        return self.request('POST', url, **kwargs)

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def options(self, url, **kwargs):
        return self.request('OPTIONS', url, **kwargs)

    def put(self, url, **kwargs):
        kwargs.setdefault('headers', {'Content-Type': 'application/json'})
        return self.request('PUT', url, **kwargs)

    def patch(self, url, **kwargs):
        kwargs.setdefault('headers', {'Content-Type': 'application/json'})
        return self.request('PATCH', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

    def request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        if not url.startswith('http'):
            url = pylcp.url.url_path_join(self.base_url, url)
        if self.key_id:
            kwargs['headers']['Authorization'] = \
                generate_authorization_header_value(
                    method,
                    url,
                    self.key_id,
                    self.shared_secret,
                    kwargs['headers'].get('Content-Type', ''),
                    kwargs.get('data', '')
                )
        request_logger.debug(
            '------------------------------------------------------------\n'
            '%(method)s %(url)s HTTP/1.1\n%(headers)s\n\n%(body)s',
            {
                'method': method,
                'url': url,
                'headers': format_headers(kwargs.get('headers', {})),
                'body': prettify_alleged_json(mask_sensitive_data(kwargs.get('data', '')))})
        response = requests.request(method, url, **kwargs)
        response_logger.debug(
            '------------------------------------------------------------\n'
            'HTTP/1.1 %(status_code)d %(reason)s\n%(headers)s\n\n%(body)s',
            {
                'status_code': response.status_code,
                'reason': response.reason,
                'headers': format_headers(response.headers),
                'body': prettify_alleged_json(response.text)})
        return response
