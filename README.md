# Dynatrace Demo - Simple Apps

Two independent Python apps generating logs, traces, and metrics with 60% success rate.

## Structure

```
app-demo-dynatrace/
├── namespaces/namespaces.yaml   # 4 namespaces
├── app1-jd/                     # App 1 (2 namespaces, 1 replica each)
│   ├── deployments.yaml
│   ├── services.yaml
│   └── kustomization.yaml
├── app2-md/                     # App 2 (2 namespaces, 1 replica each)
│   ├── deployments.yaml
│   ├── services.yaml
│   └── kustomization.yaml
├── configs/
│   ├── app.py                   # Simple Flask app
│   ├── Dockerfile
│   ├── requirements.txt
│   └── otel-collector-config.yaml
├── docker-compose.yaml          # Local dev stack
└── kustomization.yaml
```

## Apps

| App | Namespaces | Port | Success Rate |
|-----|------------|------|--------------|
| app1-jd | app1-jd-ns1, app1-jd-ns2 | 8080 | 60% |
| app2-md | app2-md-ns1, app2-md-ns2 | 8080 | 60% |

## What Each App Does

- **Single endpoint** `/` - Returns success (60%) or error (40%)
- **Logs** - Structured logging with app/namespace
- **Traces** - OpenTelemetry span per request via OTLP/gRPC
- **Metrics** - Prometheus at `/metrics` + OTel metrics

## Quick Start (Local)

```bash
docker-compose up --build
# Test: curl localhost:8081  (app1-jd-ns1)
# Test: curl localhost:8082  (app1-jd-ns2)
# Test: curl localhost:8083  (app2-md-ns1)
# Test: curl localhost:8084  (app2-md-ns2)
# OTel Collector logs show traces/metrics
```

## Deploy to Kubernetes

```bash
# All
kubectl apply -k .

# Individual
kubectl apply -k app1-jd
kubectl apply -k app2-md
```

## Verify

```bash
kubectl get pods -n app1-jd-ns1
kubectl get pods -n app2-md-ns1
curl http://app1-jd.app1-jd-ns1:8080/
curl http://app2-md.app2-md-ns1:8080/
```

Each request has 60% chance of success, 40% error - visible in logs, traces, and metrics.