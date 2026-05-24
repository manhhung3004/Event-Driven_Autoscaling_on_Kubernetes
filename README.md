## Event-Driven Autoscaling on Kubernetes — Tóm tắt

Repo này minh họa một môi trường trên máy local (Kind) để demo autoscaling dựa trên sự kiện, kết hợp:

- Service mesh: Istio
- Serverless: Knative Serving (hoặc Kourier)
- Event-driven autoscaling: KEDA
- Message broker: RabbitMQ (Bitnami Helm chart)
- Giám sát: Prometheus + Grafana

README này được chỉnh cho đúng cấu trúc của repository và thêm hướng dẫn build/deploy `web-demo` (ứng dụng demo).

**Yêu cầu (local)**

- Docker
- kind (v0.20+)
- kubectl
- helm 3
- istioctl (nếu bạn muốn dùng Istio demo profile; các script có thể tự tải nếu chưa có)

**Cấu trúc chính**

- `scripts/` — helper scripts để tạo Kind và cài component (`create-cluster.sh`, `install-components.sh`, ...)
- `k8s/` — cấu hình Helm values và cấu hình cluster-level dùng bởi các script cài đặt
- `web-demo/` — ứng dụng demo (API, worker, exporter) cùng manifests trong `web-demo/k8s/`
- `docker/` — docker-compose cho RabbitMQ (tùy chọn, local)

## Nhanh: tạo cluster và cài component (tự động)

1. Cho phép thực thi script và tạo cluster:

```bash
chmod +x scripts/*.sh
./scripts/create-cluster.sh
```

2. Cài các component chính (Istio, Knative, KEDA, RabbitMQ, Prometheus/Grafana):

```bash
./scripts/install-components.sh
```

Ghi chú: các script đã chứa các lệnh `helm` và `kubectl apply`. Nếu bạn thích cài thủ công, xem phần tiếp theo.

## Build ảnh Docker cho `web-demo`

Các image mặc định được tham chiếu trong manifests là:

- `mahhhuhh/event-demo-api:1.0.0`
- `mahhhuhh/event-demo-worker:1.0.0`
- `mahhhuhh/rabbitmq-exporter:1.0.0`

Build và (tùy chọn) load vào Kind:

```bash
docker build -t mahhhuhh/event-demo-api:1.0.0 -f web-demo/api/Dockerfile web-demo/api
docker build -t mahhhuhh/event-demo-worker:1.0.0 -f web-demo/worker/Dockerfile web-demo/worker
docker build -t mahhhuhh/rabbitmq-exporter:1.0.0 -f web-demo/exporter/Dockerfile web-demo/exporter

# Nếu dùng kind, load ảnh vào cluster
kind load docker-image mahhhuhh/event-demo-api:1.0.0 --name eda-cluster
kind load docker-image mahhhuhh/event-demo-worker:1.0.0 --name eda-cluster
kind load docker-image mahhhuhh/rabbitmq-exporter:1.0.0 --name eda-cluster
```

## Triển khai `web-demo` lên cluster

1. Tạo namespace demo:

```bash
kubectl apply -f web-demo/k8s/namespace.yaml
```

2. Triển khai ứng dụng và exporter:

```bash
kubectl apply -f web-demo/k8s/applications/
kubectl apply -f web-demo/k8s/exporter/
```

3. Triển khai KEDA ScaledObject (điều chỉnh `web-demo/k8s/keda-scaledobject.yaml` nếu cần):

```bash
kubectl apply -f web-demo/k8s/keda-scaledobject.yaml
```

## Kiểm tra

- Xem pods: `kubectl get pods -n demo`
- Xem Knative services: `kubectl get ksvc -n demo`
- Xem ScaledObjects: `kubectl get scaledobjects.keda.sh -n demo`
- Exporter metrics: `kubectl port-forward svc/rabbitmq-exporter -n demo 8000:8000` và truy cập `http://localhost:8000/metrics`
- Grafana: `kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80`

## Tùy chọn: chạy RabbitMQ bằng docker-compose (tại local)

```bash
docker compose -f docker/docker-compose.rabbit-management.yml up -d
```

Sau đó chỉnh `web-demo/k8s/keda-scaledobject.yaml` hoặc các `ConfigMap`/`Secret` để trỏ đến host/credentials phù hợp.

## Gợi ý dùng API demo

- API (FastAPI) cung cấp endpoint `POST /jobs` để đẩy message vào queue. Nếu chạy trong cluster, dùng Knative URL hoặc port-forward service.
- Worker tiêu thụ message và xuất metrics Prometheus (port mặc định `8001` trong container).

## Lưu ý và sửa lỗi nhỏ đã bắt gặp

- Thư mục script trong repo là `scripts/` (không phải `script/`) — các tham chiếu đã được cập nhật trong README.
- Manifests demo nằm trong `web-demo/k8s/` và sử dụng image tag `mahhhuhh/*:1.0.0` theo mặc định.

## Muốn mình làm tiếp?

- Mình có thể: thêm script build&deploy tự động, đổi thành Helm chart cho `web-demo`, hoặc viết demo producer/consumer để dễ test (bạn chọn).

---
