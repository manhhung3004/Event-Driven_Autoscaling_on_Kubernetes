#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

command -v kubectl >/dev/null 2>&1 || { echo "Please install 'kubectl' and retry."; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "Please install 'helm' and retry."; exit 1; }

echo "Adding Helm repos..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add kedacore https://kedacore.github.io/charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

echo "Installing Istio (using istioctl)..."
if ! command -v istioctl >/dev/null 2>&1; then
  echo "Downloading istioctl..."
  curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.19.1 sh -
  export PATH="$PWD/istio-1.19.1/bin:$PATH"
fi
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled --overwrite || true

echo "Installing Knative Serving (core components via official manifests)..."
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.12.0/serving-core.yaml
kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.12.0/net-istio.yaml

echo "Installing KEDA via Helm..."
helm upgrade --install keda kedacore/keda --namespace keda --create-namespace

echo "Installing RabbitMQ via Helm with custom values..."
helm upgrade --install rabbitmq bitnami/rabbitmq --namespace messaging --create-namespace -f "${ROOT_DIR}/k8s/values-rabbitmq.yaml"

echo "Installing Prometheus + Grafana via Helm with custom values..."
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace -f "${ROOT_DIR}/k8s/values-prometheus.yaml"

echo "Waiting for core components to be ready (this may take a few minutes)..."
kubectl wait --for=condition=Ready pods --all --namespace istio-system --timeout=5m || true
kubectl wait --for=condition=Ready pods --all --namespace keda --timeout=3m || true
kubectl wait --for=condition=Ready pods --all --namespace messaging --timeout=3m || true
kubectl wait --for=condition=Ready pods --all --namespace monitoring --timeout=3m || true

echo "Component installation complete."
