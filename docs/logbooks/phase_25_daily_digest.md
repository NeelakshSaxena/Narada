# Phase 25: Daily Digest Logbook

## Objective
Enable Nārada to autonomously compile and dispatch a "Daily Digest" summarizing the work it performed overnight, failures that occurred, and items requiring user attention, strictly separating raw logs from the intelligent briefing.

## Branch
`phase/25-daily-digest`

## Changes Made
- Introduced `DailyState` to structure overnight telemetry (`meaningful_events`, `completed_work`, `failures`, `pending_approvals`, `important_changes`, `blocked_responsibilities`).
- Built the `DigestGenerator` in `core/reports/digest.py` to marshal structured state into a natural language prompt.
- Enforced the exact "Daily Digest Prompt" from the specification to guarantee that Nārada answers four critical questions per item (what happened, why it matters, what was done, what the user must do) without hallucinating or leaking secrets.

## Testing & Verification
- Unit test `test_daily_digest_prompt_construction` strictly verifies that the engine injects the structured state data perfectly into the required LLM prompt template.
- Unit test `test_daily_digest_generation` confirms the generator correctly calls the LLM interface and returns the summarized digest.

## Exit Criteria Checklist
- [x] Defined `DailyState` struct.
- [x] Created `DigestGenerator` logic.
- [x] Implemented exact prompt constraints.
- [x] Verified via deterministic tests.

## Pre-Merge Status
All requirements for Phase 25 are fulfilled.
