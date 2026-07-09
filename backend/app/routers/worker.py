from datetime import datetime, timezone
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
