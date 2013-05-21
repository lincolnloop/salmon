import datetime
from django.shortcuts import render, get_object_or_404

from . import models


def dashboard(request):
    """Shows the latest results for each minion"""
    minions = {}
    for check in models.Check.objects.filter(active=True):
        latest_results = models.Result.objects.filter(check=check,
                                                      timestamp=check.last_run)
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
    # FIXME: this is a horrible way to get all the results for a minion
    for check in models.Check.objects.filter(active=True):
        result = check.result_set.filter(minion=minion,
                                         timestamp=check.last_run)
        if result:
            graphs.append({
                'name': result[0].check.name,
                'data': result[0].get_history(from_date=since),
            })

    return render(request, 'monitor/history.html', {
        'minion': minion,
        'graphs': graphs,
    })
