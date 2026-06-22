from __future__ import annotations

import smtplib
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
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
    if not matches:
        return (
            "<html><body style=\"font-family:Arial,sans-serif;line-height:1.5;\">"
            "<h1 style=\"margin-bottom:0.5rem;\">Bulgaria Property Alert</h1>"
            "<p>Hello {email},</p>"
            "<p><strong>There are no available listings</strong> "
            "for your saved criteria today.</p>"
            "<p>We will keep checking and send the next digest when matches appear.</p>"
            "<p style=\"color:#666;\">"
            "Criteria: {city}, {transaction_type}, {property_type}</p>"
            "</body></html>"
        ).format(
            email=subscription.email,
            city=subscription.city,
            transaction_type=subscription.transaction_type,
            property_type=subscription.property_type,
        )

    html_matches = []
    for match in matches:
        title = str(match["title"])
        url = str(match["url"])
        city = str(match["city"])
        district = match.get("district")
        price = match.get("price_eur")
        area = match.get("area_sqm")
        html_matches.append(
            (
                "<li><a href=\"{url}\">{title}</a> - {city}{district} - "
                "{price} EUR - {area} sq.m</li>"
            ).format(
                url=url,
                title=title,
                city=city,
                district=f", {district}" if district else "",
                price=price if price is not None else "N/A",
                area=area if area is not None else "N/A",
            )
        )

    return (
        "<html><body style=\"font-family:Arial,sans-serif;line-height:1.5;\">"
        "<h1 style=\"margin-bottom:0.5rem;\">Bulgaria Property Alert</h1>"
        "<p>Hello {email},</p>"
        "<p>We found <strong>{count}</strong> matching listings for your alert.</p>"
        "<ul>{matches}</ul>"
        "</body></html>"
    ).format(
        email=subscription.email,
        count=len(matches),
        matches="".join(html_matches),
    )


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
