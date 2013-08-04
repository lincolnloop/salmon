from datetime import datetime, timedelta
import json
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from . import models, utils, forms


def dashboard(request):
    """Shows the latest results for each minion"""
    minions = {}
    for result in utils.get_latest_results():
        minions.setdefault(result.minion, []).append(result)
    if request.META.get('HTTP_X_PJAX', False):
        parent_template = 'pjax.html'
    else:
        parent_template = 'base.html'
    return render(request, 'monitor/dashboard.html', {
        'minions': minions,
        'parent_template': parent_template
    })


def history(request, name):
    minion = get_object_or_404(models.Minion, name=name)
    from_date = datetime.now()-timedelta(hours=12)
    to_date = datetime.now()

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

    for result in utils.get_latest_results(minion=minion):
        histories = result.get_histories(
            from_date=from_date,
            to_date=to_date)
        # javascript uses milliseconds since epoch
        js_data = []
        for key, history in histories.items():
            js_data.append({
                'label': key,
                'data': map(lambda x: (x[0] * 1000, x[1]), history),
            })
        values_type = result.values_type()
        if values_type.startswith('percentage'):
            graph_type = 'percentage'
        else:
            graph_type = values_type
        graphs.append({
            'name': result.check.name,
            'data': json.dumps(js_data),
            'type': graph_type,
        })
    if request.META.get('HTTP_X_PJAX', False):
        parent_template = 'pjax.html'
    else:
        parent_template = 'base.html'
    return render(request, 'monitor/history.html', {
        'form': form,
        'minion': minion,
        'graphs': graphs,
        'parent_template': parent_template,
        'refresh_interval_history': settings.REFRESH_INTERVAL_HISTORY,
    })
