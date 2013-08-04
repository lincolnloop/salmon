import json
import logging
import subprocess

from django.conf import settings
from django.db import connection
import yaml


logger = logging.getLogger(__name__)


def get_latest_results(minion=None, check_ids=None):
    """
    For each (or all) minions and for the given check_ids
    get the newest result for every active check
    """
    from . import models
    cursor = connection.cursor()
    if not check_ids:
        check_ids = (models.Check.objects.filter(active=True)
                                         .values_list('pk', flat=True))

    if check_ids:
        if len(check_ids) == 1:
            having = "check_id = {0}".format(check_ids[0])
        else:
            having = "check_id IN {0}".format(tuple(check_ids))
        if minion:
            having += " AND minion_id={0}".format(minion.pk)
        # we need a first query to get the latest batch of results
        latest_timestamps = cursor.execute("""
            SELECT minion_id, check_id, MAX("timestamp")
            FROM "monitor_result"
            GROUP BY "monitor_result"."minion_id", "monitor_result"."check_id"
            HAVING {0};""".format(having))

        data = latest_timestamps.fetchall()
        if data:
            # transform the result to group them by minion_id, check_id,
            # timestamp # the new form of latest_timestamps can easily be
            # consumed by Result ORM
            latest_timestamps = zip(*data)
            latest_results = models.Result.objects.filter(
                minion_id__in=latest_timestamps[0],
                check_id__in=latest_timestamps[1],
                timestamp__in=latest_timestamps[2])
    else:
        latest_results = []
    return latest_results


def load_salmon_checks():
    """Reads in checks.yaml and returns Python object"""
    checks_yaml = open(settings.SALMON_CHECKS_PATH).read()
    return yaml.safe_load(checks_yaml)


class SaltProxy(object):

    def __init__(self, target, function, output="json"):
        self.target = target
        self.function = function
        self.output = output
        self.cmd = self._build_command(output=output)

    def _build_command(self, output='json'):
        # FIXME: this is a bad way to build up the command
        if settings.SALT_COMMAND.startswith('ssh'):
            quote = '\\\"'
        else:
            quote = '"'
        args = '--static --out={output} {quote}{target}{quote} {function}'.format(
            output=self.output, quote=quote,
            target=self.target, function=self.function)
        cmd = settings.SALT_COMMAND.format(args=args)
        return cmd

    def run(self):
        try:
            result = subprocess.Popen(self._build_command(),
                                      shell=True,
                                      stdout=subprocess.PIPE).communicate()[0]
            return json.loads(result)
        except ValueError as err:
            logging.exception("Error parsing results.")


def _traverse_dict(obj, key_string):
    """
    Traverse a dictionary using a dotted string.
    Example: 'a.b.c' will return obj['a']['b']['c']
    """
    for key in key_string.split('.'):
        if 'key' in obj and isinstance(obj, dict):
            obj = obj[key]
        else:
           return None
    return obj


def parse_values(raw_value, opts):
    """Parses Salt return value to find the keys specified"""

    if 'keys' in opts:
        results = []
        for key in opts['keys']:
            results.append(Value(
                key=key, raw=_traverse_dict(raw_value, key),
                cast_to=opts['type']))
        return results

    if 'key' in opts:
        key = opts['key']
        raw_value = _traverse_dict(raw_value, opts['key'])
    else:
        key = ''
    return [Value(key=key, raw=raw_value, cast_to=opts['type'])]


def check_failed(values, opts):
    if 'assert' not in opts:
        [val.floatify() for val in values]
        return None
    for value in values:
        success = value.do_assert(opts['assert'])
        if not success:
            return True
    return False


def serialize_values(values):
    """
    Convert a list of `Value` objects into a dictionary
    for pushing to the database.
    """

    serialized = {}
    for value in values:
        serialized[value.key] = value.as_dict()
    return serialized


class Value(object):
    """Everything needed to convert, check, and serialize a value"""
    def __init__(self, key, raw, cast_to):
        self.key = key
        self.raw = raw
        self.cast_to = cast_to
        self.real = self.cast()
        # wait for float until success is known
        self.float = None
        self.success = None

    def as_dict(self):
        return {'real': self.real, 'raw': self.raw, 'float': self.float,
                'type': self.cast_to}

    def cast(self):
        conv_method = getattr(self, 'to_{0}'.format(self.cast_to))
        return conv_method()

    def do_assert(self, assertion_string):
        # TODO: try to remove the evil
        success = eval(assertion_string.format(value=self.real))
        assert isinstance(success, bool)
        self.success = success
        self.floatify()
        return success

    def floatify(self):
        if self.cast_to == 'string':
            self.float = float(self.success)
            return
        try:
            self.float = float(self.real)
        except ValueError:
            self.float = float(0)

    def to_boolean(self):
        # bool('False') == True
        if self.raw == "False":
            return False
        return bool(self.raw) is True

    def to_integer(self):
        return self.to_float(self.raw)

    def to_percentage(self):
        return self.to_float(self.raw)

    def to_percentage_with_sign(self):
        return self.to_float(self.raw.rstrip('%'))

    def to_float(self, val):
        # float(None) blows up
        if not val:
            return float(0)
        return float(val)

    def to_string(self):
        return str(self.raw)
