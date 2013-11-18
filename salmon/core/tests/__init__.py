from tempfile import mkdtemp
import shutil

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings


@override_settings(SALMON_WHISPER_DB_PATH=mkdtemp())
class BaseTestCase(TestCase):

    def tearDown(self):
        try:
            shutil.rmtree(settings.SALMON_WHISPER_DB_PATH)
        except OSError:
            pass
