from __future__ import annotations

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from app.catalog import (
    CITY_OPTIONS,
    PROPERTY_TYPES,
    ROOM_OPTIONS,
    TRANSACTION_TYPES,
    canonicalize_district,
)
from app.services.auth import normalize_email, validate_password


class SubscriptionCreate(BaseModel):
    email: str | None = None
    transaction_type: str
    property_type: str
    city: str
    districts: list[str] = Field(default_factory=list)
    min_price_eur: float | None = Field(default=None, ge=0)
    max_price_eur: float | None = Field(default=None, ge=0)
    rooms: str | None = None
    min_area_sqm: float | None = Field(default=None, ge=0)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        return normalize_email(value)

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, value: str) -> str:
        if value not in TRANSACTION_TYPES:
            raise ValueError("Unsupported transaction type.")
        return value

    @field_validator("property_type")
    @classmethod
    def validate_property_type(cls, value: str) -> str:
        if value not in PROPERTY_TYPES:
            raise ValueError("Unsupported property type.")
        return value

    @field_validator("city")
    @classmethod
    def validate_city(cls, value: str) -> str:
        if value not in CITY_OPTIONS:
            raise ValueError("Unsupported city.")
        return value

    @field_validator("districts")
    @classmethod
    def validate_districts(
        cls,
        values: list[str],
        info: ValidationInfo,
    ) -> list[str]:
        city = info.data.get("city")
        cleaned = [
            canonicalize_district(value, city=city) for value in values if value.strip()
        ]
        unique_values = list(dict.fromkeys(cleaned))
        if city is None:
            return unique_values
        allowed = set(CITY_OPTIONS[city]["districts"])
        invalid = [value for value in unique_values if value not in allowed]
        if invalid:
            raise ValueError(
                "One or more districts do not belong to the selected city."
            )
        return unique_values

    @field_validator("rooms")
    @classmethod
    def validate_rooms(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if value not in ROOM_OPTIONS:
            raise ValueError("Unsupported room option.")
        return value

    @field_validator("max_price_eur")
    @classmethod
    def validate_price_range(
        cls,
        value: float | None,
        info: ValidationInfo,
    ) -> float | None:
        min_price = info.data.get("min_price_eur")
        if value is not None and min_price is not None and value < min_price:
            raise ValueError("Maximum price must be greater than minimum price.")
        return value


class RegisterForm(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password(value)


class LoginForm(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class PasswordResetRequestForm(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class PasswordResetForm(BaseModel):
    token: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_value(cls, value: str) -> str:
        return validate_password(value)


class SchedulerConfigUpdate(BaseModel):
    enabled: bool
    mode: str
    interval_minutes: int = Field(default=60, ge=1, le=1440)
    daily_run_time: str = "08:00"

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        if value not in {"interval", "daily_time"}:
            raise ValueError("Unsupported scheduler mode.")
        return value

    @field_validator("daily_run_time")
    @classmethod
    def validate_daily_run_time(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) != 5 or cleaned[2] != ":":
            raise ValueError("Daily run time must be in HH:MM format.")
        hours, minutes = cleaned.split(":", maxsplit=1)
        if not (hours.isdigit() and minutes.isdigit()):
            raise ValueError("Daily run time must be in HH:MM format.")
        if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
            raise ValueError("Daily run time must be in HH:MM format.")
        return cleaned


class SchedulerConfigView(BaseModel):
    enabled: bool
    mode: str
    interval_minutes: int
    daily_run_time: str
    next_run_at: str | None = None
    running: bool = False
