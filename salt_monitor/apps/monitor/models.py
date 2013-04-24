from django.db import models
from django.utils import timezone
from django.conf import settings


class Target(models.Model):
    """A Salt target minion"""
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Function(models.Model):
    """The Salt function (module) to call"""
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Check(models.Model):
    """A description for a Salt call"""
    target = models.ForeignKey('monitor.Target')
    function = models.ForeignKey('monitor.Function')
    active = models.BooleanField(default=True)
    last_run = models.DateTimeField(default=timezone.now, null=True)

    def __unicode__(self):
        return '{} {}'.format(self.target, self.function)

    @property
    def salt_command(self, output='json'):
        """The actual Salt command to shell out"""
        return ' '.join([settings.SALT_COMMAND,
                         '--static',
                         '--out={}'.format(output),
                         '"{}"'.format(self.target.name),
                         self.function.name])


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

    def __unicode__(self):
        return self.timestamp.isoformat()
