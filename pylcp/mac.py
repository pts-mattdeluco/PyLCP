from urlparse import urlparse
import base64
import hashlib
import logging
import os
import re
import time

import keyczar.keys
import requests


logger = logging.getLogger(__name__)


def request(method, url, **kwargs):

    if 'mac_key_identifier' in kwargs and 'mac_key' in kwargs:
        parsed_url = urlparse(url)
        auth_header = generate_authorization_header_value(method,
                                                          parsed_url.hostname,
                                                          parsed_url.port,
                                                          parsed_url.path,
                                                          kwargs['mac_key_identifier'],
                                                          kwargs['mac_key'],
                                                          kwargs.get('headers')['Content-Type'],
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


"""To help prevent reply attacks the timestamp of all requests can
be no older than ```TIMESTAMP_MAX_SECONDS``` seconds before the current
timestamp.  Also, because clocks can be out of sync we allow the timestamp to be
up to ```TIMESTAMP_MAX_SECONDS``` in the future."""
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

    if content_type is not None and body is not None:
        content_type_plus_body = content_type + body
        content_type_plus_body_hash = hashlib.sha1(content_type_plus_body)
        ext = content_type_plus_body_hash.hexdigest()
    else:
        ext = ""
    return ext


def build_normalized_request_string(ts, nonce, http_method, host, port, request_path, ext):
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
    """ Determine if the request signature is valid i.e. it was signed with a valid shared secret """
    # TODO - ensure that the keymode (sandbox or prod) matches the Host appropriately.

    if not keyczar.keys.HmacKey(shared_secret).Verify(
            normalized_request_string, keyczar.util.Base64WSDecode(mac_sign)):
        raise InvalidSignature


def generate_authorization_header_value(
        http_method,
        host,
        port,
        request_path,
        mac_key_identifier,
        mac_key,
        content_type,
        body):

    ts = str(int(time.time()))
    nonce = generate_nonce()
    ext = generate_ext(content_type, body)
    normalized_request_string = build_normalized_request_string(
        ts,
        nonce,
        http_method,
        host,
        port,
        request_path,
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

    def __init__(self, mac_key_identifier, ts, nonce, ext, mac):
        self.mac_key_identifier = mac_key_identifier
        self.ts = ts
        self.nonce = nonce
        self.ext = ext
        self.mac = mac

    def __str__(self):
        fmt = 'MAC id="%s", ts="%s", nonce="%s", ext="%s", mac="%s"'
        rv = fmt % (
            self.mac_key_identifier,
            self.ts,
            self.nonce,
            self.ext,
            self.mac)
        return rv

    @classmethod
    def parse(cls, value):
        """Parse a string which is the value from an HTTP authorization
        header. If parsing is successful create and return a AuthHeaderValue
        otherwise raises InvalidAuthHeader"""

        reg_ex_pattern = (
            '^\s*'
            'MAC\s+'
            'id\s*\=\s*"(?P<mac_key_identifier>[^"]+)"\s*\,\s*'
            'ts\s*\=\s*"(?P<ts>[^"]+)"\s*\,\s*'
            'nonce\s*\=\s*"(?P<nonce>[^"]+)"\s*\,\s*'
            'ext\s*\=\s*"(?P<ext>[^"]*)"\s*\,\s*'
            'mac\s*\=\s*"(?P<mac>[^"]+)"\s*'
            '$'
        )
        reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
        match = value and reg_ex.match(value)
        if not match:
            logger.warning(
                "Invalid format for authorization header '%s'",
                value)
            raise InvalidAuthHeader()
        logger.info(
            "Valid format for authorization header '%s'",
            value)

        assert 0 == match.start()
        assert len(value) == match.end()
        assert 5 == len(match.groups())

        mac_key_identifier = match.group("mac_key_identifier")
        assert mac_key_identifier
        assert 0 < len(mac_key_identifier)

        ts = match.group("ts")
        assert ts
        assert 0 < len(ts)

        nonce = match.group("nonce")
        assert nonce
        assert 0 < len(nonce)

        ext = match.group("ext")
        assert ext is not None
        assert 0 <= len(ext)

        mac = match.group("mac")
        assert mac
        assert 0 < len(mac)

        return cls(mac_key_identifier, ts, nonce, ext, mac)
