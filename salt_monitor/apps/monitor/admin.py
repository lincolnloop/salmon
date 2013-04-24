from django.contrib import admin
from . import models


class CheckInline(admin.TabularInline):
    model = models.Check
    exclude = ('last_run',)


class TargetAdmin(admin.ModelAdmin):
    inlines = (CheckInline,)


admin.site.register(models.Target, TargetAdmin)
admin.site.register(models.Check)
admin.site.register(models.Function)
admin.site.register(models.Result)
