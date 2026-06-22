
## Current checkpoint

- Completed: the fixture-backed subscription PoC, persisted daily job, minimal HTML/text digest, local `.eml` previews, configurable Gmail SMTP delivery, visible delivery outcomes, permanent subscription deletion, test isolation, local test-data cleanup, the real imot.bg parser rewrite with canonical listing URLs and district normalization, and an imot.bg-aligned catalog/UI for cities, districts, transaction types, property types, and room filters.
- Current proof of concept: users can create, unsubscribe, or permanently delete a subscription; deletion also removes its match history. Clicking **Run daily job** reports preview, delivery success, or delivery failure.
- Email direction: Gmail API OAuth 2.0 is the recommended password-free option. Implementation is pending explicit approval because it requires Google Cloud OAuth credentials and token handling.
- Next slice: implement the approved OAuth flow or scheduled execution, then expand idempotency and partial-failure tests.
