import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.config import settings
from app.database import get_db
from app.email_service import send_email, smtp_configured
from app.models import PasswordResetToken, Subscription, User
from app.schemas import (
    ForgotPasswordRequest,
    MessageOut,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserLogin,
    UserOut,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    db.add(Subscription(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/forgot-password", response_model=MessageOut)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Always returns the same message to avoid email enumeration."""
    generic = MessageOut(
        message="If an account exists for that email, a password reset link has been sent."
    )
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not user.is_active:
        return generic

    # Invalidate previous unused tokens
    now = datetime.now(timezone.utc)
    for old in (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .all()
    ):
        old.used_at = now

    raw_token = secrets.token_urlsafe(32)
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            expires_at=now + timedelta(minutes=settings.password_reset_expire_minutes),
        )
    )
    db.commit()

    reset_url = f"{settings.frontend_url.rstrip('/')}/reset-password?token={raw_token}"
    body = (
        "You requested a password reset for your SnapShot account.\n\n"
        f"Open this link to set a new password (expires in {settings.password_reset_expire_minutes} minutes):\n"
        f"{reset_url}\n\n"
        "If you did not request this, you can ignore this email.\n"
    )

    sent = send_email(to=user.email, subject="SnapShot — Reset your password", body=body)
    if not sent:
        # Still usable in ops: log the link when SMTP is missing (dev / misconfig).
        logger.warning(
            "Password reset created for %s but email was not sent (SMTP configured=%s). Reset URL: %s",
            user.email,
            smtp_configured(),
            reset_url,
        )

    return generic


@router.post("/reset-password", response_model=MessageOut)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = _hash_token(payload.token.strip())
    row = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == token_hash)
        .first()
    )
    now = datetime.now(timezone.utc)
    if not row or row.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset link")

    expires = row.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset link")

    user = db.get(User, row.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset link")

    user.password_hash = hash_password(payload.password)
    row.used_at = now
    db.commit()
    return MessageOut(message="Password updated. You can sign in with your new password.")
