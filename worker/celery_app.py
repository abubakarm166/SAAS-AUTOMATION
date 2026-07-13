"""Celery application for SnapShot job processing."""

from __future__ import annotations

import os

from celery import Celery

from worker.api_client import load_worker_env

load_worker_env()

broker_url = os.getenv("CELERY_BROKER_URL", "")
if not broker_url:
    raise RuntimeError("CELERY_BROKER_URL is required for the Celery worker")

task_queue = os.getenv("CELERY_TASK_QUEUE", "snapshot_jobs")

celery_app = Celery("snapshot_worker", broker=broker_url)
celery_app.conf.update(
    task_default_queue=task_queue,
    task_routes={"worker.tasks.process_snapshot_job": {"queue": task_queue}},
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
    result_backend=None,
    imports=("worker.tasks",),
)
