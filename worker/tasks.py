"""Celery tasks for SnapShot job processing."""

from __future__ import annotations

import logging

import requests

from worker.api_client import WorkerApiClient, load_worker_env
from worker.celery_app import celery_app
from worker.job_runner import execute_claimed_job, fail_claimed_job

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="worker.tasks.process_snapshot_job",
    max_retries=2,
    autoretry_for=(requests.RequestException, ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=120,
)
def process_snapshot_job(self, job_id: str) -> str:
    """Accept a queued job by ID, run automation, and report result."""
    load_worker_env()
    client = WorkerApiClient()

    try:
        job = client.accept_job(job_id)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 409:
            logger.info("Job %s already accepted or finished; skipping", job_id)
            return "skipped"
        raise

    try:
        result = execute_claimed_job(client, job)
        logger.info("Job %s completed with status=%s", job_id, result.get("status"))
        return "completed"
    except Exception as exc:
        error = str(exc)[-4000:]
        try:
            fail_claimed_job(client, job_id, error)
        except Exception as fail_exc:
            logger.exception("Failed to report job %s failure: %s", job_id, fail_exc)
            raise self.retry(exc=exc) from exc
        logger.error("Job %s failed: %s", job_id, error)
        return "failed"
