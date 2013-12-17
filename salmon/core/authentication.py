import base64
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.utils.crypto import constant_time_compare
from rest_framework import authentication
from rest_framework import exceptions

class SettingsAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        has_api_key = hasattr(settings, 'API_KEY')
        using_basic_auth = 'HTTP_AUTHORIZATION' in request.META
        if using_basic_auth and has_api_key:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2 and auth[0].lower() == "basic":
                key = base64.b64decode(auth[1]).split(':')[0]
                if constant_time_compare(settings.API_KEY, key):
                    request._salmon_allowed = True
                    return (AnonymousUser, None)
                else:
                    raise exceptions.AuthenticationFailed('No such user')
        return None


