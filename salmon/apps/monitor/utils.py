from django.conf import settings


def get_latest_results(minion=None):
    """
    For each (or all) minions,
    get the newest result for every active check
    """
    from . import models
    active_checks = (models.Check.objects.filter(active=True)
                                         .values_list('pk', flat=True))

    if active_checks:
        if len(active_checks) == 1:
            having = "check_id = {}".format(active_checks[0])
        else:
            having = "check_id IN {}".format(tuple(active_checks))
        if minion:
            having += " AND minion_id={}".format(minion.pk)
        latest_results = models.Result.objects.raw("""
            SELECT id, check_id, MAX("timestamp")
            FROM "monitor_result"
            GROUP BY "monitor_result"."minion_id", "monitor_result"."check_id"
            HAVING {};""".format(having))
    else:
        latest_results = []
    return latest_results


def build_command(target, function, output='json'):
    # FIXME: this is a bad way to build up the command
    if settings.SALT_COMMAND.startswith('ssh'):
        quote = '\\\"'
    else:
        quote = '"'
    args = '--static --out={output} {quote}{target}{quote} {function}'.format(
        output=output, quote=quote, target=target, function=function)
    cmd = settings.SALT_COMMAND.format(args=args)
    return cmd


def check_failed(value, opts):
    if isinstance(value, basestring):
        value = TypeTranslate(opts['type']).cast(value)
    success = eval(opts['assert'].format(value=value))
    assert isinstance(success, bool)
    # this is check_failed, not check_success
    return not success


def parse_value(raw_value, opts):
    value = raw_value
    if 'key' in opts:
        key_tree = opts['key'].split('.')
        for key in key_tree:
            value = value[key]
    # Handle the special case where the value is None
    elif value == None:
        value = ""
    return value


class TypeTranslate(object):
    def __init__(self, cast_to):
        self.cast_to = cast_to

    def cast(self, value):
        return getattr(self, 'to_{}'.format(self.cast_to))(value)

    def to_boolean(self, value):
        return bool(value) == True

    def to_percentage(self, value):
        return self.to_float(value)

    def to_percentage_with_sign(self, value):
        return self.to_float(value.rstrip('%'))

    def to_float(self, value):
        return float(value)
