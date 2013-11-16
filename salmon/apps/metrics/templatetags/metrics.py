from django.template import Library

register = Library()


@register.inclusion_tag("metrics/includes/base_field.html")
def display_result(metric):
    template = 'metrics/includes/{0}_field.html'.format(metric.display_as)
    return {'field_template': template, 'metric': metric}
