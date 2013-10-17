import base64
import hashlib
import httplib
import logging
import os
import re
import time
import urlparse

import keyczar.keys
import requests


logger = logging.getLogger(__name__)


def request(method, url, **kwargs):

    if 'mac_key_identifier' in kwargs and 'mac_key' in kwargs:
        auth_header = generate_authorization_header_value(
            method,
            url,
            kwargs['mac_key_identifier'],
            kwargs['mac_key'],
            kwargs.get('headers', {}).get('Content-Type', ''),
            kwargs.get('data', '')
        )

        kwargs.pop('mac_key_identifier')
        kwargs.pop('mac_key')

        kwargs['headers']['Authorization'] = auth_header

    return requests.request(method, url, **kwargs)


def delete(url, **kwargs):
    return request('DELETE', url, **kwargs)


def get(url, **kwargs):
    return request('GET', url, **kwargs)


def head(url, **kwargs):
    return request('HEAD', url, **kwargs)


def patch(url, **kwargs):
    return request('PATCH', url, **kwargs)


def post(url, **kwargs):
    return request('POST', url, **kwargs)


def put(url, **kwargs):
    return request('PUT', url, **kwargs)


# To help prevent reply attacks the timestamp of all requests can
# be no older than ```TIMESTAMP_MAX_SECONDS``` seconds before the current
# timestamp.  Also, because clocks can be out of sync we allow the timestamp to
# be up to ```TIMESTAMP_MAX_SECONDS``` in the future.
TIMESTAMP_MAX_SECONDS = 30


class VerificationFailure(Exception):
    """Base class for all possible signature verification failure exception."""


class InvalidAuthHeader(VerificationFailure):
    """The authorization header value invalid."""


class InvalidTimeStamp(VerificationFailure):
    """The timestamp is too old or too far in the future."""


class InvalidSignature(VerificationFailure):
    """The signature does not match."""


def generate_ext(content_type, body):
    """Implements the notion of the ext as described in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.1"""

    if (
            content_type is not None and
            body is not None and
            len(content_type) > 0 and
            len(body) > 0):
        content_type_plus_body = content_type + body
        content_type_plus_body_hash = hashlib.sha1(content_type_plus_body)
        ext = content_type_plus_body_hash.hexdigest()
    else:
        ext = ""
    return ext


def build_normalized_request_string(
        ts, nonce, http_method, host, port, request_path, ext):
    """Implements the notion of a normalized request string as described in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.2.1"""

    normalized_request_string = \
        ts + '\n' + \
        nonce + '\n' + \
        http_method + '\n' + \
        request_path + '\n' + \
        host + '\n' + \
        str(port) + '\n' + \
        ext + '\n'
    return normalized_request_string


def generate_nonce():
    """Generates a random string intend for use as a nonce when computing an
    HMAC."""
    return base64.b64encode(os.urandom(8))


def generate_signature(mac_key, normalized_request_string):
    """Generate a request's MAC given a normalized request string (aka
    a summary of the key elements of the request and the mac key (shared
    secret)."""
    return base64.b64encode(
        keyczar.keys.HmacKey(mac_key).Sign(normalized_request_string))


def verify_signature(mac_sign, shared_secret, normalized_request_string):
    """Determine if the request signature is valid i.e. it was signed with a
    valid shared secret"""
    # TODO - ensure that the keymode (sandbox or live) matches the Host
    # appropriately.

    if not keyczar.keys.HmacKey(shared_secret).Verify(
            normalized_request_string, keyczar.util.Base64WSDecode(mac_sign)):
        raise InvalidSignature


def generate_authorization_header_value(
        http_method,
        url,
        mac_key_identifier,
        mac_key,
        content_type,
        body):
    url_parts = urlparse.urlparse(url)
    port = url_parts.port
    if not port:
        if url_parts.scheme == 'https':
            port = str(httplib.HTTPS_PORT)
        else:
            port = str(httplib.HTTP_PORT)
    ts = str(int(time.time()))
    nonce = generate_nonce()
    ext = generate_ext(content_type, body)
    normalized_request_string = build_normalized_request_string(
        ts,
        nonce,
        http_method,
        url_parts.hostname,
        port,
        url_parts.path,
        ext)

    signature = generate_signature(mac_key, normalized_request_string)

    return 'MAC id="%s", ts="%s", nonce="%s", ext="%s", mac="%s"' % (
        mac_key_identifier,
        ts,
        nonce,
        ext,
        signature)


def verify_timestamp(ts):
    now = time.time()
    age = int(now) - int(ts)
    if age > TIMESTAMP_MAX_SECONDS:
        logger.warning("Rejecting timestamp %ss in the past.", age)
        raise InvalidTimeStamp()
    if (-age) > TIMESTAMP_MAX_SECONDS:
        logger.warning("Rejecting timestamp %ss in the future.", -age)
        raise InvalidTimeStamp()
    if age < 0:
        logger.info("Accepting timestamp %ss in the future.", -age)


class AuthHeaderValue(object):
    """As per http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02 create
    the value for the HTTP Authorization header using an existing hmac."""

    auth_header_re = re.compile(
        '^\s*'
        'MAC\s+'
        'id\s*=\s*"(?P<mac_key_identifier>[^"]+)"\s*\,\s*'
        'ts\s*=\s*"(?P<ts>[^"]+)"\s*\,\s*'
        'nonce\s*=\s*"(?P<nonce>[^"]+)"\s*\,\s*'
        'ext\s*=\s*"(?P<ext>[^"]*)"\s*\,\s*'
        'mac\s*=\s*"(?P<mac>[^"]+)"\s*'
        '$',
        re.IGNORECASE
    )

    def __init__(self, mac_key_identifier, ts, nonce, ext, mac):
        self.mac_key_identifier = mac_key_identifier
        self.ts = ts
        self.nonce = nonce
        self.ext = ext
        self.mac = mac

    def __str__(self):
        return (
            'MAC id="{self.mac_key_identifier}", ts="{self.ts}", '
            'nonce="{self.nonce}", ext="{self.ext}", mac="{self.mac}"'
        ).format(self=self)

    @classmethod
    def parse(cls, value):
        """Parse a string which is the value from an HTTP authorization
        header. If parsing is successful create and return a AuthHeaderValue
        otherwise raises InvalidAuthHeader"""

        match = None
        if isinstance(value, basestring):
            match = cls.auth_header_re.match(value)

        if not match:
            logger.warning(
                "Invalid format for authorization header %r",
                value)
            raise InvalidAuthHeader()
        logger.info(
            "Valid format for authorization header %r",
            value)

        values = match.groupdict()
        return cls(**values)
