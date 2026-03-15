# Services-Mesh-Event-Driven-Scaling

## Phase 1: Setup and Install Istio with Sidecar Mode

### Prerequisites

- Docker
- kubectl
- KinD
- Helm 3.x

### Installation Steps

#### 1. Create KinD Cluster

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
networking:
  disableDefaultCNI: true
  podSubnet: "10.244.0.0/16"
```

```bash
kind create cluster --config kind-config.yaml --name istio-cluster
```

#### 2. Install Flannel CNI

```bash
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

#### 3. Setup Helm for Istio

```bash
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update
```

#### 4. Install Istio Components

```bash
# Install base
helm install istio-base istio/base \
  -n istio-system \
  --set defaultRevision=default \
  --create-namespace

# Install control plane
helm install istiod istio/istiod \
  -n istio-system \
  --wait

# Install ingress gateway
kubectl create namespace istio-ingress
helm install istio-ingress istio/gateway \
  -n istio-ingress \
  --wait
```

#### 5. Enable Sidecar Injection

```bash
kubectl label namespace default istio-injection=enabled
```

#### 6. Deploy Sample App

```bash
kubectl create namespace sample-app
kubectl label namespace sample-app istio-injection=enabled
kubectl apply -f sample-app.yaml -n sample-app
```

#### 7. Verify Installation

```bash
kubectl get pods -n istio-system
kubectl get pods -n sample-app
kubectl describe pod <pod-name> -n sample-app
```

Check for `istio-proxy` container in pods.

### Useful Commands

```bash
# Check Istio status
kubectl get ns istio-system
kubectl get pods -n istio-system

# View namespace labels
kubectl get namespace --show-labels

# Check sidecar injection
kubectl describe pod <pod-name> -n <namespace>

# View logs
kubectl logs -n istio-system -l app=istiod
```

### References

- [Istio Documentation](https://istio.io/latest/docs/)
- [KinD Documentation](https://kind.sigs.k8s.io/)