from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .services import AnalyticsService
import json

def dashboard_view(request):
    service = AnalyticsService(request.user)
    stats = service.get_stats()
    weekly = service.get_weekly_data()

    context = {
        'stats': stats,
        'weekly_labels': json.dumps(weekly['labels'], ensure_ascii=False),
        'weekly_data': json.dumps(weekly['data'], ensure_ascii=False),
    }

    return render(request, 'analytics/dashboard.html', context)