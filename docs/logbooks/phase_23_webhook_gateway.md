# Phase 23: Webhook Gateway Logbook

## Objective
Establish a secure boundary for external webhooks (e.g., GitHub, Stripe) to awaken Nārada, explicitly enforcing safety via cryptographic validation rather than blindly trusting the endpoint invocation.

## Branch
`phase/23-webhook-gateway`

## Changes Made
- Created `core/gateway/webhook.py` containing `WebhookGateway` and `WebhookSecurity`.
- Implemented robust security policies before any dispatch occurs:
  - Validated HMAC SHA-256 signatures against incoming payloads.
  - Enforced a timestamp threshold (`max_age_seconds`) to block stale requests.
  - Built an event ID history cache to block malicious or duplicate replay attacks.
- Integrated the secure payload normalizer to safely extract intent.

## Testing & Verification
- Unit test `test_webhook_security_success` verifies a properly signed, timely, unique event is cleanly dispatched.
- Unit test `test_webhook_security_invalid_signature` actively asserts that tampering with the payload or signature is strictly rejected.
- Unit test `test_webhook_security_replay` verifies that repeating the exact same valid payload+signature is safely blocked due to the known event ID.
- Unit test `test_webhook_security_timestamp` confirms that a cryptographically valid event from the distant past is safely discarded.

## Exit Criteria Checklist
- [x] Implemented secure webhook receiver endpoint.
- [x] Verified HMAC signatures.
- [x] Enforced timestamp staleness checks.
- [x] Implemented replay protection logic.

## Pre-Merge Status
All requirements for Phase 23 are fulfilled.
