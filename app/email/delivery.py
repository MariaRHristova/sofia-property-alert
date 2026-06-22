from __future__ import annotations

import smtplib
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from html import escape
from pathlib import Path

from app.config import Settings
from app.services.subscriptions import SubscriptionView


@dataclass(slots=True)
class EmailDigest:
    subject: str
    html: str
    text: str


@dataclass(slots=True)
class EmailDeliveryResult:
    backend: str
    output_path: str | None = None
    sent: bool = False
    error: str | None = None


def build_digest(
    subscription: SubscriptionView,
    matches: list[dict[str, object]],
) -> EmailDigest:
    subject = _build_subject(subscription, len(matches))
    text = _build_text(subscription, matches)
    html = _build_html(subscription, matches)
    return EmailDigest(subject=subject, html=html, text=text)


def _build_subject(subscription: SubscriptionView, match_count: int) -> str:
    if match_count == 0:
        return f"Bulgaria Property Alert - No available listings in {subscription.city}"
    return f"Bulgaria Property Alert - {subscription.city} digest ({match_count})"


def _build_text(
    subscription: SubscriptionView,
    matches: list[dict[str, object]],
) -> str:
    if not matches:
        return "\n".join(
            [
                "Bulgaria Property Alert",
                "",
                f"Hello {subscription.email},",
                "",
                "There are no available listings for your saved criteria today.",
                "We will keep checking and send the next digest when matches appear.",
                "",
                (
                    f"Criteria: {subscription.city}, "
                    f"{subscription.transaction_type}, {subscription.property_type}"
                ),
            ]
        )

    text_lines = [
        "Bulgaria Property Alert",
        "",
        f"Hello {subscription.email},",
        "",
        f"We found {len(matches)} matching listings for your alert.",
    ]
    for match in matches:
        title = str(match["title"])
        city = str(match["city"])
        district = match.get("district")
        text_lines.append(f"- {title} ({city}{', ' + district if district else ''})")
    return "\n".join(text_lines)


def _build_html(
    subscription: SubscriptionView,
    matches: list[dict[str, object]],
) -> str:
    subscription_badges = _build_subscription_badges(subscription)
    listing_cards = _build_listing_cards(matches)
    match_count = len(matches)
    hero_copy = (
        "There are no available listings for your saved criteria today."
        if match_count == 0
        else f"We found {match_count} matching listings for your alert."
    )
    status_tone = "quiet" if match_count == 0 else "success"
    status_label = "No matches yet" if match_count == 0 else f"{match_count} matches found"

    return f"""<html>
  <body style=\"margin:0;background:#eef2f7;padding:24px 0;font-family:Inter,Segoe UI,Arial,sans-serif;color:#0f172a;\">
    <div style=\"max-width:760px;margin:0 auto;padding:0 16px;\">
      <div style=\"background:linear-gradient(135deg,#0f172a 0%,#1d4ed8 100%);border-radius:24px;padding:28px;color:#ffffff;box-shadow:0 18px 48px rgba(15,23,42,0.2);\">
        <div style=\"font-size:12px;letter-spacing:.14em;text-transform:uppercase;opacity:.8;margin-bottom:12px;\">Bulgaria Property Alert</div>
        <h1 style=\"margin:0 0 10px;font-size:28px;line-height:1.15;\">Your daily property digest</h1>
        <p style=\"margin:0;max-width:58ch;font-size:15px;line-height:1.7;opacity:.92;\">Hello {escape(subscription.email)}, {escape(hero_copy)}</p>
      </div>

      <div style=\"margin-top:18px;background:#ffffff;border:1px solid #dbe3ef;border-radius:24px;padding:22px;box-shadow:0 12px 32px rgba(15,23,42,0.08);\">
        <div style=\"display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px;align-items:flex-start;\">
          <div>
            <div style=\"font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#64748b;margin-bottom:6px;\">Subscription</div>
            <div style=\"font-size:20px;font-weight:700;color:#0f172a;\">{escape(subscription.city)} · {escape(subscription.property_type.title())}</div>
            <div style=\"margin-top:6px;color:#475569;line-height:1.6;\">{escape(subscription.transaction_type.title())} alert for {escape(subscription.email)}</div>
          </div>
          <div style=\"display:inline-flex;align-items:center;border-radius:999px;padding:9px 14px;font-size:13px;font-weight:700;background:{'#ecfeff' if status_tone == 'quiet' else '#dcfce7'};color:{'#155e75' if status_tone == 'quiet' else '#166534'};\">{escape(status_label)}</div>
        </div>

        <div style=\"margin-top:18px;display:flex;flex-wrap:wrap;gap:10px;\">{subscription_badges}</div>
      </div>

      <div style=\"margin-top:18px;\">
        <div style=\"font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#64748b;margin:0 0 10px 4px;\">Matched listings</div>
        {listing_cards}
      </div>
    </div>
  </body>
</html>"""


def _build_subscription_badges(subscription: SubscriptionView) -> str:
    badges = [
        _badge(subscription.transaction_type.title(), "primary"),
        _badge(subscription.city, "neutral"),
        _badge(subscription.property_type.title(), "neutral"),
    ]
    if subscription.districts:
        badges.append(_badge(", ".join(subscription.districts), "accent"))
    if subscription.rooms:
        badges.append(_badge(f"{subscription.rooms} rooms", "accent"))
    if subscription.min_price_eur is not None or subscription.max_price_eur is not None:
        min_price = _format_currency(subscription.min_price_eur)
        max_price = _format_currency(subscription.max_price_eur)
        if min_price and max_price:
            badges.append(_badge(f"€{min_price} - €{max_price}", "accent"))
        elif min_price:
            badges.append(_badge(f"From €{min_price}", "accent"))
        elif max_price:
            badges.append(_badge(f"Up to €{max_price}", "accent"))
    if subscription.min_area_sqm is not None:
        badges.append(_badge(f"Min {subscription.min_area_sqm:.0f} sq.m", "accent"))
    return "".join(badges)


def _build_listing_cards(matches: list[dict[str, object]]) -> str:
    if not matches:
        return (
            '<div style="background:#ffffff;border:1px dashed #cbd5e1;border-radius:20px;padding:18px;color:#64748b;line-height:1.7;">'
            'No listings matched this subscription today. We will keep monitoring and send the next digest when a fit appears.'
            '</div>'
        )

    cards = []
    for index, match in enumerate(matches, start=1):
        title = escape(str(match["title"]))
        url = escape(str(match["url"]))
        city = escape(str(match["city"]))
        district = match.get("district")
        district_text = f", {escape(str(district))}" if district else ""
        price = _format_currency(match.get("price_eur"))
        area = _format_number(match.get("area_sqm"))
        cards.append(
            f'''<div style="background:#ffffff;border:1px solid #dbe3ef;border-radius:22px;padding:18px 18px 16px;margin-bottom:12px;box-shadow:0 8px 24px rgba(15,23,42,0.06);">
  <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">
    <div style="min-width:0;">
      <div style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#64748b;margin-bottom:6px;">Listing {index}</div>
      <div style="font-size:18px;font-weight:700;line-height:1.35;color:#0f172a;margin-bottom:8px;"><a href="{url}" style="color:#0f172a;text-decoration:none;">{title}</a></div>
      <div style="color:#475569;line-height:1.7;">{city}{district_text}</div>
    </div>
    <div style="text-align:right;white-space:nowrap;">
      <div style="display:inline-block;background:#eff6ff;color:#1d4ed8;border-radius:999px;padding:7px 12px;font-size:13px;font-weight:700;margin-bottom:8px;">€{price}</div>
      <div style="display:block;color:#64748b;font-size:13px;">{area} sq.m</div>
    </div>
  </div>
</div>'''
        )
    return "".join(cards)


def _badge(label: str, tone: str) -> str:
    styles = {
        "primary": "background:#0f172a;color:#ffffff;border:1px solid #0f172a;",
        "neutral": "background:#f1f5f9;color:#0f172a;border:1px solid #dbe3ef;",
        "accent": "background:#dbeafe;color:#1d4ed8;border:1px solid #bfdbfe;",
    }
    return (
        f'<span style="display:inline-flex;align-items:center;border-radius:999px;'
        f'padding:8px 12px;font-size:13px;font-weight:600;line-height:1;{styles[tone]}">'
        f'{escape(label)}</span>'
    )


def _format_currency(value: object | None) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:,.0f}".replace(",", " ")
    return escape(str(value))


def _format_number(value: object | None) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.0f}"
    return escape(str(value))


class EmailService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def deliver(
        self,
        subscription: SubscriptionView,
        matches: list[dict[str, object]],
    ) -> EmailDeliveryResult:
        digest = build_digest(subscription, matches)
        preview_path = self._write_preview(subscription, digest)
        if self.settings.email_backend == "smtp":
            error = self._send_smtp(subscription, digest)
            return EmailDeliveryResult(
                backend="smtp",
                output_path=preview_path,
                sent=error is None,
                error=error,
            )
        return EmailDeliveryResult(
            backend="preview",
            output_path=preview_path,
            sent=False,
        )

    def _write_preview(
        self,
        subscription: SubscriptionView,
        digest: EmailDigest,
    ) -> str:
        preview_dir = Path(self.settings.email_preview_dir)
        preview_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}-{subscription.id}.eml"
        path = preview_dir / filename
        message = EmailMessage()
        message["To"] = subscription.email
        message["From"] = self.settings.email_from
        message["Subject"] = digest.subject
        message.set_content(digest.text)
        message.add_alternative(digest.html, subtype="html")
        path.write_text(message.as_string(), encoding="utf-8")
        return str(path)

    def _send_smtp(
        self, subscription: SubscriptionView, digest: EmailDigest
    ) -> str | None:
        message = EmailMessage()
        message["To"] = subscription.email
        message["From"] = self.settings.email_from
        message["Subject"] = digest.subject
        message.set_content(digest.text)
        message.add_alternative(digest.html, subtype="html")

        try:
            if self.settings.smtp_use_starttls:
                with smtplib.SMTP(
                    self.settings.smtp_host,
                    self.settings.smtp_port,
                ) as client:
                    client.ehlo()
                    client.starttls()
                    client.ehlo()
                    if self.settings.smtp_username:
                        client.login(
                            self.settings.smtp_username,
                            self.settings.smtp_password,
                        )
                    client.send_message(message)
                return None

            with smtplib.SMTP_SSL(
                self.settings.smtp_host,
                self.settings.smtp_port,
            ) as client:
                if self.settings.smtp_username:
                    client.login(
                        self.settings.smtp_username,
                        self.settings.smtp_password,
                    )
                client.send_message(message)
            return None
        except smtplib.SMTPAuthenticationError:
            return (
                "SMTP authentication failed. Gmail requires a 16-character "
                "Google App Password when two-step verification is enabled."
            )
        except smtplib.SMTPException as exc:
            return f"SMTP delivery failed: {exc}"
        except OSError as exc:
            return f"Could not connect to the SMTP server: {exc}"
