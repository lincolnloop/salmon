from django.db import models
from django.utils import timezone
from django.conf import settings


class Check(models.Model):
    """A description for a Salt call"""
    target = models.CharField(max_length=255)
    function = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)
    last_run = models.DateTimeField(default=timezone.now, null=True)

    def __unicode__(self):
        return '{} {}'.format(self.target, self.function)


class Minion(models.Model):
    """A single minion surfaced by a Salt call"""
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


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
        return utils.TypeTranslate(self.result_type)(self.result)