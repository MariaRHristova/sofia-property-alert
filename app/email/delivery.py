# ruff: noqa: E501
from __future__ import annotations

import smtplib
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from html import escape
from pathlib import Path

from app.config import Settings
from app.services.auth import OutboundMessage
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
    unsubscribe_url: str | None = None,
) -> EmailDigest:
    subject = _build_subject(subscription, len(matches))
    text = _build_text(subscription, matches, unsubscribe_url=unsubscribe_url)
    html = _build_html(subscription, matches, unsubscribe_url=unsubscribe_url)
    return EmailDigest(subject=subject, html=html, text=text)


def _build_subject(subscription: SubscriptionView, match_count: int) -> str:
    if match_count == 0:
        return f"Sofia Property Alert - No available listings in {subscription.city}"
    return f"Sofia Property Alert - {subscription.city} digest ({match_count})"


def _build_text(
    subscription: SubscriptionView,
    matches: list[dict[str, object]],
    unsubscribe_url: str | None = None,
) -> str:
    lines: list[str]
    if not matches:
        lines = [
            "Sofia Property Alert",
            "",
            f"Hello {subscription.email},",
            "",
            "There are no available listings for your saved criteria today.",
            "We will keep checking Sofia and send the next digest when matches appear.",
            "",
            (
                f"Criteria: {subscription.city}, "
                f"{subscription.transaction_type}, {subscription.property_type}"
            ),
        ]
    else:
        lines = [
            "Sofia Property Alert",
            "",
            f"Hello {subscription.email},",
            "",
            f"We found {len(matches)} matching listings for your alert.",
        ]
        for match in matches:
            title = str(match["title"])
            city = str(match["city"])
            district = match.get("district")
            district_suffix = f", {district}" if district else ""
            lines.append(f"- {title} ({city}{district_suffix})")

    if unsubscribe_url:
        lines.extend(["", f"Unsubscribe: {unsubscribe_url}"])
    return "\n".join(lines)


def _build_html(
    subscription: SubscriptionView,
    matches: list[dict[str, object]],
    unsubscribe_url: str | None = None,
) -> str:
    match_count = len(matches)
    has_matches = match_count > 0
    hero_copy = (
        "There are no available listings for your saved criteria today."
        if not has_matches
        else f"We found {match_count} matching listings for your alert."
    )
    status_label = "No matches yet" if not has_matches else f"{match_count} matches found"
    status_bg = "#ffffff"
    status_fg = "#181717"
    listing_section = _build_listing_rows(matches)
    unsubscribe_cta = ""
    if unsubscribe_url:
        unsubscribe_cta = (
            "<div style='margin-top:18px;padding-top:18px;border-top:2px solid #181717;'>"
            "<div style='font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#5f5a55;margin-bottom:10px;'>Manage alert</div>"
            f"<a href='{escape(unsubscribe_url)}' style='display:inline-block;background:#181717;color:#f7f7f5;text-decoration:none;border:2px solid #181717;border-radius:999px;padding:11px 18px;font-size:13px;font-weight:700;'>Unsubscribe</a>"
            "<p style='margin:10px 0 0;color:#5f5a55;font-size:12px;line-height:1.6;'>This will remove the alert from your saved searches in the Sofia dashboard.</p>"
            "</div>"
        )

    return f"""<html>
  <body style='margin:0;background:#fafafa;padding:24px 0;font-family:Arial,Helvetica,sans-serif;color:#181717;'>
    <div style='max-width:760px;margin:0 auto;padding:0 16px;'>
      <div style='border:2px solid #181717;border-radius:26px;overflow:hidden;background:#ffffff;box-shadow:6px 6px 0 rgba(15,23,42,0.05);'>
        <div style='display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:start;padding:14px 24px 10px;border-bottom:2px solid #181717;background:#ffffff;color:#181717;'>
          <span style='padding-top:2px;font-family:Georgia,Times New Roman,serif;font-size:18px;'>The</span>
          <strong style='font-family:Georgia,Times New Roman,serif;font-size:44px;font-weight:400;line-height:.9;letter-spacing:-.07em;text-align:center;text-transform:uppercase;'>Property Finder</strong>
          <small style='padding-top:4px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;'>Sofia edition</small>
        </div>
        <div style='padding:26px 24px 22px;'>
          <div style='display:inline-block;margin-bottom:14px;padding:7px 11px;border:1.5px solid #181717;border-radius:999px;background:#ffffff;font-size:11px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:#0f766e;'>Sofia Property Alert digest</div>
          <h1 style='margin:0 0 12px;font-family:Georgia,Times New Roman,serif;font-size:32px;font-weight:400;line-height:1.02;color:#181717;max-width:18ch;'>Look closer. Your next place is already on the map.</h1>
          <div style='display:flex;align-items:center;gap:10px;margin:0 0 12px;color:#0f766e;font-size:11px;letter-spacing:.14em;text-transform:uppercase;'>
            <span style='white-space:nowrap;'>Today's edition</span>
            <span style='flex:1;height:1px;background:#0f766e;opacity:.32;'></span>
          </div>
          <p style='margin:0;max-width:58ch;font-size:15px;line-height:1.7;color:#181717;'>Hello {escape(subscription.email)}, {escape(hero_copy)}</p>
        </div>
      </div>

      <div style='margin-top:18px;border:2px solid #181717;border-radius:26px;background:#ffffff;padding:22px;box-shadow:6px 6px 0 rgba(15,23,42,0.05);'>
        <table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='border-collapse:collapse;'>
          <tr>
            <td style='vertical-align:top;padding-right:12px;'>
              <div style='font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#0f766e;margin-bottom:4px;'>Saved search</div>
              <div style='font-family:Georgia,Times New Roman,serif;font-size:30px;line-height:1;color:#181717;max-width:18ch;'>{escape(subscription.city)} &middot; {escape(subscription.property_type.title())}</div>
              <div style='margin-top:8px;color:#5f5a55;line-height:1.6;'>{escape(subscription.transaction_type.title())} alert for {escape(subscription.email)}</div>
            </td>
            <td style='vertical-align:top;text-align:right;'>
              <span style='display:inline-block;border:1.5px solid #181717;border-radius:999px;padding:9px 14px;font-size:13px;font-weight:700;background:{status_bg};color:{status_fg};'>{escape(status_label)}</span>
            </td>
          </tr>
        </table>

        <div style='margin-top:18px;display:flex;flex-wrap:wrap;gap:10px;'>
          {_build_subscription_badges(subscription)}
        </div>
        {unsubscribe_cta}
      </div>

      <div style='margin-top:18px;'>
        <div style='margin:0 0 10px 4px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#0f766e;'>Matched listings</div>
        {listing_section}
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
            badges.append(_badge(f"EUR {min_price} - EUR {max_price}", "accent"))
        elif min_price:
            badges.append(_badge(f"From EUR {min_price}", "accent"))
        elif max_price:
            badges.append(_badge(f"Up to EUR {max_price}", "accent"))
    if subscription.min_area_sqm is not None:
        badges.append(_badge(f"Min {subscription.min_area_sqm:.0f} sq.m", "accent"))
    return "".join(badges)


def _build_listing_rows(matches: list[dict[str, object]]) -> str:
    if not matches:
        return (
            "<div style='border:2px dashed #181717;border-radius:16px;background:#ffffff;padding:18px 20px;color:#5f5a55;font-family:Georgia,Times New Roman,serif;line-height:1.6;font-size:15px;'>"
            "No listings matched this subscription today. We will keep monitoring Sofia and send the next digest when a fit appears."
            "</div>"
        )

    rows = []
    for index, match in enumerate(matches, start=1):
        title = escape(str(match["title"]))
        url = escape(str(match["url"]))
        city = escape(str(match["city"]))
        district = match.get("district")
        district_text = f", {escape(str(district))}" if district else ""
        price = _format_currency(match.get("price_eur"))
        area = _format_number(match.get("area_sqm"))
        rows.append(
            f"""<tr>
  <td style='padding:0 0 10px;'>
    <table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='border-collapse:separate;border-spacing:0;border:2px solid #181717;border-radius:16px;overflow:hidden;background:#ffffff;'>
      <tr>
        <td style='padding:11px 12px 9px;vertical-align:top;'>
          <div style='font-size:10px;letter-spacing:.10em;text-transform:uppercase;color:#0f766e;margin-bottom:3px;'>Listing {index}</div>
          <div style='font-size:15px;font-weight:700;line-height:1.25;color:#181717;margin-bottom:3px;max-width:24ch;'><a href='{url}' style='color:#181717;text-decoration:underline;text-underline-offset:4px;'>{title}</a></div>
          <div style='font-size:12px;line-height:1.35;color:#5f5a55;'>{city}{district_text}</div>
        </td>
        <td style='padding:11px 12px 9px;vertical-align:top;text-align:right;white-space:nowrap;'>
          <div style='display:inline-block;background:#ffffff;color:#181717;border:1.5px solid #181717;border-radius:999px;padding:4px 8px;font-size:11px;font-weight:700;margin-bottom:4px;'>EUR {price}</div>
          <div style='display:block;color:#5f5a55;font-size:11px;'>{area} sq.m</div>
        </td>
      </tr>
    </table>
  </td>
</tr>"""
        )
    return (
        "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='border-collapse:collapse;'>"
        + "".join(rows)
        + "</table>"
    )


def _badge(label: str, tone: str) -> str:
    styles = {
        "primary": "background:#ffffff;color:#181717;border:1.5px solid #181717;",
        "neutral": "background:#ffffff;color:#181717;border:1.5px solid #181717;",
        "accent": "background:#ffffff;color:#181717;border:1.5px solid #181717;",
    }
    return (
        f"<span style='display:inline-flex;align-items:center;border-radius:999px;"
        f"padding:8px 12px;font-size:13px;font-weight:700;line-height:1;{styles[tone]}'>"
        f"{escape(label)}</span>"
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
        unsubscribe_url = self._build_unsubscribe_url(subscription)
        digest = build_digest(subscription, matches, unsubscribe_url=unsubscribe_url)
        return self.send_message(
            OutboundMessage(
                to_email=subscription.email,
                subject=digest.subject,
                text=digest.text,
                html=digest.html,
            ),
            preview_key=f"{subscription.id}",
        )

    def send_message(
        self,
        message: OutboundMessage,
        *,
        preview_key: str,
    ) -> EmailDeliveryResult:
        preview_path = self._write_preview(message, preview_key=preview_key)
        if self.settings.email_backend == "smtp":
            error = self._send_smtp(message)
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

    def _build_unsubscribe_url(self, subscription: SubscriptionView) -> str:
        base_url = self.settings.app_base_url.rstrip("/")
        return f"{base_url}/subscriptions/{subscription.unsubscribe_token}/unsubscribe"

    def _write_preview(
        self,
        message: OutboundMessage,
        *,
        preview_key: str,
    ) -> str:
        preview_dir = Path(self.settings.email_preview_dir)
        preview_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}-{preview_key}.eml"
        path = preview_dir / filename
        email_message = EmailMessage()
        email_message["To"] = message.to_email
        email_message["From"] = self.settings.email_from
        email_message["Subject"] = message.subject
        email_message.set_content(message.text)
        email_message.add_alternative(message.html, subtype="html")
        path.write_text(email_message.as_string(), encoding="utf-8")
        return str(path)

    def _send_smtp(self, message: OutboundMessage) -> str | None:
        email_message = EmailMessage()
        email_message["To"] = message.to_email
        email_message["From"] = self.settings.email_from
        email_message["Subject"] = message.subject
        email_message.set_content(message.text)
        email_message.add_alternative(message.html, subtype="html")

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
                    client.send_message(email_message)
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
                client.send_message(email_message)
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
