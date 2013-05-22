from datetime import datetime, timedelta
from tempfile import mkdtemp
import os
import shutil

from django.test import TestCase

from .graph import WhisperDatabase

class WhisperDatabaseTest(TestCase):
    def setUp(self):
        self.tempdir = mkdtemp()
        self.wsp_db = WhisperDatabase(os.path.join(self.tempdir, "test.wsp"))

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_database_creation(self):
        """
        Tests that the whisper database get created if does not exist.
        """
        not_existing_wsp = "doesnotexist.wsp"
        path = os.path.join(self.tempdir, not_existing_wsp)
        self.assertEqual(os.path.exists(path), False)
        WhisperDatabase(path)
        self.assertEqual(os.path.exists(path), True)

    def test_database_update(self):
        self.wsp_db.update("25%")
        now = datetime.now()

        timeinfo, results = self.wsp_db.fetch(now-timedelta(minutes=5), now)
        self.assertEqual(results, [25])
