#!/usr/bin/env bash
set -euo pipefail

# Edit these versions if you need a different Knative release
KNATIVE_VERSION="v1.12.0"
KOURIER_VERSION="knative-net-kourier-1.12.0"

echo "=== Installing KEDA ==="
kubectl create namespace keda --dry-run=client -o yaml | kubectl apply -f -
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda --namespace keda --create-namespace || echo "KEDA already installed or helm install failed"

echo "=== Installing Knative Serving (CRDs + Core) ==="
kubectl apply -f "https://github.com/knative/serving/releases/download/knative-${KNATIVE_VERSION}/serving-crds.yaml"
kubectl apply -f "https://github.com/knative/serving/releases/download/knative-${KNATIVE_VERSION}/serving-core.yaml"

echo "=== Installing Kourier (Knative networking layer) ==="
kubectl apply -f "https://github.com/knative/net-kourier/releases/download/${KOURIER_VERSION}/kourier.yaml"
kubectl -n knative-serving patch configmap/config-network --type merge -p '{"data":{"ingress.class":"kourier.ingress.networking.knative.dev"}}' || true

echo "=== (Optional) Installing Knative Eventing ==="
kubectl apply -f "https://github.com/knative/eventing/releases/download/knative-${KNATIVE_VERSION}/eventing-crds.yaml" || true
kubectl apply -f "https://github.com/knative/eventing/releases/download/knative-${KNATIVE_VERSION}/eventing-core.yaml" || true

echo "Waiting for Knative and KEDA pods to be ready (may take a few minutes)"
kubectl wait --for=condition=ready pod --all -n keda --timeout=300s || true
kubectl wait --for=condition=ready pod --all -n knative-serving --timeout=600s || true
kubectl wait --for=condition=ready pod --all -n knative-eventing --timeout=600s || true

echo "=== Status ==="
kubectl get pods -n keda
kubectl get pods -n knative-serving
kubectl get pods -n knative-eventing || true

echo "Installation script finished. If any pods are not Ready, check logs and events."
