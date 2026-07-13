"""Shared job execution logic for poll and Celery workers."""

from __future__ import annotations

from typing import Any

from worker.api_client import WorkerApiClient
from worker.processor import process_job


def execute_claimed_job(client: WorkerApiClient, job: dict[str, Any]) -> dict[str, Any]:
    """Run automation for a claimed job and report success to the API."""
    job_id = str(job["id"])
    output_rows, files = process_job(job)

    from worker.s3_storage import s3_enabled, upload_job_files

    if s3_enabled():
        files = upload_job_files(job, files)

    return client.complete_job(job_id, output_rows=output_rows, files=files)


def fail_claimed_job(client: WorkerApiClient, job_id: str, error: str) -> dict[str, Any]:
    return client.fail_job(job_id, error)
