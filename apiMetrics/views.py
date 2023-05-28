from datetime import datetime, timedelta
from collections import defaultdict

from prometheus_client import(
    generate_latest,
    CollectorRegistry,
    multiprocess, 
    CONTENT_TYPE_LATEST,
    Gauge)

from django.http import HttpResponse
from django.shortcuts import render
from .models import *

# Create your views here.
def api_metrics(request):
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)

    labels = ['api','status']
    gauge = Gauge("api_transactions", "API Transactions", labels, registry=registry)

    yesterday = datetime.now() - timedelta(days=1)
    transactions = Transaction.objects.filter(time_modified__gte=yesterday)
    
    aggregates = defaultdict(int)
    for t in transactions:
        aggregates[(t.api.name, t.status.name)] += 1  
        
    for key in aggregates.keys():
        label_values =  zip(labels, key)
        label_values = {l:v for l,v in label_values}

        value = aggregates[key]
        gauge.labels(**label_values).set(value)

    metrics_page = generate_latest(registry)
    return HttpResponse(
		metrics_page, content_type=CONTENT_TYPE_LATEST)








