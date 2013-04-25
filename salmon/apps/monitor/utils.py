from django.conf import settings


def build_command(target, function, output='json'):
    cmd_list = settings.SALT_COMMAND.split()
    cmd_list.extend(['--static', '--out={}'.format(output), target])
    cmd_list.extend(function.split())
    return cmd_list

def check_failed(value_as_str, opts):
    value = TypeTranslate(opts['type']).cast(value_as_str)
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
        return bool(value)

    def to_percentage(self, value):
        return self.to_float(value.rstrip('%'))

    def to_float(self, value):
        return float(value)
