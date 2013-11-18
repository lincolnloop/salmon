from django.utils.timezone import now
from django.core.urlresolvers import reverse

from salmon.core.tests import BaseTestCase
from salmon.metrics import models


class MonitorUrlTest(BaseTestCase):

    def setUp(self):
        self.source = models.Source.objects.create(name='source')
        models.Metric.objects.create(source=self.source, name='a',
                                     latest_value=1.0, last_updated=now())

    def test_dashboard_get(self):
        url = reverse("dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_history_get(self):
        url = self.source.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["graphs"]), 1)
