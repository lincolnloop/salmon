from django.utils import unittest

from salmon.metrics.utils import Transform

class TransformTests(unittest.TestCase):
    def test_valid(self):
        result = Transform(expr='x+5*2.5', value=8.0, timedelta=0).result()
        self.assertEqual(result, 8.0+5*2.5)

    def test_bad_variable(self):
        trans = Transform(expr='b+5*2.5', value=8.0, timedelta=0)
        self.assertRaises(ValueError, trans.result)

    def test_invalid_command(self):
        trans = Transform(expr='5**99999', value=8.0, timedelta=0)
        self.assertRaises(TypeError, trans.result)
