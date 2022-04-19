from prometheus_client import Gauge, Info, Summary


class Metrics(object):
    # Instance info
    app = Info(name="app", documentation="Service information")

    # API Request metrics
    app_api_latency_seconds = Summary(
        name="app_api_latency_seconds",
        documentation="API request time in seconds",
        labelnames=["method", "alias", "status_code"],
    )
    app_api_connection_total = Gauge(
        name="app_api_connection_total",
        documentation="API concurrent connection count",
        labelnames=[],
    )


def update_latest(version):
    Metrics.app.info({"version": version})
