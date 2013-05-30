import datetime
import json
import subprocess
from optparse import make_option
import yaml

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

    def load_salmon_checks(self):
        """Reads in checks.yaml and returns Python object"""
        checks_yaml = open(settings.SALMON_CHECKS_PATH).read()
        return yaml.safe_load(checks_yaml)

    def handle(self, *args, **options):
        self.options = options
        config = self.load_salmon_checks()
        if options['fake']:
            self.stdout.write("Printing checks [fake mode] ...")
        else:
            self.stdout.write("Running checks...")

        self.active_checks = []
        for target, functions in config.items():
            for func_name, func_opts in functions.items():
                cmd = utils.build_command(target, func_name)
                if options['fake']:
                    self.stdout.write("target: %s -- cmd: %s" % (target, cmd))
                    self.stdout.write("    func_name: %s" % func_name)
                    self.stdout.write("    func_opts: %s" % func_opts)

                else:
                    self._run_cmd(target, func_name, func_opts, cmd)
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
        self.stdout.write("{} checks deactivated".format(
            inactived_checks.count()))
        inactived_checks.update(active=False)

        self.stdout.write("Removing old results...")
        now = datetime.datetime.now()
        expiration_date = now - datetime.timedelta(
            minutes=settings.EXPIRE_RESULTS)
        models.Result.objects.filter(timestamp__lt=expiration_date).delete()
        self.stdout.write("Done!")

    def _run_cmd(self, target, func_name, func_opts, cmd):
        """
        Runs salt checks and stores results to database.
        """
        check, _ = models.Check.objects.get_or_create(
            target=target, function=func_name,
            name=func_opts.get('name', func_name),
            alert_email=func_opts.get('alert_email', ""))
        self.stdout.write("+ {}".format(cmd))
        timestamp = timezone.now()
        # shell out to salt command
        result = subprocess.check_output(cmd, shell=True)

        if not check.active:
            check.active = True
            check.save()
        self.active_checks.append(check.pk)

        try:
            parsed = json.loads(result)
        except ValueError:
            self.stdout.write("  Error parsing results")
            return

        # parse out minion names in the event of a wildcard target
        for name, raw_value in parsed.iteritems():
            if int(self.options["verbosity"]) > 1:
                self.stdout.write(
                    "+     name: {} -- str(raw_value): {}".format(
                        name, str(raw_value)))
            value = utils.parse_value(raw_value, func_opts)
            self.stdout.write("   {}: {}".format(name, value))
            minion, _ = models.Minion.objects.get_or_create(name=name)
            failed = utils.check_failed(value, func_opts)
            self.stdout.write("   {}: {}".format("Assertion has failed",
                                                 failed))
            models.Result.objects.create(timestamp=timestamp,
                                         result=value,
                                         result_type=func_opts['type'],
                                         check=check,
                                         minion=minion,
                                         failed=failed)
