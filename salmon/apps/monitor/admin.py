from django.contrib import admin
from . import models


class ResultAdmin(admin.ModelAdmin):
    list_filter = ("minion", "check")
    date_hierarchy = "timestamp"
    list_display = ("timestamp", "minion", "check", "failed",
                    "notified", "result")


class CheckAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "target", "function", "alert_email")


admin.site.register(models.Check, CheckAdmin)
admin.site.register(models.Result, ResultAdmin)
admin.site.register(models.Minion)
