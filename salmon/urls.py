from django.conf.urls import patterns, url, include
from django.contrib import admin

from salmon.metrics import views as metrics_views

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^$', metrics_views.dashboard, name="dashboard"),
    url(r'^(?P<name>[-\w\._]*)/$', metrics_views.history, name="history"),
    url(r'^api/v1/metric/$', metrics_views.CreateMetricView.as_view()),
)
