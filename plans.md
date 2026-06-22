
## Current checkpoint

- Completed: the fixture-backed subscription PoC, persisted daily job, app-level scheduler settings with both interval and daily-time modes, minimal HTML/text digest, local `.eml` previews, configurable Gmail SMTP delivery, visible delivery outcomes, permanent subscription deletion, unsubscribe/reactivate flows, search-progress UI feedback, test isolation, local test-data cleanup, the real imot.bg parser rewrite with canonical listing URLs and district normalization, and an imot.bg-aligned catalog/UI for cities, districts, transaction types, property types, and room filters.
- Current proof of concept: users can create, unsubscribe, reactivate, or permanently delete a subscription; unsubscribe clears the current matches and reactivate repopulates them immediately. The app can run the listing job manually or on a global saved schedule using either every N minutes or a fixed daily time.
- Email direction: Gmail API OAuth 2.0 is the recommended password-free option. Implementation is pending explicit approval because it requires Google Cloud OAuth credentials and token handling.
- Next slice: implement the approved OAuth flow, then expand idempotency, scheduler edge-case, reactivation, and partial-failure tests.
