import os
SECRET_KEY = "{default_key}"

SALMON_URL = "{site_url}"

# https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
# from urlparse import urlparse
# ALLOWED_HOSTS = [urlparse(SALMON_URL).hostname]

# work-around for https://github.com/saltstack/salt/issues/4454
SALT_COMMAND = '/usr/bin/python /usr/bin/salt {{args}}'
# Execute against a remote master over SSH:
# SALT_COMMAND = 'ssh salt-master.example.com "sudo su - salmon  -s /bin/bash -c \'salt {{args}} \'\"'

SALMON_CHECKS_PATH = os.path.expanduser('~/.salmon/checks.yaml')
SALMON_WHISPER_DB_PATH = os.path.expanduser('~/.salmon/whisper')

# ==============================================================
# whisper
# ==============================================================
XFILEFACTOR = 0.5
AGGREGATION_METHOD = "average"
ARCHIVES = "5m:1d,30m:7d,1d:1y"


# ==============================================================
# email
# ==============================================================
# ALERT_EMAILS is a list of emails, they are notified for each
# `result.failed` unless specified otherwise in the checks.yaml
ALERT_EMAILS = None

