from django.template import Context, Library, loader

register = Library()

@register.simple_tag
def display_result(metric):
    template_base = 'metrics/includes/{0}_field.html'
    display_template = template_base.format(metric.display_as)
    default_template = template_base.format('default')
    template = loader.select_template([display_template, default_template])
    return template.render(Context({'metric': metric}))
