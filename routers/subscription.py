import os
import hmac
import hashlib
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import User, Subscription, Scan
from schemas import PaymentRequest, SubscriptionOut
from core.deps import get_current_user
from datetime import datetime

router = APIRouter(prefix="/subscription", tags=["subscription"])

FLW_SECRET = os.getenv("FLW_SECRET_KEY", "")

PLANS = {
    "basic": {"amount": 500, "days": 30, "label": "Basic - Isanzwe"},
    "family": {"amount": 1000, "days": 30, "label": "Family - Umuryango"},
    "business": {"amount": 5000, "days": 30, "label": "Business - Ubucuruzi"},
}

FREE_SCANS_LIMIT = 5


@router.get("/status", response_model=SubscriptionOut)
async def subscription_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active",
            Subscription.end_date >= today,
        ).order_by(Subscription.end_date.desc())
    )
    sub = result.scalar_one_or_none()

    count_result = await db.execute(
        select(func.count(Scan.id)).where(
            Scan.user_id == current_user.id,
            Scan.created_at >= datetime.combine(today, datetime.min.time()),
        )
    )
    scans_today = count_result.scalar() or 0

    if sub:
        return SubscriptionOut(plan=sub.plan, end_date=sub.end_date,
                               is_active=True, scans_today=scans_today, scans_limit=9999)
    return SubscriptionOut(plan="free", end_date=None, is_active=True,
                           scans_today=scans_today, scans_limit=FREE_SCANS_LIMIT)


@router.get("/plans")
async def list_plans():
    return [{"id": k, "label": v["label"], "amount": v["amount"],
             "currency": "RWF", "period": "monthly"} for k, v in PLANS.items()]


@router.post("/pay")
async def initiate_payment(
    body: PaymentRequest,
    current_user: User = Depends(get_current_user),
):
    if body.plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    plan = PLANS[body.plan]
    # In production: call Flutterwave API to initiate mobile money charge
    # For now, return payment link data
    return {
        "plan": body.plan,
        "amount": plan["amount"],
        "currency": "RWF",
        "message": "Use Flutterwave payment link to complete payment.",
        "payment_link": f"https://checkout.flutterwave.com/v3/pay",
        "redirect_url": "https://eza-ai-backend.onrender.com/api/v1/subscription/webhook",
    }


@router.post("/webhook")
async def payment_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Flutterwave sends payment confirmation here."""
    payload = await request.json()

    # Verify Flutterwave signature
    flw_signature = request.headers.get("verif-hash", "")
    if FLW_SECRET and flw_signature != FLW_SECRET:
        raise HTTPException(status_code=401, detail="Invalid signature")

    if payload.get("status") != "successful":
        return {"status": "ignored"}

    tx_id = str(payload.get("id", ""))
    customer = payload.get("customer", {})
    phone = customer.get("phone_number", "").replace("+250", "").lstrip("0")
    meta = payload.get("meta", {})
    plan_key = meta.get("plan", "basic")

    if plan_key not in PLANS:
        return {"status": "unknown_plan"}

    plan_info = PLANS[plan_key]

    # Find user by phone
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        return {"status": "user_not_found"}

    # Cancel existing subscriptions
    existing = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id, Subscription.status == "active")
    )
    for s in existing.scalars().all():
        s.status = "cancelled"

    # Create new subscription
    today = date.today()
    sub = Subscription(
        user_id=user.id,
        plan=plan_key,
        start_date=today,
        end_date=today + timedelta(days=plan_info["days"]),
        status="active",
        amount=plan_info["amount"],
        tx_id=tx_id,
    )
    db.add(sub)
    return {"status": "subscription_activated", "plan": plan_key}
