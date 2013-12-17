import os

from django.conf import settings

from salmon.core import graph
from salmon.core.tests import BaseTestCase


class WhisperDatabaseTest(BaseTestCase):

    def test_database_creation(self):
        """
        Tests that the whisper database get created if does not exist.
        """
        not_existing_wsp = "doesnotexist.wsp"
        path = os.path.join(settings.SALMON_WHISPER_DB_PATH, not_existing_wsp)
        self.assertEqual(os.path.exists(path), False)
        graph.WhisperDatabase(path)
        self.assertEqual(os.path.exists(path), True)
