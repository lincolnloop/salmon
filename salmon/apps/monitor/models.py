import logging

from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.text import get_valid_filename

from . import utils, graph


logger = logging.getLogger(__name__)


class Check(models.Model):
    """A description for a Salt call"""
    target = models.CharField(max_length=255)
    function = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    alert_emails = models.CharField(max_length=255, blank=True,
                                    help_text="Comma separated list of emails")
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return '{0} {1} ({2})'.format(self.target, self.function, self.name)

    def send_alert_email(self):
        from_email = settings.DEFAULT_FROM_EMAIL
        to_emails = self.get_alert_emails()
        subject = render_to_string(
            "monitor/emails/subject_alert_email.txt",
            {"check": self})
        latest_results = utils.get_latest_results(
            minion=None, check_ids=[self.id])

        failures = {}
        last_failing_result_ids = []
        for result in latest_results:
            if result.failed:
                last_failing_result_ids.append(result.id)
                try:
                    last_successful = Result.objects.filter(
                        minion=result.minion,
                        check=self.pk,
                        failed=False).order_by("-timestamp")[0]
                except IndexError:
                    last_successful = None
                failures[result.minion] = {
                    "last_failed": result,
                    "last_successful": last_successful}

        if failures and to_emails:
            msg = render_to_string(
                "monitor/emails/message_alert_email.txt",
                {
                    "check": self,
                    "failures": failures
                })

            try:
                # TODO: Understand where the \n is coming from
                send_mail(subject.strip("\n"), msg, from_email, to_emails)
                (Result.objects.filter(id__in=last_failing_result_ids)
                               .update(notified=True))
            except Exception as err:
                logger.exception("An error occured while sending alert emails")

    def get_alert_emails(self):
        """
        This method return a list of email address that should be notified
        for this check
        """
        if self.alert_emails:
            return self.alert_emails.split(",")
        return settings.ALERT_EMAILS


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
    notified = models.BooleanField(default=False)

    def __unicode__(self):
        return self.timestamp.isoformat()

    @property
    def cleaned_result(self):
        return utils.TypeTranslate(self.result_type).cast(self.result)

    @property
    def whisper_filename(self):
        """Build a file path to the Whisper database"""
        return get_valid_filename("{0}__{1}.wsp".format(
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
            if isinstance(self.result, basestring) or self.result_type:
                value = self.cleaned_result
            else:
                value = self.result
            wsp.update(self.timestamp, value)
        return super(Result, self).save(*args, **kwargs)
