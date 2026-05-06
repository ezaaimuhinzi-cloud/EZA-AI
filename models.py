import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Float, DateTime, Integer, Text, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), default="")
    district = Column(String(100), default="")
    language_pref = Column(String(10), default="en")
    referral_code = Column(String(10), unique=True)
    referred_by = Column(String(10))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    scans = relationship("Scan", back_populates="user", lazy="select")
    subscriptions = relationship("Subscription", back_populates="user", lazy="select")


class OTP(Base):
    __tablename__ = "otps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    plan = Column(String(20), nullable=False, default="free")  # free, basic, family, business
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default="active")  # active, expired, cancelled
    amount = Column(Integer, default=0)  # RWF
    tx_id = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="subscriptions")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    photo_url = Column(Text, default="")
    crop_id = Column(String(50), default="")
    crop_name_en = Column(String(100), default="")
    crop_name_kiny = Column(String(100), default="")
    disease_id = Column(String(100))
    disease_name_en = Column(String(200))
    disease_name_kiny = Column(String(200))
    confidence = Column(Float, default=0.0)
    is_healthy = Column(Boolean, default=False)
    cause_en = Column(Text)
    cause_kiny = Column(Text)
    signs_en = Column(Text)
    signs_kiny = Column(Text)
    prevention_en = Column(Text)
    prevention_kiny = Column(Text)
    medicine_name = Column(String(200))
    medicine_price_est = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scans")
