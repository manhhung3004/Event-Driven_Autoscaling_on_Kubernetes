import json
import os
from typing import Any

import aio_pika
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

app = FastAPI(title="Event Demo API")

JOBS_ENQUEUED = Counter("api_jobs_enqueued_total", "Jobs enqueued by the API")
JOBS_FAILED = Counter("api_jobs_failed_total", "Jobs failed to enqueue by the API")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "demo")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "demo")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "task-queue")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "api", "status": "ok"}


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/jobs")
async def create_job(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    message_body = json.dumps(payload or {}).encode("utf-8")

    try:
        connection = await aio_pika.connect_robust(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            login=RABBITMQ_USERNAME,
            password=RABBITMQ_PASSWORD,
        )
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(RABBITMQ_QUEUE, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=queue.name,
            )
        JOBS_ENQUEUED.inc()
        return {"message": "Job queued", "queue": RABBITMQ_QUEUE, "payload": payload or {}}
    except Exception as exc:  # pragma: no cover - simple demo failure path
        JOBS_FAILED.inc()
        raise HTTPException(status_code=500, detail=f"Failed to enqueue job: {exc}") from exc
