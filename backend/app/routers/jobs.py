from uuid import UUID

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_active_subscription
from app.config import settings
from app.database import get_db
from app.models import Job, JobFile, JobStatus, User
from app.queue import enqueue_snapshot_job
from app.schemas import FileDownloadOut, JobCreate, JobFileOut, JobOut
from app.storage import create_presigned_download_url, s3_configured

router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = logging.getLogger(__name__)


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db),
):
    if not payload.inputs.addresses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one address is required")

    job = Job(
        user_id=user.id,
        status=JobStatus.queued,
        source_url=payload.source_url,
        inputs=payload.inputs.model_dump(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    if settings.celery_enabled:
        try:
            enqueue_snapshot_job(str(job.id))
        except Exception as exc:
            # Job stays queued — poll worker can still pick it up as fallback.
            logger.warning("Failed to enqueue job %s: %s", job.id, exc)

    return job


@router.get("", response_model=list[JobOut])
def list_jobs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.user_id == user.id).order_by(Job.created_at.desc()).all()
    return jobs


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.get("/{job_id}/files", response_model=list[JobFileOut])
def list_job_files(job_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return db.query(JobFile).filter(JobFile.job_id == job.id).order_by(JobFile.created_at.asc()).all()


@router.get("/{job_id}/files/{file_id}/download", response_model=FileDownloadOut)
def download_job_file(
    job_id: UUID,
    file_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job_file = (
        db.query(JobFile)
        .filter(JobFile.id == file_id, JobFile.job_id == job_id, JobFile.user_id == user.id)
        .first()
    )
    if not job_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if not job_file.s3_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not available in storage")
    if not s3_configured():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="S3 is not configured")
    if not settings.aws_access_key_id or not settings.aws_secret_access_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AWS credentials not configured for download URLs",
        )

    url = create_presigned_download_url(job_file.s3_key, job_file.filename)
    return FileDownloadOut(url=url, expires_in=settings.s3_presign_expire_seconds, filename=job_file.filename)
