from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# ── Auth ──────────────────────────────────────────────────────────

class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    code: str

class ProfileSetup(BaseModel):
    name: str
    district: str
    lang: str = "en"

class TokenResponse(BaseModel):
    token: str
    user: "UserOut"
    is_new_user: bool


# ── Subscription ──────────────────────────────────────────────────

class SubscriptionOut(BaseModel):
    plan: str
    end_date: Optional[date]
    is_active: bool
    scans_today: int
    scans_limit: int


# ── User ──────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: str
    phone: str
    name: str
    district: str
    language_pref: str
    referral_code: Optional[str]
    subscription: SubscriptionOut

    class Config:
        from_attributes = True


# ── Medicine ──────────────────────────────────────────────────────

class MedicineOut(BaseModel):
    name: str
    dosage_en: str
    dosage_kiny: str
    how_to_use_en: str
    how_to_use_kiny: str
    price_est: str


# ── Disease ───────────────────────────────────────────────────────

class DiseaseOut(BaseModel):
    id: str
    crop_id: str
    name_en: str
    name_kiny: str
    cause_en: str
    cause_kiny: str
    signs_en: str
    signs_kiny: str
    prevention_en: str
    prevention_kiny: str
    medicines: List[MedicineOut]


# ── Scan ──────────────────────────────────────────────────────────

class ScanOut(BaseModel):
    id: str
    photo_url: str
    crop_id: str
    crop_name_en: str
    crop_name_kiny: str
    confidence: float
    is_healthy: bool
    disease: Optional[DiseaseOut]
    scanned_at: str


# ── Crop ──────────────────────────────────────────────────────────

class CropOut(BaseModel):
    id: str
    name_en: str
    name_kiny: str
    emoji: str
    is_active: bool


# ── Subscription payment ──────────────────────────────────────────

class PaymentRequest(BaseModel):
    plan: str  # basic, family, business
    phone: str
    provider: str  # mtn, airtel


# ── Admin ─────────────────────────────────────────────────────────

class AdminStats(BaseModel):
    total_users: int
    total_scans: int
    active_subscriptions: int
    scans_today: int
    top_diseases: List[dict]
