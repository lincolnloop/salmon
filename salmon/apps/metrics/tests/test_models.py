from django.test import TestCase

from salmon.apps.metrics import models

class TestModels(TestCase):
    def test_no_alert(self):
        metric = models.Metric(latest_value=10, alert_operator='lt',
                               alert_value=11)
        self.assertTrue(metric.in_alert_state())


    def test_yes_alert(self):
        metric = models.Metric(latest_value=10, alert_operator='lt',
                               alert_value=8)
        self.assertTrue(metric.in_alert_state())
