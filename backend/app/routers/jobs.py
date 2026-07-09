from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_active_subscription
from app.database import get_db
from app.models import Job, JobStatus, User
from app.schemas import JobCreate, JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


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
