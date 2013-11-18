import datetime
import random
import shutil
from tempfile import mkdtemp

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from salmon.apps.metrics import models

INTERVAL_MIN = 5


@override_settings(SALMON_WHISPER_DB_PATH=mkdtemp())
class TestModels(TestCase):

    def tearDown(self):
        try:
            shutil.rmtree(settings.SALMON_WHISPER_DB_PATH)
        except OSError:
            pass

    def test_no_alert(self):
        metric = models.Metric(latest_value=10, alert_operator='lt',
                               alert_value=11)
        self.assertTrue(metric.in_alert_state())

    def test_yes_alert(self):
        metric = models.Metric(latest_value=10, alert_operator='lt',
                               alert_value=8)
        self.assertFalse(metric.in_alert_state())

    def test_counter(self):
        first_value = 20
        second_value = 30
        metric = models.Metric(name='a', is_counter=True,
                               latest_value=first_value)
        metric.latest_value = second_value
        metric.save()
        self.assertEqual(metric.latest_value, second_value - first_value)

    def test_archive(self):
        iters = 5
        start = (datetime.datetime.now() -
                 datetime.timedelta(minutes=iters * INTERVAL_MIN))
        metric = models.Metric(name='a', latest_value=0, last_updated=start)
        for i in range(iters):
            metric.latest_value = random.randint(1, 100)
            metric.last_updated = (
                start + datetime.timedelta(minutes=i * INTERVAL_MIN))
            metric.add_latest_to_archive()

        self.assertEqual(len(metric.load_archive(start)), iters)
