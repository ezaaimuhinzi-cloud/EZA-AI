from datetime import datetime, date
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import User, Scan, Subscription
from schemas import ScanOut, DiseaseOut, MedicineOut
from core.deps import get_current_user
from services.ai_service import predict_disease
from services.disease_service import get_crop_info, build_disease_info
import uuid

router = APIRouter(prefix="/scan", tags=["scan"])

FREE_SCANS_LIMIT = 5


async def _check_scan_limit(user: User, db: AsyncSession):
    today = date.today()
    # Check for active paid subscription
    sub_result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.status == "active",
            Subscription.end_date >= today,
        )
    )
    if sub_result.scalar_one_or_none():
        return  # paid user — unlimited

    # Count today's scans
    count_result = await db.execute(
        select(func.count(Scan.id)).where(
            Scan.user_id == user.id,
            Scan.created_at >= datetime.combine(today, datetime.min.time()),
        )
    )
    scans_today = count_result.scalar() or 0
    if scans_today >= FREE_SCANS_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Free plan limit reached ({FREE_SCANS_LIMIT} scans/day). Upgrade to continue.",
        )


def _build_scan_out(scan: Scan) -> ScanOut:
    disease = None
    if scan.disease_id and not scan.is_healthy:
        medicines = []
        if scan.medicine_name:
            medicines.append(MedicineOut(
                name=scan.medicine_name,
                dosage_en="See label",
                dosage_kiny="Reba etiketi",
                how_to_use_en="Follow label instructions.",
                how_to_use_kiny="Kurikiza amabwiriza y'etiketi.",
                price_est=scan.medicine_price_est or "N/A",
            ))
        disease = DiseaseOut(
            id=scan.disease_id,
            crop_id=scan.crop_id,
            name_en=scan.disease_name_en or "",
            name_kiny=scan.disease_name_kiny or "",
            cause_en=scan.cause_en or "",
            cause_kiny=scan.cause_kiny or "",
            signs_en=scan.signs_en or "",
            signs_kiny=scan.signs_kiny or "",
            prevention_en=scan.prevention_en or "",
            prevention_kiny=scan.prevention_kiny or "",
            medicines=medicines,
        )
    return ScanOut(
        id=str(scan.id),
        photo_url=scan.photo_url or "",
        crop_id=scan.crop_id,
        crop_name_en=scan.crop_name_en,
        crop_name_kiny=scan.crop_name_kiny,
        confidence=scan.confidence,
        is_healthy=scan.is_healthy,
        disease=disease,
        scanned_at=scan.created_at.isoformat(),
    )


@router.post("/upload", response_model=ScanOut)
async def upload_scan(
    file: UploadFile = File(...),
    crop_filter: Optional[str] = Form(None),
    lang: str = Form("en"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    await _check_scan_limit(current_user, db)

    image_bytes = await file.read()

    # Call AI model (HF Space)
    try:
        ai_result = await predict_disease(image_bytes, crop_filter=crop_filter)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(e)}")

    # Resolve crop identity (user selection takes priority)
    effective_crop = crop_filter if crop_filter else ai_result.get("cropRaw", "")
    crop_id, crop_en, crop_kiny = get_crop_info(effective_crop)
    disease_raw: str = ai_result.get("diseaseRaw", "")
    is_healthy: bool = ai_result.get("isHealthy", True)
    confidence: float = float(ai_result.get("confidence", 0.0))

    # Build full disease info
    disease_info = None
    if not is_healthy and disease_raw:
        disease_info = build_disease_info(crop_id, crop_en, crop_kiny, disease_raw)

    # Save scan to DB
    medicines = disease_info.get("medicines", []) if disease_info else []
    first_med = medicines[0] if medicines else {}

    scan = Scan(
        user_id=current_user.id,
        photo_url="",  # Cloudinary integration optional
        crop_id=crop_id,
        crop_name_en=crop_en,
        crop_name_kiny=crop_kiny,
        disease_id=disease_raw if not is_healthy else None,
        disease_name_en=disease_info["name_en"] if disease_info else None,
        disease_name_kiny=disease_info["name_kiny"] if disease_info else None,
        confidence=confidence,
        is_healthy=is_healthy,
        cause_en=disease_info["cause_en"] if disease_info else None,
        cause_kiny=disease_info["cause_kiny"] if disease_info else None,
        signs_en=disease_info["signs_en"] if disease_info else None,
        signs_kiny=disease_info["signs_kiny"] if disease_info else None,
        prevention_en=disease_info["prevention_en"] if disease_info else None,
        prevention_kiny=disease_info["prevention_kiny"] if disease_info else None,
        medicine_name=first_med.get("name") if first_med else None,
        medicine_price_est=first_med.get("price_est") if first_med else None,
    )
    db.add(scan)
    await db.flush()

    # Build response
    disease_out = None
    if disease_info:
        disease_out = DiseaseOut(
            id=disease_info["id"],
            crop_id=disease_info["crop_id"],
            name_en=disease_info["name_en"],
            name_kiny=disease_info["name_kiny"],
            cause_en=disease_info["cause_en"],
            cause_kiny=disease_info["cause_kiny"],
            signs_en=disease_info["signs_en"],
            signs_kiny=disease_info["signs_kiny"],
            prevention_en=disease_info["prevention_en"],
            prevention_kiny=disease_info["prevention_kiny"],
            medicines=[MedicineOut(**m) for m in disease_info["medicines"]],
        )

    return ScanOut(
        id=str(scan.id),
        photo_url="",
        crop_id=crop_id,
        crop_name_en=crop_en,
        crop_name_kiny=crop_kiny,
        confidence=confidence,
        is_healthy=is_healthy,
        disease=disease_out,
        scanned_at=scan.created_at.isoformat(),
    )


@router.get("/history", response_model=list[ScanOut])
async def scan_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    scans = result.scalars().all()
    return [_build_scan_out(s) for s in scans]


@router.delete("/{scan_id}")
async def delete_scan(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    await db.delete(scan)
    return {"message": "Deleted"}
