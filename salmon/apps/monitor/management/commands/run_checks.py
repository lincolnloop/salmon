import datetime
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from salmon.apps.monitor import models, utils


class Command(BaseCommand):
    help = "Run Salt monitor checks"
    option_list = BaseCommand.option_list + (
        make_option('--fake', action='store_true', dest='fake', default=False,
                    help='Do not run the checks '
                         'but print the Salt command instead'),
        make_option('--no-alert', action='store_true', dest='no_alert',
                    default=False,
                    help='Alert via email when a check fails'),)

    def handle(self, *args, **options):
        self.options = options
        config = utils.load_salmon_checks()
        if options['fake']:
            self.stdout.write("Printing checks [fake mode] ...")
        else:
            self.stdout.write("Running checks...")

        self.active_checks = []
        for target, functions in config.items():
            for func_name, func_opts in functions.items():
                salt_proxy = utils.SaltProxy(target, func_name)
                self.stdout.write("salt command: %s" % salt_proxy.cmd)
                if not options['fake']:
                    result = salt_proxy.run()
                    self._handle_result(target, func_name, func_opts, result)
        if not options['fake']:
            self.cleanup()
        if not options['no_alert'] and self.active_checks:
            self.stdout.write("Alerting via email")
            for check in models.Check.objects.filter(
                    id__in=self.active_checks):
                check.send_alert_email()

    def cleanup(self):
        """
        Flag inactive checks and remove old results from database.
        """
        inactived_checks = models.Check.objects.exclude(active=False).exclude(
            pk__in=self.active_checks)
        self.stdout.write("{0} checks deactivated".format(
            inactived_checks.count()))
        inactived_checks.update(active=False)

        self.stdout.write("Removing old results...")
        now = datetime.datetime.now()
        expiration_date = now - datetime.timedelta(
            minutes=settings.EXPIRE_RESULTS)
        models.Result.objects.filter(timestamp__lt=expiration_date).delete()
        self.stdout.write("Done!")

    def _handle_result(self, target, func_name, func_opts, result):
        """
        handle salt check result and stores results to database.
        """
        # TODO: Move this elsewhere were it is more easily testable.
        alert_emails = func_opts.get('alert_emails', [])

        if alert_emails in [False, None]:
            alert_emails = models.Check.NO_EMAIL_FLAG
        else:
            alert_emails = ",".join(alert_emails)

        check, _ = models.Check.objects.get_or_create(
            target=target, function=func_name,
            name=func_opts.get('name', func_name),
            alert_emails=alert_emails)
        timestamp = timezone.now()

        if not check.active:
            check.active = True
            check.save()
        self.active_checks.append(check.pk)

        # parse out minion names in the event of a wildcard target
        for name, raw_value in result.iteritems():
            if int(self.options["verbosity"]) > 1:
                self.stdout.write(
                    "+     name: {0} -- str(raw_value): {1}".format(
                        name, str(raw_value)))
            value = utils.parse_value(raw_value, func_opts)
            self.stdout.write("   {0}: {1}".format(name, value))
            minion, _ = models.Minion.objects.get_or_create(name=name)
            failed = utils.check_failed(value, func_opts)
            self.stdout.write("   Assertion: {0}".format(not failed))
            models.Result.objects.create(timestamp=timestamp,
                                         result=value,
                                         result_type=func_opts['type'],
                                         check=check,
                                         minion=minion,
                                         failed=failed)
