from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import stripe

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Subscription, SubscriptionStatus, User
from app.schemas import BillingConfigOut, SubscriptionOut

router = APIRouter(prefix="/billing", tags=["billing"])


def _ensure_stripe() -> None:
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe is not configured")
    stripe.api_key = settings.stripe_secret_key


def _map_stripe_status(raw: str) -> SubscriptionStatus:
    try:
        return SubscriptionStatus(raw)
    except ValueError:
        return SubscriptionStatus.incomplete


def _as_dict(obj) -> dict:
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return dict(obj)


def _sync_stripe_subscription(db: Session, stripe_sub) -> Subscription | None:
    data = _as_dict(stripe_sub)
    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == data["id"]).first()
    if not sub and data.get("customer"):
        sub = db.query(Subscription).filter(Subscription.stripe_customer_id == data["customer"]).first()
    if not sub:
        return None

    sub.stripe_subscription_id = data["id"]
    sub.stripe_customer_id = data.get("customer") or sub.stripe_customer_id
    sub.status = _map_stripe_status(data.get("status", "incomplete"))

    items = (data.get("items") or {}).get("data") or []
    if items:
        price = (items[0].get("price") or {})
        sub.plan_id = price.get("id") if isinstance(price, dict) else getattr(price, "id", sub.plan_id)

    period_end = data.get("current_period_end")
    if period_end:
        sub.current_period_end = datetime.fromtimestamp(int(period_end), tz=timezone.utc)

    db.commit()
    db.refresh(sub)
    return sub


def _get_or_create_subscription_row(db: Session, user: User) -> Subscription:
    subscription = user.subscription
    if not subscription:
        subscription = Subscription(user_id=user.id)
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    return subscription


@router.get("/config", response_model=BillingConfigOut)
def billing_config():
    """Public-ish status for the dashboard (auth not required so login pages can hint)."""
    return BillingConfigOut(
        stripe_configured=bool(settings.stripe_secret_key),
        price_configured=bool(settings.stripe_price_id),
        webhook_configured=bool(settings.stripe_webhook_secret),
        bypass_subscription_check=settings.bypass_subscription_check,
    )


@router.get("/subscription", response_model=SubscriptionOut)
def get_subscription(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subscription = _get_or_create_subscription_row(db, user)
    return subscription


@router.post("/checkout-session")
def create_checkout_session(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _ensure_stripe()
    if not settings.stripe_price_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe price is not configured (set STRIPE_PRICE_ID)",
        )

    subscription = _get_or_create_subscription_row(db, user)

    if subscription.status in {SubscriptionStatus.active, SubscriptionStatus.trialing}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have an active subscription")

    if not subscription.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, metadata={"user_id": str(user.id)})
        subscription.stripe_customer_id = customer.id
        db.commit()

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=subscription.stripe_customer_id,
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        success_url=f"{settings.frontend_url.rstrip('/')}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.frontend_url.rstrip('/')}/billing/cancel",
        client_reference_id=str(user.id),
        metadata={"user_id": str(user.id)},
        allow_promotion_codes=True,
    )
    return {"checkout_url": session.url}


@router.post("/portal-session")
def create_portal_session(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Stripe Customer Portal — manage payment method, cancel, invoices."""
    _ensure_stripe()
    subscription = _get_or_create_subscription_row(db, user)
    if not subscription.stripe_customer_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Stripe customer on file. Subscribe first.")

    portal = stripe.billing_portal.Session.create(
        customer=subscription.stripe_customer_id,
        return_url=f"{settings.frontend_url.rstrip('/')}/billing",
    )
    return {"portal_url": portal.url}


@router.post("/sync", response_model=SubscriptionOut)
def sync_subscription(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Pull latest status from Stripe (useful right after Checkout success)."""
    _ensure_stripe()
    subscription = _get_or_create_subscription_row(db, user)

    if subscription.stripe_subscription_id:
        stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
        synced = _sync_stripe_subscription(db, stripe_sub)
        return synced or subscription

    if subscription.stripe_customer_id:
        subs = stripe.Subscription.list(customer=subscription.stripe_customer_id, status="all", limit=5)
        for stripe_sub in subs.data:
            synced = _sync_stripe_subscription(db, stripe_sub)
            if synced:
                return synced

    return subscription


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    _ensure_stripe()
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe webhook not configured")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook") from exc

    event_type = event["type"]
    obj = event["data"]["object"]

    if event_type == "checkout.session.completed":
        user_id = (obj.get("metadata") or {}).get("user_id") or obj.get("client_reference_id")
        customer_id = obj.get("customer")
        subscription_id = obj.get("subscription")

        sub = None
        if user_id:
            try:
                sub = db.query(Subscription).filter(Subscription.user_id == UUID(str(user_id))).first()
            except ValueError:
                sub = None
        if not sub and customer_id:
            sub = db.query(Subscription).filter(Subscription.stripe_customer_id == customer_id).first()

        if sub:
            sub.stripe_customer_id = customer_id or sub.stripe_customer_id
            sub.stripe_subscription_id = subscription_id or sub.stripe_subscription_id
            if obj.get("payment_status") == "paid" or obj.get("status") == "complete":
                sub.status = SubscriptionStatus.active
            sub.plan_id = settings.stripe_price_id or sub.plan_id
            db.commit()

            if subscription_id:
                stripe_sub = stripe.Subscription.retrieve(subscription_id)
                _sync_stripe_subscription(db, stripe_sub)

    elif event_type in {
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    }:
        if event_type == "customer.subscription.deleted":
            data = _as_dict(obj)
            sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == data["id"]).first()
            if sub:
                sub.status = SubscriptionStatus.canceled
                db.commit()
        else:
            _sync_stripe_subscription(db, obj)

    elif event_type in {"invoice.payment_failed", "invoice.paid"}:
        data = _as_dict(obj)
        subscription_id = data.get("subscription")
        if subscription_id:
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            _sync_stripe_subscription(db, stripe_sub)

    return {"received": True}
