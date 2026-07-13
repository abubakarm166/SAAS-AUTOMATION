"""Publish snapshot jobs to the Celery broker (Redis)."""

from __future__ import annotations

import logging

from celery import Celery

from app.config import settings

logger = logging.getLogger(__name__)

_producer: Celery | None = None


def _get_producer() -> Celery:
    global _producer
    if _producer is None:
        if not settings.celery_broker_url:
            raise RuntimeError("CELERY_BROKER_URL is not configured")
        _producer = Celery("snapshot_producer", broker=settings.celery_broker_url)
    return _producer


def enqueue_snapshot_job(job_id: str) -> None:
    """Send a job to the Windows Celery worker queue."""
    producer = _get_producer()
    producer.send_task(
        "worker.tasks.process_snapshot_job",
        args=[job_id],
        queue=settings.celery_task_queue,
    )
    logger.info("Enqueued snapshot job %s on queue %s", job_id, settings.celery_task_queue)
