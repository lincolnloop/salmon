from tempfile import mkdtemp
import os
import shutil

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from salmon.core import graph


@override_settings(SALMON_WHISPER_DB_PATH=mkdtemp())
class WhisperDatabaseTest(TestCase):

    def tearDown(self):
        shutil.rmtree(settings.SALMON_WHISPER_DB_PATH)

    def test_database_creation(self):
        """
        Tests that the whisper database get created if does not exist.
        """
        not_existing_wsp = "doesnotexist.wsp"
        path = os.path.join(settings.SALMON_WHISPER_DB_PATH, not_existing_wsp)
        self.assertEqual(os.path.exists(path), False)
        graph.WhisperDatabase(path)
        self.assertEqual(os.path.exists(path), True)
