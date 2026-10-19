from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.auth import is_admin_user, require_admin
from app.database import get_db
from app.job_stats import summarize_jobs
from app.models import Job, Subscription, SubscriptionStatus, User
from app.schemas import AdminJobOut, AdminStatsOut, AdminUserOut

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/stats", response_model=AdminStatsOut)
def admin_stats(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    base = summarize_jobs(jobs, days=14)
    users_total = db.query(func.count(User.id)).scalar() or 0
    subscribers_active = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.status.in_([SubscriptionStatus.active, SubscriptionStatus.trialing]))
        .scalar()
        or 0
    )
    return AdminStatsOut(
        **base.model_dump(),
        users_total=users_total,
        subscribers_active=subscribers_active,
    )


@router.get("/users", response_model=list[AdminUserOut])
def admin_users(db: Session = Depends(get_db)):
    users = db.query(User).options(joinedload(User.subscription)).order_by(User.created_at.desc()).all()
    counts = dict(db.query(Job.user_id, func.count(Job.id)).group_by(Job.user_id).all())
    return [
        AdminUserOut(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            is_admin=is_admin_user(user),
            created_at=user.created_at,
            job_count=int(counts.get(user.id, 0)),
            subscription_status=user.subscription.status.value if user.subscription else None,
        )
        for user in users
    ]


@router.get("/jobs", response_model=list[AdminJobOut])
def admin_jobs(db: Session = Depends(get_db)):
    jobs = (
        db.query(Job)
        .options(joinedload(Job.user))
        .order_by(Job.created_at.desc())
        .limit(500)
        .all()
    )
    return [
        AdminJobOut(
            id=job.id,
            user_id=job.user_id,
            user_email=job.user.email,
            status=job.status.value if hasattr(job.status, "value") else str(job.status),
            source_url=job.source_url,
            inputs=job.inputs or {},
            error_message=job.error_message,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at,
        )
        for job in jobs
    ]
