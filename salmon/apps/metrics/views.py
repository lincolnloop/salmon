import datetime
import json
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.utils.datastructures import SortedDict
from django.utils.timezone import now

from rest_framework.generics import CreateAPIView
from rest_framework.authentication import SessionAuthentication

from salmon.core import authentication, permissions
from . import forms, models, serializers


class CreateMetricView(CreateAPIView):
    """Saves a new metric value (or values)"""
    authentication_classes = (authentication.SettingsAuthentication,
                              SessionAuthentication)
    permission_classes = (permissions.SalmonPermission,)
    model = models.Metric
    serializer_class = serializers.MetricSerializer

    def get_serializer(self, instance=None, data=None, files=None,
                       many=False, partial=False):
        if isinstance(data, list):
            many = True
        return super(CreateMetricView, self).get_serializer(instance, data,
                                                            files, many,
                                                            partial)


def dashboard(request):
    """Shows the latest results for each source"""
    sources = (models.Source.objects.all().prefetch_related('metric_set')
                                          .order_by('name'))
    metrics = SortedDict([(src, src.metric_set.all()) for src in sources])
    no_source_metrics = models.Metric.objects.filter(source__isnull=True)
    if no_source_metrics:
        metrics[''] = no_source_metrics

    if request.META.get('HTTP_X_PJAX', False):
        parent_template = 'pjax.html'
    else:
        parent_template = 'base.html'
    return render(request, 'metrics/dashboard.html', {
        'source_metrics': metrics,
        'parent_template': parent_template
    })

def history(request, name):
    source = get_object_or_404(models.Source, name=name)
    from_date = now() - datetime.timedelta(hours=12)
    to_date = now()

    initial = {
        "from_date": from_date,
        "to_date": to_date
    }
    if "from_date" in request.GET or "to_date" in request.GET:
        data = request.GET.copy()
        if not request.GET.get("from_date"):
            data.setlist("from_date", [from_date])
        if not request.GET.get("to_date"):
            data.setlist("to_date", [to_date])
        form = forms.FilterHistory(data, initial=initial)
        if form.is_valid():
            from_date = form.cleaned_data["from_date"] or from_date
            to_date = form.cleaned_data["to_date"] or to_date
    else:
        form = forms.FilterHistory(initial=initial)
    graphs = []

    for metric in source.metric_set.all().order_by('name'):
        history = metric.load_archive(
            from_date=from_date,
            to_date=to_date)
        # javascript uses milliseconds since epoch
        js_data = map(lambda x: (x[0] * 1000, x[1]), history)
        graphs.append({
            'name': metric.name,
            'data': json.dumps(js_data),
            'type': 'float',
        })
    if request.META.get('HTTP_X_PJAX', False):
        parent_template = 'pjax.html'
    else:
        parent_template = 'base.html'
    return render(request, 'metrics/history.html', {
        'form': form,
        'source': source,
        'graphs': graphs,
        'parent_template': parent_template,
        'refresh_interval_history': settings.REFRESH_INTERVAL_HISTORY,
    })

