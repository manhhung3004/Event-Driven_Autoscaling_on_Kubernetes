#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

CLUSTER_NAME="eda-cluster"

command -v kind >/dev/null 2>&1 || {
  echo "Please install 'kind' and retry."
  exit 1
}

command -v kubectl >/dev/null 2>&1 || {
  echo "Please install 'kubectl' and retry."
  exit 1
}

if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  echo "Kind cluster '${CLUSTER_NAME}' already exists. Skipping create."
else
  echo "Creating kind cluster '${CLUSTER_NAME}'..."

  kind create cluster \
    --name "${CLUSTER_NAME}" \
    --config "${ROOT_DIR}/k8s/kind-cluster.yaml" \
    --image kindest/node:v1.28.0
fi

echo "Cluster info:"
kubectl cluster-info --context "kind-${CLUSTER_NAME}" || true

echo "Nodes:"
kubectl get nodes

echo "System pods:"
kubectl get pods -A

echo "Exporting kubeconfig for cluster '${CLUSTER_NAME}'..."
sudo kind export kubeconfig --name eda-cluster

echo "Setting up kubeconfig for current user..."
mkdir -p ~/.kube
sudo cp /root/.kube/config ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config
