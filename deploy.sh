#!/bin/bash
# Deploy script for Kubernetes

echo "Deploying namespaces..."
kubectl apply -f namespaces/namespaces.yaml

echo "Deploying app1-jd..."
kubectl apply -k app1-jd/

echo "Deploying app2-md..."
kubectl apply -k app2-md/

echo "Done! Verify with:"
echo "  kubectl get pods -n app1-jd-ns1"
echo "  kubectl get pods -n app1-jd-ns2"
echo "  kubectl get pods -n app2-md-ns1"
echo "  kubectl get pods -n app2-md-ns2"