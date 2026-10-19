from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db
from app.models import SubscriptionStatus, User

security = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user = db.get(User, UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    _sync_bootstrap_admin(user, db)
    return user


def require_active_subscription(user: User = Depends(get_current_user)) -> User:
    if settings.bypass_subscription_check:
        return user

    subscription = user.subscription
    if not subscription or subscription.status not in {SubscriptionStatus.active, SubscriptionStatus.trialing}:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Active subscription required")
    return user


def admin_email_set() -> set[str]:
    return {email.strip().lower() for email in settings.admin_emails.split(",") if email.strip()}


def is_bootstrap_admin(user: User) -> bool:
    return user.email.lower() in admin_email_set()


def is_admin_user(user: User) -> bool:
    return bool(getattr(user, "is_admin", False)) or is_bootstrap_admin(user)


def _sync_bootstrap_admin(user: User, db: Session) -> None:
    if user.is_admin or not is_bootstrap_admin(user):
        return
    user.is_admin = True
    db.add(user)
    db.commit()
    db.refresh(user)


def seed_bootstrap_admins() -> None:
    emails = admin_email_set()
    if not emails:
        return
    db = SessionLocal()
    try:
        db.query(User).filter(User.email.in_(emails), User.is_admin.is_(False)).update(
            {User.is_admin: True},
            synchronize_session=False,
        )
        db.commit()
    finally:
        db.close()


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not is_admin_user(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
