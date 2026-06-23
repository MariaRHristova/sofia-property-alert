## Current checkpoint

- Completed: the fixture-backed subscription PoC, persisted daily job, email digest rendering and SMTP/preview delivery, scheduler settings with interval and daily-time modes, unsubscribe/reactivate/delete flows, the real imot.bg parser rewrite with canonical listing URLs and district normalization, and authenticated user accounts with email verification, password reset, private dashboards, per-user scheduler settings, and per-user manual job controls.
- Current proof of concept: each verified user can register, sign in, create Sofia-only subscriptions, run their own listing job manually, save their own scheduler interval, receive preview or SMTP emails, and manage only their own alerts.
- Email direction: Gmail SMTP remains available through `.env`; Gmail API OAuth 2.0 is still the recommended future password-free delivery option and remains pending explicit approval.
- Next slice: implement the approved Gmail OAuth flow, then add browser-based UI verification screenshots and expand deeper scheduler edge-case and auth-session expiry coverage.
