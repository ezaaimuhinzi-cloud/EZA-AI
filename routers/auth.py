import os
import random
import string
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import User, OTP, Subscription
from schemas import OTPRequest, OTPVerify, ProfileSetup, TokenResponse, UserOut, SubscriptionOut
from core.security import create_access_token
from core.deps import get_current_user
from services.sms_service import generate_otp, send_otp
import uuid
from datetime import date

router = APIRouter(prefix="/auth", tags=["auth"])

DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
FREE_SCANS_LIMIT = 5


def _gen_referral_code(user_id: str) -> str:
    return str(user_id).replace("-", "")[:8].upper()


async def _get_subscription_out(user: User, db: AsyncSession) -> SubscriptionOut:
    today = date.today()
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user.id, Subscription.status == "active",
               Subscription.end_date >= today)
        .order_by(Subscription.end_date.desc())
    )
    sub = result.scalar_one_or_none()

    if sub:
        plan = sub.plan
        end_date = sub.end_date
        is_active = True
        scans_limit = 9999
    else:
        plan = "free"
        end_date = None
        is_active = True
        scans_limit = FREE_SCANS_LIMIT

    # Count today's scans
    from models import Scan
    count_result = await db.execute(
        select(func.count(Scan.id)).where(
            Scan.user_id == user.id,
            Scan.created_at >= datetime.combine(today, datetime.min.time())
        )
    )
    scans_today = count_result.scalar() or 0

    return SubscriptionOut(
        plan=plan,
        end_date=end_date,
        is_active=is_active,
        scans_today=scans_today,
        scans_limit=scans_limit,
    )


async def _user_out(user: User, db: AsyncSession) -> UserOut:
    sub = await _get_subscription_out(user, db)
    return UserOut(
        id=str(user.id),
        phone=user.phone,
        name=user.name or "",
        district=user.district or "",
        language_pref=user.language_pref or "en",
        referral_code=user.referral_code,
        subscription=sub,
    )


@router.post("/request-otp")
async def request_otp(body: OTPRequest, db: AsyncSession = Depends(get_db)):
    phone = body.phone.strip()

    # Invalidate old OTPs for this phone
    old_result = await db.execute(select(OTP).where(OTP.phone == phone, OTP.used == False))
    for old_otp in old_result.scalars().all():
        old_otp.used = True

    code = generate_otp()
    otp = OTP(
        phone=phone,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(otp)
    await db.flush()

    sent = await send_otp(phone, code)

    resp = {"message": "OTP sent via SMS"}
    if DEV_MODE:
        resp["dev_otp"] = code  # only visible in dev
    return resp


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(body: OTPVerify, db: AsyncSession = Depends(get_db)):
    phone = body.phone.strip()
    code = body.code.strip()

    result = await db.execute(
        select(OTP)
        .where(OTP.phone == phone, OTP.code == code, OTP.used == False,
               OTP.expires_at > datetime.utcnow())
        .order_by(OTP.created_at.desc())
    )
    otp = result.scalar_one_or_none()

    if not otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    otp.used = True

    # Get or create user
    user_result = await db.execute(select(User).where(User.phone == phone))
    user = user_result.scalar_one_or_none()
    is_new = user is None

    if is_new:
        user = User(phone=phone, language_pref="en")
        db.add(user)
        await db.flush()
        user.referral_code = _gen_referral_code(str(user.id))

    token = create_access_token(str(user.id))
    user_out = await _user_out(user, db)
    return TokenResponse(token=token, user=user_out, is_new_user=is_new)


@router.post("/setup", response_model=UserOut)
async def setup_profile(
    body: ProfileSetup,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.name = body.name.strip()
    current_user.district = body.district.strip()
    current_user.language_pref = body.lang
    return await _user_out(current_user, db)


@router.get("/me", response_model=UserOut)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _user_out(current_user, db)
