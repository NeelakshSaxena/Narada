# Phase 12: Event-Driven Wakeups Logbook

## Objective
Enable Nārada to wake up because something explicitly happened, transforming it from a simple polling agent into a reactive, event-driven autonomous worker.

## Branch
`phase/12-event-driven-wakeups`

## Changes Made
- Created the core `Event` schema (`core/events/models.py`) to handle standardized properties: `type`, `payload`, `source`, `id`, and `timestamp`.
- Built the `EventPipeline` in `core/events/pipeline.py`, strictly mapping to the blueprint architecture: `normalize -> persist -> match responsibilities -> filter irrelevant -> wake relevant responsibility -> execute`.
- Embedded an LLM evaluator directly inside the pipeline (`filter_irrelevant`) to intelligently discard spam or irrelevant events by comparing the event payload against the target responsibility's goal.

## Testing & Verification
- Test `test_event_pipeline` injects a mock `github.push` event and uses a deterministic LLM mock to verify that the event successfully matches the Github responsibility trigger, passes the LLM relevance filter, and explicitly triggers execution while ignoring mismatched responsibilities.

## Exit Criteria Checklist
- [x] Built the `Event` schema.
- [x] Constructed the structured `EventPipeline`.
- [x] Implemented LLM event filtering before execution.
- [x] Proven behavior via deterministic tests.

## Pre-Merge Status
All requirements for Phase 12 are fulfilled.
