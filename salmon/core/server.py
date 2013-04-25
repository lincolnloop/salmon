from django.core.management import call_command
from django.conf import settings


# Borrowed liberally from Sentry
# https://github.com/getsentry/sentry/blob/3cc971a843efcab317f8acac0a98f1851e8f838d/src/sentry/services/http.py
class SalmonHTTPServer(object):

    def __init__(self, host=None, port=None, debug=False, workers=None):

        self.host = host or settings.WEB_HOST
        self.port = port or settings.WEB_PORT
        self.workers = workers

        options = (settings.WEB_OPTIONS or {}).copy()
        options['debug'] = debug
        options.setdefault('bind', '%s:%s' % (self.host, self.port))
        options.setdefault('daemon', False)
        options.setdefault('timeout', 30)
        options.setdefault('proc_name', 'Salmon')
        if workers:
            options['workers'] = workers

        self.options = options

    def run(self):
        call_command('run_gunicorn', **self.options)
