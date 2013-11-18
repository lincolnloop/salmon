from django.test import TestCase

from salmon.metrics.serializers import MetricSerializer
from salmon.metrics import models

class TestSerializer(TestCase):

    def test_single(self):
        data = {'source': 'test.example.com',
                'name': 'load',
                'value': 0.1}
        serializer = MetricSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        metric = models.Metric.objects.get(pk=serializer.object.pk)
        self.assertEqual(data['source'], metric.source.name)
        self.assertEqual(data['name'], metric.name)
        self.assertEqual(data['value'], metric.latest_value)
        self.assertFalse(metric.last_updated is None)


    def test_multi(self):
        data = [
            {'source': 'test.example.com', 'name': 'load', 'value': 0.1},
            {'source': 'multi.example.com', 'name': 'cpu', 'value': 55.5},
        ]
        serializer = MetricSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        for item in data:
            source = models.Source.objects.get(name=item['source'])
            self.assertEqual(source.metric_set.count(), 1)

    def test_invalid(self):
        data = {'source': 'test.example.com',
                'name': 'load'}
        serializer = MetricSerializer(data=data)
        self.assertFalse(serializer.is_valid())
