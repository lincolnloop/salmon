from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.dashboard, name="dashboard"),
    url(r'^(?P<name>[\w\.]*)$', views.history, name="history"),
)
