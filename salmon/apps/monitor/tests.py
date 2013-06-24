from datetime import datetime, timedelta
from tempfile import mkdtemp
import os
import shutil
from random import randint

from django.test.utils import override_settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase


from salmon.apps.monitor.graph import WhisperDatabase
from salmon.apps.monitor.models import Minion, Check, Result
from salmon.apps.monitor.utils import (get_latest_results, build_command,
                                       Checker)

POINT_NUMBERS = 50
INTERVAL_MIN = 5


def generate_sample_data(point_numbers, interval):
    """
    This method generate sample data and populate the databases

        :point_numbers: is an int that defines the number of results
        :interval: is an int that defines the interval between each results

    This method returns a tuple (minion, active_check, not_active_check)
    """
    minion, created = Minion.objects.get_or_create(name="minion.local")
    checks = []

    check, created = Check.objects.get_or_create(
        target="*",
        function="ps.virtual_memory_usage",
        name="Memory Usage",
        active=True)
    checks.append(check)

    check, created = Check.objects.get_or_create(
        target="*",
        function="disk.usage",
        name="Disk usage (not active)",
        active=False)
    checks.append(check)

    now = datetime.now()
    for i in range(point_numbers):
        for check in checks:
            Result.objects.create(
                check=check,
                minion=minion,
                timestamp=now-timedelta(minutes=interval*i),
                result=str(randint(1, 100)),
                result_type="float",
                failed=False)

    return (minion, checks[0], checks[1])


@override_settings(SALMON_WHISPER_DB_PATH=mkdtemp())
class BaseTestCase(TestCase):
    def setUp(self):
        self.minion, self.active_check, self.not_active_check = (
            generate_sample_data(POINT_NUMBERS, INTERVAL_MIN))

    def tearDown(self):
        shutil.rmtree(settings.SALMON_WHISPER_DB_PATH)


class WhisperDatabaseTest(BaseTestCase):

    def test_database_creation(self):
        """
        Tests that the whisper database get created if does not exist.
        """
        not_existing_wsp = "doesnotexist.wsp"
        path = os.path.join(settings.SALMON_WHISPER_DB_PATH, not_existing_wsp)
        self.assertEqual(os.path.exists(path), False)
        WhisperDatabase(path)
        self.assertEqual(os.path.exists(path), True)

    def test_database_update(self):
        now = datetime.now()
        result = Result.objects.create(check=self.active_check,
                                       minion=self.minion,
                                       timestamp=now,
                                       result="101",
                                       result_type="float",
                                       failed=False)
        history = result.get_history(now-timedelta(minutes=INTERVAL_MIN*20))
        self.assertEqual(len(history), 20)


class MonitorUrlTest(BaseTestCase):

    def test_dashboard_get(self):
        url = reverse("dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_history_get(self):
        url = self.minion.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["graphs"]), 1)


class MonitorUtilsTest(BaseTestCase):
    def test_get_latest_results_for_all_minions(self):
        latest_results = get_latest_results()
        self.assertEqual(
            [(r.minion.name, r.check.name) for r in latest_results],
            [(u'minion.local', u'Memory Usage')])

    def test_get_latest_results_a_minion(self):
        latest_results = get_latest_results(minion=self.minion)
        self.assertEqual(
            [(r.minion.name, r.check.name) for r in latest_results],
            [(u'minion.local', u'Memory Usage')])


@override_settings(SALMON_WHISPER_DB_PATH=mkdtemp(),
                   ALERT_EMAILS=["alert1@ll.com, alert2@ll.com"])
class MonitorModelCheckTest(TestCase):
    def setUp(self):
        self.check, created = Check.objects.get_or_create(
            target="*",
            function="ps.virtual_memory_usage",
            name="Memory Usage",
            active=True)

        self.check_with_emails, created = Check.objects.get_or_create(
            target="*",
            function="disk.usage",
            name="Disk usage (not active)",
            alert_emails=",".join(["yml@ll.com", "ipmb@ll.com"]),
            active=False)

        minion, created = Minion.objects.get_or_create(name="minion.local")
        now = datetime.now()
        for check in [self.check, self.check_with_emails]:
            Result.objects.create(
                check=check,
                minion=minion,
                timestamp=now-timedelta(minutes=INTERVAL_MIN*1),
                result=str(randint(1, 100)),
                result_type="float",
                failed=True)
            Result.objects.create(
                check=check,
                minion=minion,
                timestamp=now-timedelta(minutes=INTERVAL_MIN*2),
                result=str(randint(1, 100)),
                result_type="float",
                failed=False)

    def tearDown(self):
        try:
            shutil.rmtree(settings.SALMON_WHISPER_DB_PATH)
        except OSError:
            # No reason to bell out if the temp directory has not been created
            pass

    def test_check_get_alert_emails(self):
        self.assertEqual(self.check.get_alert_emails(),
                         ['alert1@ll.com, alert2@ll.com'])

    def test_check_with_emails_get_alert_emails(self):
        self.assertEqual(self.check_with_emails.get_alert_emails(),
                         ["yml@ll.com", "ipmb@ll.com"])

    def test_check_send_alert_email(self):
        self.check.send_alert_email()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject.find(self.check.function) > 1,
                         True)


class MonitorUtilsBuildCommmand(TestCase):
    def setUp(self):
        self.target = "*"
        self.function = "disk.usage"

    @override_settings(SALT_COMMAND='ssh example.com "sudo su - salmon  -s ' +
                                    '/bin/bash -c \'salt {args} \'\"')
    def test_build_command_ssh(self):
        expected_cmd = ('ssh example.com "sudo su - salmon  -s /bin/bash -c ' +
                        '\'salt --static --out=json \\"*\\" ' +
                        'disk.usage \'"')
        cmd = build_command(self.target,
                            self.function)
        self.assertEqual(cmd, expected_cmd)

    @override_settings(SALT_COMMAND='/usr/bin/python /usr/bin/salt {args}')
    def test_build_command(self):
        expected_cmd = ('/usr/bin/python /usr/bin/salt --static ' +
                        '--out=json "*" disk.usage')
        cmd = build_command(self.target,
                            self.function)
        self.assertEqual(cmd, expected_cmd)


class CheckerTest(TestCase):

    def test_boolean_false_result(self):
        cast_to = "boolean"
        raw_value = "False"
        assertion_string = "{value} == True"
        checker = Checker(cast_to=cast_to, raw_value=raw_value)
        self.assertEqual(checker.do_assert(assertion_string), False)

    def test_boolean_true_result(self):
        cast_to = "boolean"
        raw_value = "False"
        assertion_string = "{value} == False"
        checker = Checker(cast_to=cast_to, raw_value=raw_value)
        self.assertEqual(checker.do_assert(assertion_string), True)

    def test_string_true_result(self):
        cast_to = "string"
        raw_value = "HTTP/1.1 200 OK"
        assertion_string = "'{value}' == 'HTTP/1.1 200 OK'"
        checker = Checker(cast_to=cast_to, raw_value=raw_value)
        self.assertEqual(checker.do_assert(assertion_string), True)
