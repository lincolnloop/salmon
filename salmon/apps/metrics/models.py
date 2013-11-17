import operator
import time
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.text import get_valid_filename
from django.template import defaultfilters
from salmon.core import graph


class Source(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("history", kwargs={"name": self.name})


class Metric(models.Model):
    OPERATOR_CHOICES = (
        ('lt', 'value < alert'),
        ('le', 'value <= alert'),
        ('eq', 'value == alert'),
        ('ne', 'value != alert'),
        ('ge', 'value >= alert'),
        ('gt', 'value > alert'),
    )
    DISPLAY_CHOICES = (
        ('float', 'Number'),
        ('boolean', 'True/False'),
        ('byte', 'Bytes'),
        ('percentage', 'Percentage'),
        ('second', 'Seconds'),
    )
    source = models.ForeignKey(Source, null=True)
    name = models.CharField(max_length=255)
    latest_value = models.FloatField(null=True)
    last_updated = models.DateTimeField(null=True)
    alert_operator = models.CharField(max_length=2, choices=OPERATOR_CHOICES,
                                      blank=True)
    alert_value = models.FloatField(null=True, blank=True)
    alert_triggered = models.BooleanField(default=False)
    display_as = models.CharField(max_length=20, choices=DISPLAY_CHOICES,
                                  default='float')

    class Meta:
        unique_together = ('source', 'name')

    @property
    def whisper_filename(self):
        """Build a file path to the Whisper database"""
        return get_valid_filename("{0}__{1}.wsp".format(self.source.name,
                                                        self.name))

    def add_latest_to_archive(self):
        """Adds value to whisper DB"""
        archive = self.get_or_create_archive()
        archive.update(self.last_updated, self.latest_value)

    def get_or_create_archive(self):
        """
        Gets a Whisper DB instance.
        Creates it if it doesn't exist.
        """
        return graph.WhisperDatabase(self.whisper_filename)

    def load_archive(self, from_date, to_date=None):
        """Loads in historical data from Whisper database"""
        return self.get_or_create_archive().fetch(from_date, to_date)

    def in_alert_state(self):
        oper = getattr(operator, self.alert_operator)
        return bool(oper(self.latest_value, self.alert_value))

    def get_value_display(self):
        """Human friendly value output"""
        if self.display_as == 'percentage':
            return '{0}%'.format(self.latest_value)
        if self.display_as == 'boolean':
            return bool(self.latest_value)
        if self.display_as == 'byte':
            return defaultfilters.filesizeformat(self.latest_value)
        if self.display_as == 'second':
            return time.strftime('%H:%M:%S', time.gmtime(self.latest_value))
        return self.latest_value

    def save(self, *args, **kwargs):
        if self.alert_operator and self.alert_value:
            self.alert_triggered = self.in_alert_state()
        return super(Metric, self).save(*args, **kwargs)
