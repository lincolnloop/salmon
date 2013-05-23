import os
import datetime
import json
from django.shortcuts import render, get_object_or_404
from . import models


def dashboard(request):
    """Shows the latest results for each minion"""
    minions = {}
    active_checks = (models.Check.objects.filter(active=True)
                                         .values_list('pk', flat=True))
    # For each minion, gets the newest result for every active check
    latest_results = models.Result.objects.raw("""
        SELECT id, check_id, MAX("timestamp")
        FROM "monitor_result"
        GROUP BY "monitor_result"."minion_id", "monitor_result"."check_id"
        HAVING check_id IN {};""".format(tuple(active_checks)))
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
    active_checks = (models.Check.objects.filter(active=True)
                                         .values_list('pk', flat=True))
    # Get the newest result for every active check
    latest_results = models.Result.objects.raw("""
        SELECT id, check_id, MAX("timestamp")
        FROM "monitor_result"
        GROUP BY "monitor_result"."minion_id", "monitor_result"."check_id"
        HAVING minion_id={} AND check_id IN {};""".format(
        minion.pk, tuple(active_checks)))
    for result in latest_results:
        # create test databases
        #db_file = os.path.join(settings.SALMON_WHISPER_DB_PATH,
        #                       result.whisper_filename)
        #graph.create_test_database(db_file)
        history = result.get_history(from_date=since)
        # javascript uses milliseconds since epoch
        js_data = map(lambda x: (x[0] * 1000, x[1]), history)
        graphs.append({
            'name': result.check.name,
            'data': json.dumps(js_data),
        })
    if request.META.get('HTTP_X_PJAX', False):
        parent_template = 'pjax.html'
    else:
        parent_template = 'base.html'
    return render(request, 'monitor/history.html', {
        'minion': minion,
        'graphs': graphs,
        'parent_template': parent_template,
    })
