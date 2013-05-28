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
from .utils import get_latest_results

POINT_NUMBERS = 50
INTERVAL_MIN = 5


def generate_sample_data(point_numbers, interval):
    """
    This method generate sample data and populate the databases

        :point_numbers: is an int that defines the number of results
        :interval: is an int that defines the interval between each results

    This method returns a tuple (minion, active_check, not_active_check)
    """
    minion, created = Minion.objects.get_or_create(name="minion.local")
    checks = []

    check, created = Check.objects.get_or_create(
        target="*",
        function="ps.virtual_memory_usage",
        name="Memory Usage",
        active=True)
    checks.append(check)

    check, created = Check.objects.get_or_create(
        target="*",
        function="disk.usage",
        name="Disk usage (not active)",
        active=False)
    checks.append(check)

    now = datetime.now()
    for i in range(point_numbers):
        for check in checks:
            Result.objects.create(
                check=check,
                minion=minion,
                timestamp=now-timedelta(minutes=interval*i),
                result=str(randint(1, 100)),
                result_type="float",
                failed=False)

    return (minion, checks[0], checks[1])


@override_settings(SALMON_WHISPER_DB_PATH=mkdtemp())
class BaseTestCase(TestCase):
    def setUp(self):
        self.minion, self.active_check, self.not_active_check = (
            generate_sample_data(POINT_NUMBERS, INTERVAL_MIN))

    def tearDown(self):
        shutil.rmtree(settings.SALMON_WHISPER_DB_PATH)


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
        result = Result.objects.create(check=self.active_check,
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


class MonitorUtilsTest(BaseTestCase):
    def test_get_latest_results_for_all_minions(self):
        latest_results = get_latest_results()
        self.assertEqual(
            [(r.minion.name, r.check.name) for r in latest_results],
            [(u'minion.local', u'Memory Usage')])

    def test_get_latest_results_a_minion(self):
        latest_results = get_latest_results(minion=self.minion)
        self.assertEqual(
            [(r.minion.name, r.check.name) for r in latest_results],
            [(u'minion.local', u'Memory Usage')])
