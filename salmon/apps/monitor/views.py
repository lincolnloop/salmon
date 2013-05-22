import os
import datetime
import json
from django.shortcuts import render, get_object_or_404
from . import models


def dashboard(request):
    """Shows the latest results for each minion"""
    minions = {}
    latest_results = []
    for check in models.Check.objects.filter(active=True):
        try:
            result = (models.Result.objects.filter(check_id=check.pk)
                                           .order_by("-timestamp")[0])
        except IndexError:
            continue

        latest_results.append(result)
        for result in latest_results:
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
    since = datetime.datetime.now() - datetime.timedelta(hours=12)
    graphs = []
    latest_results = []
    for check in models.Check.objects.filter(active=True):
        try:
            result = (models.Result.objects.filter(check_id=check.pk,
                                                   minion_id=minion.pk)
                                           .order_by("-timestamp")[0])
        except IndexError:
            continue

        latest_results.append(result)

        if latest_results:
            # create test databases
            #db_file = os.path.join(settings.SALMON_WHISPER_DB_PATH,
            #                       result[0].whisper_filename)
            #graph.create_test_database(db_file)
            history = latest_results[0].get_history(from_date=since)
            # javascript uses milliseconds since epoch
            js_data = map(lambda x: (x[0] * 1000, x[1]), history)
            graphs.append({
                'name': latest_results[0].check.name,
                'data': json.dumps(js_data),
            })

    return render(request, 'monitor/history.html', {
        'minion': minion,
        'graphs': graphs,
    })
