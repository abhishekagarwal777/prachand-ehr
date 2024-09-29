from prometheus_client import CollectorRegistry, Gauge, generate_latest
from prometheus_client.exposition import generate_latest
import prometheus_client
import os

class MeterRegistryCustomizerConfiguration:
    def __init__(self):
        self.application_name = os.getenv('SPRING_APPLICATION_NAME', 'default_application_name')
        self.registry = CollectorRegistry()
        self._setup_metrics()

    def _setup_metrics(self):
        self.application_gauge = Gauge(
            'application_info',
            'Application metrics',
            labelnames=['application'],
            registry=self.registry
        )
        self.application_gauge.labels(application=self.application_name).set(1)

    def get_metrics(self):
        return generate_latest(self.registry)

# Usage
metrics_config = MeterRegistryCustomizerConfiguration()
print(metrics_config.get_metrics())
