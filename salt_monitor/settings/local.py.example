"""
Example settings for local development

Use this file as a base for your local development settings and copy
it to {{ project_name }}/settings/local.py. It should not be checked into
your code repository.

"""
from {{ project_name }}.settings.base import *   # pylint: disable=W0614,W0401

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('You', 'your@email'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(VAR_ROOT, 'dev.db'),
    }
}

# ROOT_URLCONF = '{{ project_name }}.urls.local'
# WSGI_APPLICATION = '{{ project_name }}.wsgi.local.application'
