import os
SECRET_KEY = "{secret_key}"

SALMON_URL = "{site_url}"

API_KEY = "{api_key}"

# https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
# from urlparse import urlparse
# ALLOWED_HOSTS = [urlparse(SALMON_URL).hostname]

SALMON_WHISPER_DB_PATH = os.path.expanduser('~/.salmon/whisper')

# ==============================================================
# whisper
# ==============================================================
XFILEFACTOR = 0.5
AGGREGATION_METHOD = "average"
ARCHIVES = "5m:1d,30m:7d,1d:1y"

