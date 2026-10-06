# Dynatrace Demo - Simple Apps

Two independent Python apps generating logs, traces, and metrics with 60% success rate.

## Structure

```
app-python-demo-observabilidad/
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
├── docker-compose.yaml          # Local dev stack (NOT for kubectl)
├── deploy.sh                    # Deploy script
└── kustomization.yaml           # Root kustomization
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

## Quick Start (Local - Docker Compose)

```bash
docker-compose up --build
# Test: curl localhost:8081  (app1-jd-ns1)
# Test: curl localhost:8082  (app1-jd-ns2)
# Test: curl localhost:8083  (app2-md-ns1)
# Test: curl localhost:8084  (app2-md-ns2)
# OTel Collector logs show traces/metrics
```

## Deploy to Kubernetes

**Option 1: Use deploy script (recommended)**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Option 2: Kustomize (requires kubectl 1.14+)**
```bash
# Deploy all
kubectl apply -k .

# Or deploy individually
kubectl apply -k app1-jd/
kubectl apply -k app2-md/
```

**Option 3: Apply manifests directly**
```bash
kubectl apply -f namespaces/namespaces.yaml
kubectl apply -f app1-jd/deployments.yaml
kubectl apply -f app1-jd/services.yaml
kubectl apply -f app2-md/deployments.yaml
kubectl apply -f app2-md/services.yaml
```

## Verify Deployment

```bash
kubectl get pods -n app1-jd-ns1
kubectl get pods -n app1-jd-ns2
kubectl get pods -n app2-md-ns1
kubectl get pods -n app2-md-ns2

# Test endpoints
kubectl run -i --rm --restart=Never curl --image=curlimages/curl -- \
  curl http://app1-jd.app1-jd-ns1:8080/

kubectl run -i --rm --restart=Never curl --image=curlimages/curl -- \
  curl http://app2-md.app2-md-ns1:8080/
```

## Notes

- `docker-compose.yaml` is for local development only - **do not apply with kubectl**
- `kustomization.yaml` files are for `kubectl apply -k` not `kubectl apply -f`
- Each app is completely independent with its own namespaces
- 60% success rate, 40% error rate visible in logs, traces, and metrics