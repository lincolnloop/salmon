from django.template import Library

register = Library()


@register.inclusion_tag("monitor/includes/base_field.html")
def display_result(result):
    if result.result_type in ['percentage', 'percentage_with_sign']:
        template = 'percentage_field.html'
    elif result.result_type == 'boolean':
        template = 'boolean_field.html'
    elif result.result_type == 'string':
        template = 'string_field.html'
    else:
        template = 'default_field.html'
    template = 'monitor/includes/{0}'.format(template)
    return {'field_template': template, 'result': result}
