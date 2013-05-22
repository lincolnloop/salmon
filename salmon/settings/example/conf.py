import os
SECRET_KEY = "{default_key}"

SALMON_CHECKS_PATH = os.path.expanduser('~/.salmon/checks.yaml')
SALMON_WHISPER_DB_PATH = os.path.expanduser('~/.salmon/whisper')

# ==============================================================
# whisper
# ==============================================================
XFILEFACTOR = 0.5
AGGREGATION_METHOD = "average"
ARCHIVES = "5m:1d,30m:7d,1d:1y"
