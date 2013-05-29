import os
SECRET_KEY = "{default_key}"

# https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
# ALLOWED_HOSTS = ["salmon.example.com"]

ALERT_EMAIL = None

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
