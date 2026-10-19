from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.auth import is_admin_user, is_bootstrap_admin, require_admin
from app.config import settings
from app.database import get_db
from app.job_stats import summarize_jobs
from app.models import Job, Subscription, SubscriptionStatus, User
from app.schemas import AdminJobOut, AdminStatsOut, AdminUserOut, AdminUserUpdate

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _plan_label(plan_id: str | None) -> str | None:
    if not plan_id:
        return None
    yearly = (settings.stripe_price_id_yearly or "").strip()
    monthly = (settings.stripe_price_id_monthly or settings.stripe_price_id or "").strip()
    if yearly and plan_id == yearly:
        return "Yearly"
    if monthly and plan_id == monthly:
        return "Monthly"
    return "Paid"


def _status_value(value) -> str | None:
    if value is None:
        return None
    return value.value if hasattr(value, "value") else str(value)


def _admin_user_out(user: User, job_count: int) -> AdminUserOut:
    sub = user.subscription
    return AdminUserOut(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_admin=is_admin_user(user),
        is_bootstrap_admin=is_bootstrap_admin(user),
        created_at=user.created_at,
        job_count=job_count,
        subscription_status=_status_value(sub.status) if sub else None,
        plan_id=sub.plan_id if sub else None,
        plan_label=_plan_label(sub.plan_id) if sub else None,
        current_period_end=sub.current_period_end if sub else None,
    )


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
    return [_admin_user_out(user, int(counts.get(user.id, 0))) for user in users]


@router.get("/subscribers", response_model=list[AdminUserOut])
def admin_subscribers(db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .options(joinedload(User.subscription))
        .join(User.subscription)
        .filter(Subscription.status.in_([SubscriptionStatus.active, SubscriptionStatus.trialing]))
        .order_by(Subscription.current_period_end.desc().nulls_last(), User.created_at.desc())
        .all()
    )
    counts = dict(db.query(Job.user_id, func.count(Job.id)).group_by(Job.user_id).all())
    return [_admin_user_out(user, int(counts.get(user.id, 0))) for user in users]


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_admin_user(
    user_id: UUID,
    payload: AdminUserUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.is_admin:
        user.is_admin = True
    else:
        if user.id == admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot remove your own admin access",
            )
        if is_bootstrap_admin(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account is listed in ADMIN_EMAILS on the server and cannot be removed here",
            )
        other_admins = (
            db.query(func.count(User.id))
            .filter(User.is_admin.is_(True), User.id != user.id)
            .scalar()
            or 0
        )
        if other_admins < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last admin",
            )
        user.is_admin = False

    db.add(user)
    db.commit()
    db.refresh(user)
    job_count = db.query(func.count(Job.id)).filter(Job.user_id == user.id).scalar() or 0
    return _admin_user_out(user, int(job_count))


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
