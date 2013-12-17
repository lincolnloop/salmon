from django.contrib import admin
from . import models

class MetricAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('source',)
    list_display = ('name', 'source', 'last_updated', 'value_display',
                    'alert_triggered', 'display_as', 'is_counter', 'transform',
                    'alert_operator', 'alert_value')
    list_editable = ('display_as', 'is_counter',
                     'alert_operator', 'alert_value')


    def __init__(self, *args, **kwargs):
        super(MetricAdmin, self).__init__(*args, **kwargs)
        # Don't link to detail pages
        self.list_display_links = (None, )

    def has_add_permission(self, request):
        """Hides the add metric link in admin"""
        return False

    def value_display(self, obj):
        return obj.get_value_display()
    value_display.admin_order_field = 'latest_value'


class MetricGroupAdmin(MetricAdmin):
    list_filter = ('display_as', 'is_counter')
    list_display = ('name', 'display_as', 'is_counter', 'transform',
                    'alert_operator', 'alert_value')


    def get_queryset(self, request):
        """Shows one entry per distinct metric name"""
        queryset = super(MetricGroupAdmin, self).get_queryset(request)
        # poor-man's DISTINCT ON for Sqlite3
        qs_values = queryset.values('id', 'name')
        # 2.7+ only :(
        # = {metric['name']: metric['id'] for metric in qs_values}
        distinct_names = {}
        for metric in qs_values:
            distinct_names[metric['name']] = metric['id']
        queryset = self.model.objects.filter(id__in=distinct_names.values())
        return queryset

    def save_model(self, request, obj, form, change):
        """Updates all metrics with the same name"""
        like_metrics = self.model.objects.filter(name=obj.name)
        # 2.7+ only :(
        # = {key: form.cleaned_data[key] for key in form.changed_data}
        updates = {}
        for key in form.changed_data:
            updates[key] = form.cleaned_data[key]
        like_metrics.update(**updates)



admin.site.register(models.Metric, MetricAdmin)
admin.site.register(models.MetricGroup, MetricGroupAdmin)
admin.site.register(models.Source)
