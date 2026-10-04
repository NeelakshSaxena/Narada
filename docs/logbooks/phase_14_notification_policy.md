# Phase 14: Away-Mode Notification Policy Logbook

## Objective
Prevent notification spam by implementing strict notification policies (`silent`, `informational`, `important`, `urgent`, `approval_required`) and robust event deduplication based on source signatures and payload hashing.

## Branch
`phase/14-notification-policy`

## Changes Made
- Created the `EventDeduplicator` (`core/events/dedup.py`) which generates stable signatures for events using either their native external IDs or deterministic SHA-256 payload hashes.
- Integrated the deduplicator natively into the `EventPipeline` so duplicate events are short-circuited before ever hitting persistence or triggering the LLM evaluator.
- Established `NotificationPolicy` and a `PolicyEvaluator` (`core/notifications/policy.py`) that uses an LLM to categorize the execution outcome of an event into an explicit spam-prevention tier.

## Testing & Verification
- Unit test `test_event_deduplication` proves that duplicate events (identical payloads from identical sources or identical external IDs) are properly flagged, while uniquely modified payloads correctly generate new signatures.
- Unit test `test_policy_evaluator` simulates mock LLM responses to prove the parsing and fallback logic correctly maps raw execution outputs to the strict `NotificationPolicy` enums.

## Exit Criteria Checklist
- [x] Implemented `NotificationPolicy` classifications.
- [x] Built the `EventDeduplicator` based on external IDs or payload hashes.
- [x] Integrated Deduplicator into the `EventPipeline`.
- [x] Tested deduplication and policy evaluations deterministically.

## Pre-Merge Status
All requirements for Phase 14 are fulfilled.
