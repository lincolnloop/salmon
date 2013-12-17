import datetime
import random
import shutil
from tempfile import mkdtemp

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from salmon.core.tests import BaseTestCase
from salmon.metrics import models

INTERVAL_MIN = 5


class TestModels(BaseTestCase):

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
        third_value = 70
        metric = models.Metric(name='a', is_counter=True,
                               latest_value=first_value)
        metric.save()
        metric.latest_value = second_value
        metric.save()
        self.assertEqual(metric.latest_value, second_value - first_value)
        metric.latest_value = third_value
        metric.save()
        self.assertEqual(metric.latest_value, third_value - second_value)


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
