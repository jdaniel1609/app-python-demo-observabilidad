#!/usr/bin/env python3
"""
Simple Python demo app generating logs, traces, and metrics with 60% success rate.
"""

import os
import random
import time
import logging
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

APP_NAME = os.getenv("APP_NAME", "app1-jd")
NAMESPACE = os.getenv("NAMESPACE", "ns1")
SUCCESS_RATE = float(os.getenv("SUCCESS_RATE", "0.6"))
PORT = int(os.getenv("PORT", "8080"))
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(APP_NAME)

resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: APP_NAME,
    ResourceAttributes.SERVICE_NAMESPACE: NAMESPACE,
    "deployment.environment": "demo"
})

trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True)))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(APP_NAME)

meter_provider = MeterProvider(resource=resource, metric_readers=[
    PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=OTEL_ENDPOINT, insecure=True), export_interval_millis=10000)
])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(APP_NAME)

REQUESTS = Counter(f'{APP_NAME}_requests_total', 'Total requests', ['status'])
LATENCY = Histogram(f'{APP_NAME}_latency_seconds', 'Request latency')
ERRORS = Counter(f'{APP_NAME}_errors_total', 'Total errors')

otel_requests = meter.create_counter(f"{APP_NAME}.requests", description="Requests")
otel_latency = meter.create_histogram(f"{APP_NAME}.latency", description="Latency")
otel_errors = meter.create_counter(f"{APP_NAME}.errors", description="Errors")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

def should_succeed():
    return random.random() < SUCCESS_RATE

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": APP_NAME, "ns": NAMESPACE})

@app.route("/metrics")
def metrics_ep():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route("/")
def index():
    start = time.time()
    try:
        with tracer.start_as_current_span("request") as span:
            span.set_attribute("app", APP_NAME)
            span.set_attribute("namespace", NAMESPACE)
            
            if should_succeed():
                REQUESTS.labels(status="success").inc()
                otel_requests.add(1, {"status": "success"})
                logger.info(f"Success request from {APP_NAME}/{NAMESPACE}")
                return jsonify({"ok": True, "app": APP_NAME, "ns": NAMESPACE})
            else:
                REQUESTS.labels(status="error").inc()
                ERRORS.inc()
                otel_requests.add(1, {"status": "error"})
                otel_errors.add(1)
                logger.error(f"Error request from {APP_NAME}/{NAMESPACE}")
                return jsonify({"ok": False, "error": "Random failure", "app": APP_NAME, "ns": NAMESPACE}), 500
    finally:
        dur = time.time() - start
        LATENCY.observe(dur)
        otel_latency.record(dur)

if __name__ == "__main__":
    logger.info(f"Starting {APP_NAME} in {NAMESPACE} (success={SUCCESS_RATE*100}%)")
    app.run(host="0.0.0.0", port=PORT)