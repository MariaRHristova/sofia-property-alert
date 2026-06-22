from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    transaction_type: Mapped[str] = mapped_column(String(20))
    property_type: Mapped[str] = mapped_column(String(20))
    city: Mapped[str] = mapped_column(String(80), index=True)
    districts: Mapped[str] = mapped_column(Text, default="")
    min_price_eur: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_price_eur: Mapped[float | None] = mapped_column(Float, nullable=True)
    rooms: Mapped[str | None] = mapped_column(String(20), nullable=True)
    min_area_sqm: Mapped[float | None] = mapped_column(Float, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    initialized: Mapped[bool] = mapped_column(Boolean, default=False)
    unsubscribe_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (UniqueConstraint("source", "external_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(40), index=True)
    external_id: Mapped[str] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(String(1000))
    title: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(80))
    district: Mapped[str | None] = mapped_column(String(120), nullable=True)
    transaction_type: Mapped[str] = mapped_column(String(20))
    property_type: Mapped[str] = mapped_column(String(20))
    price_eur: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_sqm: Mapped[float | None] = mapped_column(Float, nullable=True)
    rooms: Mapped[str | None] = mapped_column(String(20), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    raw_summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class ListingMatch(Base):
    __tablename__ = "listing_matches"
    __table_args__ = (UniqueConstraint("subscription_id", "listing_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subscription_id: Mapped[int] = mapped_column(Integer, index=True)
    listing_id: Mapped[int] = mapped_column(Integer, index=True)
    state: Mapped[str] = mapped_column(String(20), default="pending")
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )


class JobRun(Base):
    __tablename__ = "job_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), default="started")
    listings_seen: Mapped[int] = mapped_column(Integer, default=0)
    listings_created: Mapped[int] = mapped_column(Integer, default=0)
    matches_created: Mapped[int] = mapped_column(Integer, default=0)
    emails_sent: Mapped[int] = mapped_column(Integer, default=0)
    failure_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class SchedulerConfig(Base):
    __tablename__ = "scheduler_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mode: Mapped[str] = mapped_column(String(20), default="interval")
    interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    daily_run_time: Mapped[str] = mapped_column(String(5), default="08:00")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
