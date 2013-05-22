from datetime import datetime, timedelta
from tempfile import mkdtemp
import os
import shutil
from random import randint

from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase


from .graph import WhisperDatabase
from .models import Minion, Check, Result


POINT_NUMBERS= 1000
INTERVAL_MIN=5

@override_settings(SALMON_WHISPER_DB_PATH=mkdtemp())
class BaseTestCase(TestCase):
    def setUp(self):
        self.minion = Minion.objects.create(name="minion.local")
        self.check = Check.objects.create(target="*",
                                          function="ps.virtual_memory_usage",
                                          name="Memory Usage",
                                          active=True)
        self.populate_results(POINT_NUMBERS, INTERVAL_MIN)

    def tearDown(self):
        shutil.rmtree(settings.SALMON_WHISPER_DB_PATH)

    def populate_results(self, point_numbers, interval):
        now = datetime.now()
        for i in range(point_numbers):
            Result.objects.create(check=self.check,
                                  minion=self.minion,
                                  timestamp=now-timedelta(minutes=interval),
                                  result=str(randint(1, 100)),
                                  result_type="float",
                                  failed=False)


class WhisperDatabaseTest(BaseTestCase):

    def test_database_creation(self):
        """
        Tests that the whisper database get created if does not exist.
        """
        not_existing_wsp = "doesnotexist.wsp"
        path = os.path.join(settings.SALMON_WHISPER_DB_PATH, not_existing_wsp)
        self.assertEqual(os.path.exists(path), False)
        WhisperDatabase(path)
        self.assertEqual(os.path.exists(path), True)

    def test_database_update(self):
        now = datetime.now()
        result = Result.objects.create(check=self.check,
                                       minion=self.minion,
                                       timestamp=now,
                                       result="101",
                                       result_type="float",
                                       failed=False)
        history = result.get_history(now-timedelta(minutes=INTERVAL_MIN*20))
        self.assertEqual(len(history), 20)


class MonitorUrlTest(BaseTestCase):

    def test_dashboard_get(self):
        url = reverse("dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_history_get(self):
        url = self.minion.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["graphs"]), 1)
