# Django Prometheus Metrics Exporter

A Django application that demonstrates how to serve custom multi-process Prometheus metrics from a Django application.

## Overview

This project provides a simple yet powerful way to expose API transaction metrics to Prometheus from a Django application running in a multi-process environment (e.g., under uWSGI). It shows how to:

1. Set up a Django application to collect metrics
2. Configure multi-process metric collection
3. Aggregate transaction data
4. Expose metrics through a custom endpoint

## Features

- Track API transactions by API name and status
- Aggregate metrics from the past 24 hours
- Support for multi-process metric collection
- Compatible with uWSGI deployment
- Simple database models for tracking transactions

## Project Structure

```
django-prometheus-metrics/
├── apiMetrics/                  # Django app for metrics collection
│   ├── migrations/              # Database migrations
│   ├── models.py                # API, Transaction, and TransactionStatus models
│   ├── views.py                 # Metrics view for Prometheus
│   └── admin.py                 # Admin interface configuration
├── config/                      # Django project configuration
│   ├── settings.py              # Project settings
│   ├── urls.py                  # URL routing
│   └── wsgi.py                  # WSGI configuration
├── populate_db.py               # Script to populate test data
├── requirements.txt             # Python dependencies
├── uwsgi.ini                    # uWSGI configuration
└── manage.py                    # Django management script
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/django-prometheus-metrics.git
   cd django-prometheus-metrics
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser for the admin interface:
   ```bash
   python manage.py createsuperuser
   ```

5. Populate the database with test data:
   ```bash
   python populate_db.py
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Setting Up Multi-Process Metrics Collection

For multi-process environments like uWSGI, standard Prometheus client implementations don't work out of the box because each process collects metrics independently. The solution is to use a directory where all processes can write their metrics, which can then be aggregated.

### Step 1: Configure the Environment Variable

You must set the `PROMETHEUS_MULTIPROC_DIR` environment variable to a directory where all processes can write their metrics:

```bash
export PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_METRICS/
mkdir -p $PROMETHEUS_MULTIPROC_DIR
```

For uWSGI, this is set in the `uwsgi.ini` file:

```ini
env=PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_METRICS/
```

### Step 2: Clean the Directory on Startup

Ensure the directory is cleaned on application startup to avoid issues with stale metrics.

### Step 3: Implement the Metrics Endpoint

The metrics endpoint is implemented in `apiMetrics/views.py`. The key parts are:

```python
def api_metrics(request):
    # Create a registry and set up the multi-process collector
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)

    # Define gauge with labels for API and status
    labels = ['api', 'status']
    gauge = Gauge("api_transactions", "API Transactions", labels, registry=registry)

    # Get transactions from the last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    transactions = Transaction.objects.filter(time_modified__gte=yesterday)
    
    # Aggregate transactions by API and status
    aggregates = defaultdict(int)
    for t in transactions:
        aggregates[(t.api.name, t.status.name)] += 1  
        
    # Set gauge values for each combination of API and status
    for key in aggregates.keys():
        label_values = zip(labels, key)
        label_values = {l:v for l,v in label_values}
        value = aggregates[key]
        gauge.labels(**label_values).set(value)

    # Generate and return metrics
    metrics_page = generate_latest(registry)
    return HttpResponse(metrics_page, content_type=CONTENT_TYPE_LATEST)
```

## Data Models

The application uses three main models:

1. **API**: Represents different APIs being monitored
   - `name`: Name of the API
   - `description`: Description of the API
   - `params`: JSON field for API parameters

2. **TransactionStatus**: Represents possible transaction statuses
   - `name`: Status name (e.g., "TimedOut", "Pending", "Processing")
   - `description`: Description of the status

3. **Transaction**: Represents individual API transactions
   - `amount`: Transaction amount
   - `api`: Foreign key to the API model
   - `status`: Foreign key to the TransactionStatus model
   - `time_created`: When the transaction was created
   - `time_modified`: When the transaction was last modified

## Deployment with uWSGI

To deploy the application with uWSGI, use the provided `uwsgi.ini` configuration:

```ini
[uwsgi]
chdir= /home/exporter/
module=config.wsgi:application
socket = 0.0.0.0:8000 
master = true
processes = 4
pidfile=master.pid
buffer-size=65535
env=PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_METRICS/
```

Start uWSGI with:

```bash
uwsgi --ini uwsgi.ini
```

## Prometheus Configuration

Add the following job to your Prometheus configuration to scrape metrics from the Django application:

```yaml
scrape_configs:
  - job_name: 'django-api-metrics'
    scrape_interval: 15s
    static_configs:
      - targets: ['your-server-ip:8000']
    metrics_path: /metrics
```

## Sample Metrics

The application exposes metrics in the following format:

```
# HELP api_transactions API Transactions
# TYPE api_transactions gauge
api_transactions{api="Mpesa Express",status="Pending"} 5.0
api_transactions{api="Mpesa Express",status="Processing"} 8.0
api_transactions{api="Mpesa B2C",status="Processed"} 12.0
api_transactions{api="Mpesa B2C",status="Failed"} 3.0
```

## Security Considerations

For production deployment:

1. Update `settings.py` with:
   - Set `DEBUG = False`
   - Change `SECRET_KEY` to a secure value
   - Update `ALLOWED_HOSTS` with your domain names

2. Consider adding authentication to the metrics endpoint if it's exposed publicly.

3. Ensure the `PROMETHEUS_MULTIPROC_DIR` directory has appropriate permissions.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


