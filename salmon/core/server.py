import os
import subprocess
from django.conf import settings


# Borrowed liberally from Sentry
# https://github.com/getsentry/sentry/blob/3cc971a843efcab317f8acac0a98f1851e8f838d/src/sentry/services/http.py
class SalmonHTTPServer(object):

    def __init__(self, host=None, port=None, debug=False, workers=None):

        self.host = host or settings.WEB_HOST
        self.port = port or settings.WEB_PORT
        self.workers = workers

        options = settings.WEB_OPTIONS or {}
        gunicorn_args = [
            '--bind={0}:{1}'.format(self.host, self.port),
            '--timeout={0}'.format(options.get('timeout', 30)),
            '--name={0}'.format(options.get('name', 'Salmon')),
        ]

        for bool_arg in ['debug', 'daemon']:
            if options.get(bool_arg):
                gunicorn_args.append('--{0}'.format(options[bool_arg]))

        if workers:
            '--workers={0}'.format(workers)

        self.gunicorn_args = gunicorn_args

    def run(self):
        command = [os.path.join(settings.PYTHON_BIN, 'gunicorn'),
                   'salmon.wsgi:application']
        subprocess.call(command + self.gunicorn_args)
