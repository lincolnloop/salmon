import datetime
import random

from salmon.metrics import models

def generate_sample_data(point_numbers, interval):
    """
    This function generates sample data and populates the databases

        :point_numbers: is an int defining the number of values for each metric
        :interval: is an int defining the interval between each results

    This method returns a list of metrics
    """
    src_names = ['test.example.com', 'salmon.example.com', 'www.example.com']
    sources = []
    for name in src_names:
        sources.append(models.Source.objects.get_or_create(name=name)[0])
    sources.append(None)
    metric_names = ['ps.virtual_memory_usage',
                    'ps.disk_io_counters.write_bytes',
                    'ps.disk_io_counters.read_bytes',
                    'ps.disk_usage.percent',
                    'ps.physical_memory_usage.percent']

    for source in sources:
        for name in metric_names:
            metric = models.Metric.objects.get_or_create(source=source,
                                                         name=name)[0]
            start = datetime.datetime.now() - datetime.timedelta(
                minutes=interval * point_numbers)
            for i in range(point_numbers):
                metric.latest_value = random.randint(1, 100)
                metric.last_updated = (start +
                                       datetime.timedelta(minutes=interval * i))
                metric.save()

