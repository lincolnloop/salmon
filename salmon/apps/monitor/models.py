from django.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.text import get_valid_filename

from . import utils, graph


class Check(models.Model):
    """A description for a Salt call"""
    target = models.CharField(max_length=255)
    function = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return '{} {} ({})'.format(self.target, self.function, self.name)


class Minion(models.Model):
    """A single minion surfaced by a Salt call"""
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("history", kwargs={"name": self.name})


class Result(models.Model):
    """The results of a Check"""
    check = models.ForeignKey('monitor.Check')
    minion = models.ForeignKey('monitor.Minion')
    timestamp = models.DateTimeField(default=timezone.now)
    result = models.TextField()
    result_type = models.CharField(max_length=30)
    failed = models.BooleanField(default=True)

    def __unicode__(self):
        return self.timestamp.isoformat()

    @property
    def cleaned_result(self):
        return utils.TypeTranslate(self.result_type).cast(self.result)

    @property
    def whisper_filename(self):
        """Build a file path to the Whisper database"""
        return get_valid_filename("{}__{}.wsp".format(
            self.minion.name, self.check.name))

    def get_or_create_whisper(self):
        """
        Gets a Whisper DB instance.
        Creates it if it doesn't exist.
        """
        return graph.WhisperDatabase(self.whisper_filename)

    def get_history(self, from_date, to_date=None):
        """Loads in historical data from Whisper database"""
        return self.get_or_create_whisper().fetch(from_date, to_date)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Store the value in the whisper database
            wsp = self.get_or_create_whisper()
            if isinstance(self.result, basestring):
                value = self.cleaned_result
            else:
                value = self.result
            wsp.update(self.timestamp, value)
        return super(Result, self).save(*args, **kwargs)
