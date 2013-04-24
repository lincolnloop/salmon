import json
from django.core.management.base import NoArgsCommand
from django.utils import timezone
import envoy

from salt_monitor.apps.monitor import models


class Command(NoArgsCommand):
    help = "Run Salt monitor checks"

    def handle_noargs(self, **options):
        self.stdout.write("Running checks...")
        for check in models.Check.objects.filter(active=True):
            self.stdout.write("+ {}".format(check.salt_command))
            timestamp = timezone.now()
            result = envoy.run(check.salt_command)
            check.last_run = timestamp
            check.save()
            try:
                parsed = json.loads(result.std_out)
            except ValueError:
                self.stdout.write("  Error parsing results")
                continue
            # parse out minion names in the event of a wildcard target
            for name, value in parsed.iteritems():
                self.stdout.write("  {}: {}".format(name, value))
                minion, _ = models.Minion.objects.get_or_create(name=name)
                models.Result.objects.create(timestamp=timestamp,
                                             result=value,
                                             check=check,
                                             minion=minion)
