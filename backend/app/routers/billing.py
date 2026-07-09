from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import stripe

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Subscription, SubscriptionStatus, User
from app.schemas import SubscriptionOut

router = APIRouter(prefix="/billing", tags=["billing"])

if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


def _map_stripe_status(status: str) -> SubscriptionStatus:
    try:
        return SubscriptionStatus(status)
    except ValueError:
        return SubscriptionStatus.incomplete


def _sync_stripe_subscription(db: Session, stripe_sub: dict) -> None:
    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub["id"]).first()
    if not sub and stripe_sub.get("customer"):
        sub = db.query(Subscription).filter(Subscription.stripe_customer_id == stripe_sub["customer"]).first()
    if not sub:
        return

    sub.stripe_subscription_id = stripe_sub["id"]
    sub.stripe_customer_id = stripe_sub.get("customer") or sub.stripe_customer_id
    sub.status = _map_stripe_status(stripe_sub.get("status", "incomplete"))

    items = stripe_sub.get("items", {}).get("data", [])
    if items:
        sub.plan_id = items[0].get("price", {}).get("id")

    period_end = stripe_sub.get("current_period_end")
    if period_end:
        sub.current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc)

    db.commit()


@router.get("/subscription", response_model=SubscriptionOut)
def get_subscription(user: User = Depends(get_current_user)):
    if not user.subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subscription found")
    return user.subscription


@router.post("/checkout-session")
def create_checkout_session(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not settings.stripe_secret_key or not settings.stripe_price_id:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe not configured")

    subscription = user.subscription
    if not subscription:
        subscription = Subscription(user_id=user.id)
        db.add(subscription)
        db.commit()
        db.refresh(subscription)

    if not subscription.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, metadata={"user_id": str(user.id)})
        subscription.stripe_customer_id = customer.id
        db.commit()

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=subscription.stripe_customer_id,
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        success_url=f"{settings.frontend_url}/billing/success",
        cancel_url=f"{settings.frontend_url}/billing/cancel",
        metadata={"user_id": str(user.id)},
    )
    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe webhook not configured")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook") from exc

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")

        sub = None
        if user_id:
            sub = db.query(Subscription).filter(Subscription.user_id == UUID(user_id)).first()
        if not sub and customer_id:
            sub = db.query(Subscription).filter(Subscription.stripe_customer_id == customer_id).first()

        if sub:
            sub.stripe_customer_id = customer_id
            sub.stripe_subscription_id = subscription_id
            sub.status = SubscriptionStatus.active
            sub.plan_id = settings.stripe_price_id
            db.commit()

            if subscription_id:
                stripe_sub = stripe.Subscription.retrieve(subscription_id)
                _sync_stripe_subscription(db, stripe_sub)

    elif event["type"] in {"customer.subscription.created", "customer.subscription.updated"}:
        _sync_stripe_subscription(db, event["data"]["object"])

    elif event["type"] == "customer.subscription.deleted":
        stripe_sub = event["data"]["object"]
        sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub["id"]).first()
        if sub:
            sub.status = SubscriptionStatus.canceled
            db.commit()

    return {"received": True}
