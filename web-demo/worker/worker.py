import json
import os
import time

import pika
from prometheus_client import Counter, Gauge, start_http_server

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "demo")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "demo")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "task-queue")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8001"))

JOBS_PROCESSED = Counter("worker_jobs_processed_total", "Jobs processed by the worker")
JOBS_FAILED = Counter("worker_jobs_failed_total", "Jobs failed by the worker")
JOBS_IN_PROGRESS = Gauge("worker_jobs_in_progress", "Jobs currently being processed")


def handle_message(channel, method, properties, body) -> None:
    JOBS_IN_PROGRESS.inc()
    try:
        payload = json.loads(body.decode("utf-8"))
        print(f"[worker] start processing: {payload}", flush=True)
        time.sleep(10)
        print(f"[worker] finished processing: {payload}", flush=True)
        JOBS_PROCESSED.inc()
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as exc:
        JOBS_FAILED.inc()
        print(f"[worker] failed processing message: {exc}", flush=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    finally:
        JOBS_IN_PROGRESS.dec()


def main() -> None:
    start_http_server(METRICS_PORT)
    print(f"[worker] metrics server started on :{METRICS_PORT}", flush=True)

    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=30,
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=handle_message)

    print(f"[worker] waiting for messages on queue '{RABBITMQ_QUEUE}'", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
