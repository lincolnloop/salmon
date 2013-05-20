import json
import subprocess
from optparse import make_option
import yaml

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from salmon.apps.monitor import models, utils


class Command(BaseCommand):
    help = "Run Salt monitor checks"
    option_list = BaseCommand.option_list + (
        make_option('--fake',
                    action='store_true',
                    dest='fake',
                    default=False,
                    help='Do not run the checks but print the command instead'),)

    def load_salmon_checks(self):
        checks_yaml = open(settings.SALMON_CHECKS_PATH).read()
        return yaml.safe_load(checks_yaml)

    def handle(self, *args, **options):
        config = self.load_salmon_checks()
        if options['fake']:
            self.stdout.write("Printing checks [fake mode] ...")
        else:
            self.stdout.write("Running checks...")
        for target, functions in config.items():
            for func_name, func_opts in functions.items():
                cmd = utils.build_command(target, func_name)
                if options['fake']:
                    self.stdout.write("cmd: %s" % cmd)
                else:
                    self._run_cmd(cmd)

    def _run_cmd(self, cmd):
        check, _ = models.Check.objects.get_or_create(
            target=target, function=func_name,
            name=func_opts.get('name', func_name))
        self.stdout.write("+ {}".format(' '.join(cmd)))
        timestamp = timezone.now()
        result = subprocess.check_output(cmd)
        check.last_run = timestamp
        check.active = True
        check.save()
        try:
            parsed = json.loads(result)
        except ValueError:
            self.stdout.write("  Error parsing results")
            return
        # parse out minion names in the event of a wildcard target
        for name, raw_value in parsed.iteritems():
            value = utils.parse_value(raw_value, func_opts)
            self.stdout.write("  {}: {}".format(name, value))
            minion, _ = models.Minion.objects.get_or_create(name=name)
            failed = utils.check_failed(value, func_opts)
            models.Result.objects.create(timestamp=timestamp,
                                         result=value,
                                         result_type=func_opts['type'],
                                         check=check,
                                         minion=minion,
                                         failed=failed)
