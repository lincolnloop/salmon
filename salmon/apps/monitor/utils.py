from django.conf import settings


def build_command(target, function, output='json'):
    args = '--static --out={} \\\"{}\\\" {}'.format(output, target, function)
    cmd = settings.SALT_COMMAND.format(args=args)
    return cmd


def check_failed(value, opts):
    import ipdb; ipdb.set_trace()
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
    return value


class TypeTranslate(object):
    def __init__(self, cast_to):
        self.cast_to = cast_to

    def cast(self, value):
        return getattr(self, 'to_{}'.format(self.cast_to))(value)

    def to_boolean(self, value):
        return value == 'True'

    def to_percentage(self, value):
        return self.to_float(value)

    def to_percentage_with_sign(self, value):
        return self.to_float(value.rstrip('%'))

    def to_float(self, value):
        return float(value)
