from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import FileType, Job, JobFile, JobStatus, Log, OutputRow
from app.schemas_worker import JobCompletePayload, JobFailPayload, WorkerJobOut

router = APIRouter(prefix="/worker", tags=["worker"])


def verify_worker_key(x_worker_api_key: str = Header(...)) -> None:
    if not settings.worker_api_key or x_worker_api_key != settings.worker_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid worker key")


@router.post("/jobs/claim", response_model=WorkerJobOut | None)
def claim_next_job(
    _: None = Depends(verify_worker_key),
    db: Session = Depends(get_db),
):
    job = (
        db.query(Job)
        .filter(Job.status == JobStatus.queued)
        .order_by(Job.created_at.asc())
        .with_for_update(skip_locked=True)
        .first()
    )
    if not job:
        return None

    job.status = JobStatus.running
    job.started_at = datetime.now(timezone.utc)
    db.add(Log(user_id=job.user_id, job_id=job.id, level="info", message="Job claimed by worker"))
    db.commit()
    db.refresh(job)
    return job


@router.post("/jobs/{job_id}/accept", response_model=WorkerJobOut)
def accept_job(
    job_id: UUID,
    _: None = Depends(verify_worker_key),
    db: Session = Depends(get_db),
):
    """Claim a specific job by ID (used by Celery workers)."""
    job = db.query(Job).filter(Job.id == job_id).with_for_update().first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.status != JobStatus.queued:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job is not queued")

    job.status = JobStatus.running
    job.started_at = datetime.now(timezone.utc)
    db.add(Log(user_id=job.user_id, job_id=job.id, level="info", message="Job accepted by Celery worker"))
    db.commit()
    db.refresh(job)
    return job


@router.post("/jobs/recover-stale")
def recover_stale_jobs(
    _: None = Depends(verify_worker_key),
    db: Session = Depends(get_db),
):
    """Requeue jobs stuck in running longer than celery_stale_job_seconds."""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.celery_stale_job_seconds)
    stale_jobs = (
        db.query(Job)
        .filter(Job.status == JobStatus.running, Job.started_at.isnot(None), Job.started_at < cutoff)
        .all()
    )
    recovered = []
    for job in stale_jobs:
        job.status = JobStatus.queued
        job.started_at = None
        db.add(
            Log(
                user_id=job.user_id,
                job_id=job.id,
                level="warning",
                message="Job requeued after worker timeout",
            )
        )
        recovered.append(str(job.id))

    if recovered:
        db.commit()
        if settings.celery_enabled:
            from app.queue import enqueue_snapshot_job

            for job_id in recovered:
                try:
                    enqueue_snapshot_job(job_id)
                except Exception:
                    pass

    return {"recovered": recovered, "count": len(recovered)}


@router.post("/jobs/{job_id}/complete", response_model=WorkerJobOut)
def complete_job(
    job_id: UUID,
    payload: JobCompletePayload,
    _: None = Depends(verify_worker_key),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.status not in {JobStatus.running, JobStatus.queued}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job is not runnable")

    for row in payload.output_rows:
        db.add(OutputRow(user_id=job.user_id, job_id=job.id, row_data=row))

    for file_info in payload.files:
        file_type = file_info.get("file_type", "pdf")
        db.add(
            JobFile(
                user_id=job.user_id,
                job_id=job.id,
                file_type=FileType(file_type),
                s3_key=file_info.get("s3_key"),
                filename=file_info.get("filename", "report.pdf"),
            )
        )

    job.status = JobStatus.completed
    job.completed_at = datetime.now(timezone.utc)
    job.error_message = None
    db.add(Log(user_id=job.user_id, job_id=job.id, level="info", message="Job completed"))
    db.commit()
    db.refresh(job)
    return job


@router.post("/jobs/{job_id}/fail", response_model=WorkerJobOut)
def fail_job(
    job_id: UUID,
    payload: JobFailPayload,
    _: None = Depends(verify_worker_key),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.status not in {JobStatus.running, JobStatus.queued}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job is not runnable")

    job.status = JobStatus.failed
    job.completed_at = datetime.now(timezone.utc)
    job.error_message = payload.error_message
    db.add(Log(user_id=job.user_id, job_id=job.id, level="error", message=payload.error_message))
    db.commit()
    db.refresh(job)
    return job
