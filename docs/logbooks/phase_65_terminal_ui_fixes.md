# Phase 65: Terminal UI Formatting & Polish

## Goals
Fix text formatting, eliminate raw Rich markup from being displayed literally, implement a cleaner layout, and dynamically display the active LLM provider and model.

## Changes Made
- Modified `core/runtime/runtime.py` to expose `llm.provider` and `llm.model` in the `get_status` response so the UI can fetch it.
- Switched the Textual app's `Log` widget to `RichLog` in `apps/terminal/app.py` to properly support Rich rendering objects.
- Removed literal markup from strings and implemented explicit `Text` object creation to ensure formatting is evaluated.
- Upgraded the `StatusPanel` component to render a cleanly formatted Rich `Table` instead of a plain string, displaying the dynamic provider and model underneath the system status.
- Designed a distinct layout using `Horizontal` and `Vertical` layouts to clearly separate the mascot placeholder from the main conversational chat area.
- Replaced the temporary mascot ASCII art in `apps/terminal/mascot.py` with a simple placeholder boundary `[ MASCOT AREA ]` to keep the UI clean until graphical assets are integrated.
- Updated styles to reflect the intended dark background (`#0f111a`), warm gold accents (`#d4af37`), and muted blue secondary colors (`#4a6fa5`).
- Updated `tests/terminal/test_mascot.py` to reflect the new placeholder state fallback behavior.

## Verification
- Run `pytest tests/terminal/test_mascot.py` and verify all tests pass.
- Run `python scripts/narada.py chat` and verify no raw rich tags are displayed and that the status header renders a two-line layout containing the model name.

## Next Steps
- Implement graphical integration for the mascot assets once provided.
