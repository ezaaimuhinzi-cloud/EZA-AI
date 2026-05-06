import os
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import User, Scan, Subscription
from core.deps import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_KEY = os.getenv("ADMIN_KEY", "eza-admin-secret")


def _require_admin(key: str):
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/stats")
async def admin_stats(key: str, db: AsyncSession = Depends(get_db)):
    _require_admin(key)
    today = date.today()

    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    total_scans = (await db.execute(select(func.count(Scan.id)))).scalar()
    active_subs = (await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.status == "active", Subscription.end_date >= today
        )
    )).scalar()
    scans_today = (await db.execute(
        select(func.count(Scan.id)).where(
            Scan.created_at >= datetime.combine(today, datetime.min.time())
        )
    )).scalar()

    # Top diseases
    top_result = await db.execute(
        select(Scan.disease_name_en, func.count(Scan.id).label("count"))
        .where(Scan.disease_name_en != None, Scan.is_healthy == False)
        .group_by(Scan.disease_name_en)
        .order_by(func.count(Scan.id).desc())
        .limit(5)
    )
    top_diseases = [{"disease": r[0], "count": r[1]} for r in top_result.all()]

    return {
        "total_users": total_users,
        "total_scans": total_scans,
        "active_subscriptions": active_subs,
        "scans_today": scans_today,
        "top_diseases": top_diseases,
    }


@router.get("/users")
async def list_users(key: str, limit: int = 50, db: AsyncSession = Depends(get_db)):
    _require_admin(key)
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(limit)
    )
    users = result.scalars().all()
    return [{"id": str(u.id), "phone": u.phone, "name": u.name,
             "district": u.district, "created_at": u.created_at.isoformat()} for u in users]


@router.get("/scans")
async def list_recent_scans(key: str, limit: int = 50, db: AsyncSession = Depends(get_db)):
    _require_admin(key)
    result = await db.execute(
        select(Scan).order_by(Scan.created_at.desc()).limit(limit)
    )
    scans = result.scalars().all()
    return [{
        "id": str(s.id), "crop": s.crop_name_en, "disease": s.disease_name_en,
        "is_healthy": s.is_healthy, "confidence": s.confidence,
        "created_at": s.created_at.isoformat(),
    } for s in scans]
