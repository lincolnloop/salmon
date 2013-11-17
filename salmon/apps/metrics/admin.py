from django.contrib import admin
from . import models


class MetricAdmin(admin.ModelAdmin):
    list_filter = ('source',)
    date_hierarchy = 'last_updated'
    list_display = ('last_updated', 'name', 'source', 'value_display',
                    'alert_triggered', 'display_as', 'alert_operator',
                    'alert_value')
    list_editable = ('display_as', 'alert_operator', 'alert_value')

    fieldsets = (
        (None, {
            'fields': (('name', 'source'), ('alert_operator', 'alert_value'),
                        'display_as'),
        }),
        ('Last update', {
            'fields': ('last_updated', 'latest_value', 'alert_triggered'),
        }),
    )

    def value_display(self, obj):
        return obj.get_value_display()
    value_display.admin_order_field = 'latest_value'



admin.site.register(models.Metric, MetricAdmin)
admin.site.register(models.Source)
