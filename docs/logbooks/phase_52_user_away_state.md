# Phase 52: User Away State Logbook

## Objective
Implement awareness of user availability, away states, and quiet hours to determine correct message delivery policies.

## Branch
`phase/52-user-away-state`

## Changes Made
- Added `DeliveryManager` in `core/notifications/delivery.py`.
- Defined `UserState` (AVAILABLE, AWAY, DND), `QuietHours`, and `DeliveryDecision` (NOTIFY, QUEUE, DISCARD).
- The delivery logic properly inspects event priority via `NotificationPolicy` and respects quiet hour overrides.

## Testing & Verification
- Test `test_delivery` asserts different delivery flows depending on availability states, including correct routing inside and outside of `QuietHours`.

## Exit Criteria Checklist
- [x] Evaluates User Away / DND states.
- [x] Evaluates Quiet Hours.
- [x] Correlates policy severity with user availability.

## Pre-Merge Status
All requirements for Phase 52 are fulfilled.
