# -*- coding: utf-8 -*-

import hashlib

from mock import patch, call
from nose.tools import assert_is_not_none, eq_

from pylcp import mac


class TestGenerateExt(object):
    def test_content_type_and_body_none_is_zero_length_ext(self):
        content_type = None
        body = None
        ext = mac.generate_ext(content_type, body)
        assert_is_not_none(ext)
        eq_(ext, "")

    def test_content_type_and_body_zero_length_is_zero_length_ext(self):
        content_type = ''
        body = ''
        ext = mac.generate_ext(content_type, body)
        assert_is_not_none(ext)
        eq_(ext, "")

    def test_content_type_non_none_and_body_none_is_zero_length_ext(self):
        content_type = "dave was here"
        body = None
        ext = mac.generate_ext(content_type, body)
        assert_is_not_none(ext)
        eq_(ext, "")

    def test_content_type_none_and_body_non_none_is_zero_length_ext(self):
        content_type = None
        body = "dave was here"
        ext = mac.generate_ext(content_type, body)
        assert_is_not_none(ext)
        eq_(ext, "")

    @patch('pylcp.mac.hashlib.sha1')
    def test_content_type_and_body_non_none_returns_sha1_of_both(self, mock_sha1):
        content_type = "hello world!"
        body = "dave was here"
        ext = mac.generate_ext(content_type, body)
        eq_(ext, mock_sha1.return_value.hexdigest.return_value)
        eq_(mock_sha1.call_args_list, [call(content_type + body)])

    @patch('pylcp.mac.hashlib.sha1')
    def test_unicode_content_type_and_body_returns_sha1_of_both(self, mock_sha1):
        content_type = u"\u4f60\u597d\u4e16\u754c"
        body = u"\u6234\u592b\u5728\u8fd9\u91cc"
        ext = mac.generate_ext(content_type, body)
        eq_(ext, mock_sha1.return_value.hexdigest.return_value)
        eq_(mock_sha1.call_args_list, [call((content_type + body).encode('utf-8'))])


class TestBuildNormalizedRequestString(object):
    def test_generate_concatenates_request_elements_as_per_rfc(self):
        # This is the example from the RFC:
        # http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.2.1
        actual = mac.build_normalized_request_string(
            '264095',
            '7d8f3e4a',
            'POST',
            'example.com',
            80,
            '/request?b5=%3D%253D&a3=a&c%40=&a2=r%20b&c2&a3=2+q',
            'a,b,c')
        expected = '''264095
7d8f3e4a
POST
/request?b5=%3D%253D&a3=a&c%40=&a2=r%20b&c2&a3=2+q
example.com
80
a,b,c
'''
        eq_(expected, actual)


class TestGenerateNonce(object):
    @patch('pylcp.mac.base64.b64encode')
    @patch('pylcp.mac.os.urandom')
    def test_returns_b64_encoded_random_string(self, mock_urandom, mock_b64encode):
        eq_(mock_b64encode.return_value, mac.generate_nonce())
        eq_(mock_b64encode.call_args_list, [
            call(mock_urandom.return_value)])
        eq_(mock_urandom.call_args_list, [call(8)])


class TestGenerateSignature(object):
    @patch('pylcp.mac.base64.b64decode')
    @patch('pylcp.mac.base64.b64encode')
    @patch('pylcp.mac.hmac.new')
    def test_returns_signature(self, hmac_new_mock, b64encode_mock, b64decode_mock):
        b64decode_mock.return_value = 'test_key'
        eq_(mac.generate_signature('test_key', 'test_nrs'), b64encode_mock.return_value)
        eq_(b64encode_mock.call_args_list, [call(hmac_new_mock.return_value.digest.return_value)])
        eq_(hmac_new_mock.call_args, call('test_key', 'test_nrs', hashlib.sha1))


class TestGenerateAuthorizationHeaderValue(object):
    def setup(self):
        self.mock_time = patch('pylcp.mac.time.time').start()
        self.mock_generate_nonce = patch('pylcp.mac.generate_nonce').start()
        self.mock_generate_ext = patch('pylcp.mac.generate_ext').start()
        self.mock_build_normalized_request_string = patch(
            'pylcp.mac.build_normalized_request_string').start()
        self.mock_generate_signature = patch('pylcp.mac.generate_signature').start()
        self.mock_time.return_value = 42
        self.mock_generate_nonce.return_value = 'NONCE'
        self.mock_generate_ext.return_value = 'EXT'
        self.mock_generate_signature.return_value = 'SIGNATURE'

    def teardown(self):
        patch.stopall()

    def test_returns_authorization_header_as_per_rfc(self):
        # http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.1
        retval = mac.generate_authorization_header_value(
            'METHOD', 'http://HOST:8008/PATH', 'KEY_ID', 'SECRET', 'CONTENT_TYPE',
            'BODY')
        eq_(
            retval, 'MAC id="KEY_ID", ts="42", nonce="NONCE", ext="EXT", mac="SIGNATURE"')

    def test_calls_all_dependencies(self):
        mac.generate_authorization_header_value(
            'METHOD', 'http://HOST:8008/PATH', 'KEY_ID', 'SECRET', 'CONTENT_TYPE', 'BODY')
        eq_(self.mock_time.call_args_list, [call()])
        eq_(self.mock_generate_nonce.call_args_list, [call()])
        eq_(self.mock_generate_ext.call_args_list, [
            call('CONTENT_TYPE', 'BODY')])
        eq_(self.mock_generate_signature.call_args_list, [
            call('SECRET', self.mock_build_normalized_request_string.return_value)])

    def test_defaults_to_http_port_for_http_scheme(self):
        mac.generate_authorization_header_value(
            'METHOD', 'http://HOST/PATH', 'KEY_ID', 'SECRET', 'CONTENT_TYPE', 'BODY')
        eq_(
            [call(
                str(self.mock_time.return_value),
                self.mock_generate_nonce.return_value,
                'METHOD',
                'host',
                '80',
                '/PATH',
                self.mock_generate_ext.return_value
            )],
            self.mock_build_normalized_request_string.call_args_list
        )

    def test_defaults_to_https_port_for_https_scheme(self):
        mac.generate_authorization_header_value(
            'METHOD', 'https://HOST/PATH', 'KEY_ID', 'SECRET', 'CONTENT_TYPE', 'BODY')
        eq_(
            [call(
                str(self.mock_time.return_value),
                self.mock_generate_nonce.return_value,
                'METHOD',
                'host',
                '443',
                '/PATH',
                self.mock_generate_ext.return_value
            )],
            self.mock_build_normalized_request_string.call_args_list
        )


class TestAuthHeaderValue(object):
    def _create_ahv_str(
            self, mac_key_identifier='FAKE_ID', ts='42', nonce='FAKE_NONCE',
            ext='FAKE_EXT', mac='FAKE_MAC'):
        fmt = 'MAC id="%s", ts="%s", nonce="%s", ext="%s", mac="%s"'
        return fmt % (mac_key_identifier, ts, nonce, ext, mac)

    def test_string_representation_include_all_parameters_as_per_rfc(self):
        actual = '%s' % mac.AuthHeaderValue('FAKE_ID', '42', 'FAKE_NONCE', 'FAKE_EXT', 'FAKE_MAC')
        eq_(self._create_ahv_str(), actual)
