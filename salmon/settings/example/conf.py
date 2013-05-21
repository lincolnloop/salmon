import os
SECRET_KEY = "{default_key}"

SALMON_CHECKS_PATH = os.path.expanduser('~/.salmon/checks.yaml')

# ==============================================================
# whisper
# ==============================================================
XFILEFACTOR = 0.5
AGGREGATION_METHOD = "average"
ARCHIVES = "30s:8"
