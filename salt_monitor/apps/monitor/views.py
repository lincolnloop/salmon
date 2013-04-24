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

    return render(request, 'monitor/dashboard.html', {'minions': minions})