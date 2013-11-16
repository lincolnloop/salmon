from django.contrib import admin
from . import models


class MetricAdmin(admin.ModelAdmin):
    list_filter = ("source",)
    date_hierarchy = "last_updated"
    list_display = ("last_updated", "name", "source", "latest_value",
                    "alert_triggered")

    fieldsets = (
        (None, {
            'fields': (('name', 'source'), ('alert_operator', 'alert_value'),
                        'display_as'),
        }),
        ('Last update', {
            'fields': ('last_updated', 'latest_value', 'alert_triggered'),
        }),
    )



admin.site.register(models.Metric, MetricAdmin)
admin.site.register(models.Source)
