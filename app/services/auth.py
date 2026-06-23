# ruff: noqa: E501
from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import AccountToken, Subscription, User, UserSession

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 15
PASSWORD_MAX_LENGTH = 128
SESSION_COOKIE_NAME = "property_alert_session"
SESSION_TTL_DAYS = 30
VERIFY_EMAIL_PURPOSE = "verify_email"
RESET_PASSWORD_PURPOSE = "reset_password"


class AuthError(Exception):
    pass


@dataclass(slots=True)
class SessionBundle:
    token: str
    csrf_token: str
    session: UserSession


@dataclass(slots=True)
class AuthenticatedUser:
    id: int
    email: str
    verified_at: datetime | None
    csrf_token: str


@dataclass(slots=True)
class OutboundMessage:
    to_email: str
    subject: str
    text: str
    html: str


@dataclass(slots=True)
class RegisterResult:
    user: User
    verification_message: OutboundMessage


@dataclass(slots=True)
class PasswordResetResult:
    reset_message: OutboundMessage


class PasswordHasher:
    def hash_password(self, password: str) -> str:
        validate_password(password)
        salt = secrets.token_bytes(16)
        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
            dklen=64,
        )
        return ("scrypt$16384$8$1$" + "{salt}$" + "{digest}").format(
            salt=base64.urlsafe_b64encode(salt).decode("ascii"),
            digest=base64.urlsafe_b64encode(digest).decode("ascii"),
        )

    def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            algorithm, n_value, r_value, p_value, salt_value, digest_value = (
                password_hash.split("$", maxsplit=5)
            )
        except ValueError:
            return False
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_value.encode("ascii"))
        expected_digest = base64.urlsafe_b64decode(digest_value.encode("ascii"))
        actual_digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n_value),
            r=int(r_value),
            p=int(p_value),
            dklen=len(expected_digest),
        )
        return hmac.compare_digest(actual_digest, expected_digest)


def normalize_email(value: str) -> str:
    cleaned = value.strip().lower()
    if not EMAIL_RE.match(cleaned):
        raise AuthError("Enter a valid email address.")
    return cleaned


def validate_password(value: str) -> str:
    if len(value) < PASSWORD_MIN_LENGTH:
        raise AuthError(
            f"Use a password with at least {PASSWORD_MIN_LENGTH} characters."
        )
    if len(value) > PASSWORD_MAX_LENGTH:
        raise AuthError(
            f"Use a password with at most {PASSWORD_MAX_LENGTH} characters."
        )
    return value


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class AuthService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.password_hasher = PasswordHasher()

    def register_user(self, email: str, password: str) -> RegisterResult:
        normalized_email = normalize_email(email)
        password_hash = self.password_hasher.hash_password(password)
        existing = self.session.scalar(select(User).where(User.email == normalized_email))
        if existing is not None:
            raise AuthError("An account with this email already exists.")

        user = User(email=normalized_email, password_hash=password_hash)
        self.session.add(user)
        self.session.flush()
        self._claim_existing_subscriptions(user)
        token = self._issue_token(user.id, VERIFY_EMAIL_PURPOSE, hours=24)
        self.session.commit()
        self.session.refresh(user)
        return RegisterResult(
            user=user,
            verification_message=build_verification_message(
                normalized_email,
                self._absolute_url(f"/auth/verify?token={token}"),
            ),
        )

    def authenticate_user(self, email: str, password: str) -> User:
        normalized_email = normalize_email(email)
        user = self.session.scalar(select(User).where(User.email == normalized_email))
        if user is None or not self.password_hasher.verify_password(
            password, user.password_hash
        ):
            raise AuthError("Invalid email or password.")
        if not user.active:
            raise AuthError("This account is inactive.")
        if user.verified_at is None:
            raise AuthError("Verify your email before signing in.")
        return user

    def create_session(self, user: User) -> SessionBundle:
        raw_token = secrets.token_urlsafe(32)
        csrf_token = secrets.token_urlsafe(24)
        user_session = UserSession(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            csrf_token=csrf_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=SESSION_TTL_DAYS),
        )
        self.session.add(user_session)
        self.session.commit()
        self.session.refresh(user_session)
        return SessionBundle(token=raw_token, csrf_token=csrf_token, session=user_session)

    def get_authenticated_user(self, raw_token: str | None) -> AuthenticatedUser | None:
        if not raw_token:
            return None
        statement = select(UserSession, User).join(User, User.id == UserSession.user_id).where(
            UserSession.token_hash == hash_token(raw_token)
        )
        row = self.session.execute(statement).first()
        if row is None:
            return None
        user_session, user = row
        now = datetime.now(timezone.utc)
        if user_session.revoked_at is not None or _as_utc(user_session.expires_at) <= now:
            return None
        user_session.last_seen_at = now
        self.session.commit()
        return AuthenticatedUser(
            id=user.id,
            email=user.email,
            verified_at=user.verified_at,
            csrf_token=user_session.csrf_token,
        )

    def revoke_session(self, raw_token: str | None) -> None:
        if not raw_token:
            return
        user_session = self.session.scalar(
            select(UserSession).where(UserSession.token_hash == hash_token(raw_token))
        )
        if user_session is None:
            return
        user_session.revoked_at = datetime.now(timezone.utc)
        self.session.commit()

    def require_csrf(self, raw_token: str | None, csrf_token: str | None) -> AuthenticatedUser:
        user = self.get_authenticated_user(raw_token)
        if user is None:
            raise AuthError("Sign in to continue.")
        if not csrf_token or not hmac.compare_digest(user.csrf_token, csrf_token):
            raise AuthError("Your session expired. Refresh the page and try again.")
        return user

    def verify_email_token(self, raw_token: str) -> User:
        token = self._consume_token(raw_token, VERIFY_EMAIL_PURPOSE)
        user = self.session.get(User, token.user_id)
        if user is None:
            raise AuthError("Verification link is no longer valid.")
        if user.verified_at is None:
            user.verified_at = datetime.now(timezone.utc)
            self._claim_existing_subscriptions(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def create_password_reset(self, email: str) -> PasswordResetResult | None:
        normalized_email = normalize_email(email)
        user = self.session.scalar(select(User).where(User.email == normalized_email))
        if user is None or user.verified_at is None:
            return None
        token = self._issue_token(user.id, RESET_PASSWORD_PURPOSE, hours=2)
        self.session.commit()
        return PasswordResetResult(
            reset_message=build_reset_message(
                normalized_email,
                self._absolute_url(f"/auth/password/reset?token={token}"),
            )
        )

    def reset_password(self, raw_token: str, password: str) -> User:
        token = self._consume_token(raw_token, RESET_PASSWORD_PURPOSE)
        user = self.session.get(User, token.user_id)
        if user is None:
            raise AuthError("Reset link is no longer valid.")
        user.password_hash = self.password_hasher.hash_password(password)
        self.session.execute(delete(UserSession).where(UserSession.user_id == user.id))
        self.session.commit()
        self.session.refresh(user)
        return user

    def _issue_token(self, user_id: int, purpose: str, *, hours: int) -> str:
        self.session.execute(
            delete(AccountToken).where(
                AccountToken.user_id == user_id,
                AccountToken.purpose == purpose,
                AccountToken.used_at.is_(None),
            )
        )
        raw_token = secrets.token_urlsafe(32)
        token = AccountToken(
            user_id=user_id,
            purpose=purpose,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=hours),
        )
        self.session.add(token)
        return raw_token

    def _consume_token(self, raw_token: str, purpose: str) -> AccountToken:
        token = self.session.scalar(
            select(AccountToken).where(
                AccountToken.token_hash == hash_token(raw_token),
                AccountToken.purpose == purpose,
            )
        )
        now = datetime.now(timezone.utc)
        if token is None or token.used_at is not None or _as_utc(token.expires_at) <= now:
            raise AuthError("This link is no longer valid.")
        token.used_at = now
        return token

    def _claim_existing_subscriptions(self, user: User) -> None:
        subscriptions = list(
            self.session.scalars(
                select(Subscription).where(
                    or_(
                        Subscription.user_id.is_(None),
                        Subscription.user_id == user.id,
                    ),
                    Subscription.email == user.email,
                )
            )
        )
        for subscription in subscriptions:
            subscription.user_id = user.id

    def _absolute_url(self, path: str) -> str:
        return f"{self.settings.app_base_url.rstrip('/')}{path}"


def build_verification_message(email: str, verification_url: str) -> OutboundMessage:
    subject = "Verify your Sofia Property Alert account"
    text = (
        "Sofia Property Alert\n\n"
        f"Hello {email},\n\n"
        "Confirm your account to start receiving your saved property digests.\n"
        f"Verify your email: {verification_url}\n"
    )
    html = (
        "<html><body style='font-family:Arial,sans-serif;padding:24px;color:#181717;'>"
        "<h1 style='font-family:Georgia,serif;font-weight:400;'>Verify your account</h1>"
        "<p>Confirm your email to activate your Sofia Property Alert dashboard.</p>"
        f"<p><a href='{verification_url}' style='display:inline-block;padding:12px 18px;border-radius:999px;background:#181717;color:#ffffff;text-decoration:none;'>Verify email</a></p>"
        f"<p>If the button does not work, use this link:<br>{verification_url}</p>"
        "</body></html>"
    )
    return OutboundMessage(to_email=email, subject=subject, text=text, html=html)


def build_reset_message(email: str, reset_url: str) -> OutboundMessage:
    subject = "Reset your Sofia Property Alert password"
    text = (
        "Sofia Property Alert\n\n"
        f"Hello {email},\n\n"
        "Use the link below to choose a new password.\n"
        f"Reset your password: {reset_url}\n"
    )
    html = (
        "<html><body style='font-family:Arial,sans-serif;padding:24px;color:#181717;'>"
        "<h1 style='font-family:Georgia,serif;font-weight:400;'>Reset your password</h1>"
        "<p>Use the secure link below to choose a new password.</p>"
        f"<p><a href='{reset_url}' style='display:inline-block;padding:12px 18px;border-radius:999px;background:#181717;color:#ffffff;text-decoration:none;'>Reset password</a></p>"
        f"<p>If the button does not work, use this link:<br>{reset_url}</p>"
        "</body></html>"
    )
    return OutboundMessage(to_email=email, subject=subject, text=text, html=html)

