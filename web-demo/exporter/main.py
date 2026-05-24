import os

import requests
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest

app = FastAPI(title="RabbitMQ Exporter")

QUEUE_MESSAGES = Gauge(
    "rabbitmq_queue_messages",
    "Messages ready in the RabbitMQ queue",
    ["queue"],
)

RABBITMQ_HTTP_URL = os.getenv("RABBITMQ_HTTP_URL", "http://rabbitmq:15672")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "demo")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "demo")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "task-queue")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/metrics")
def metrics() -> Response:
    queue_length = 0

    try:
      response = requests.get(
          f"{RABBITMQ_HTTP_URL}/api/queues/%2F/{RABBITMQ_QUEUE}",
          auth=(RABBITMQ_USERNAME, RABBITMQ_PASSWORD),
          timeout=5,
      )
      response.raise_for_status()
      payload = response.json()
      queue_length = int(payload.get("messages_ready", 0))
    except Exception:
      queue_length = 0

    QUEUE_MESSAGES.labels(queue=RABBITMQ_QUEUE).set(queue_length)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)