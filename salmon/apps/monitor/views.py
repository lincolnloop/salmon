from django.shortcuts import render

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
    return render(request, 'monitor/dashboard.html',
                            {'minions': minions,
                             'parent_template': parent_template})
