import base64
from django.conf import settings
from django.utils import unittest
from django.test.client import RequestFactory
from django.test.utils import override_settings

from rest_framework import exceptions

from salmon.core.authentication import SettingsAuthentication


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        self.req_factory = RequestFactory()

    @override_settings(API_KEY='test')
    def test_valid_auth(self):
        http_auth = 'Basic {0}'.format(
            base64.encodestring(settings.API_KEY))
        request = self.req_factory.post('/api/v1/metric/', {},
                                        HTTP_AUTHORIZATION=http_auth)
        auth = SettingsAuthentication()
        auth_resp = auth.authenticate(request)
        self.assertFalse(auth_resp is None, "Authentication failed")

    @override_settings(API_KEY='test')
    def test_invalid_auth(self):
        http_auth = 'Basic {0}'.format(
            base64.encodestring('wrongkey'))
        request = self.req_factory.post('/api/v1/metric/', {},
                               HTTP_AUTHORIZATION=http_auth)
        auth = SettingsAuthentication()
        self.assertRaises(exceptions.AuthenticationFailed, auth.authenticate,
                          request)

    @override_settings(API_KEY='test')
    def test_no_auth(self):
        request = self.req_factory.post('/api/v1/metric/', {})
        auth = SettingsAuthentication()
        auth_resp = auth.authenticate(request)
        self.assertTrue(auth_resp is None, "Authentication succeeded")

