# Phase 64: Mascot Terminal UI

## Goals
Implement the Narada terminal interface as a real interactive terminal application, with an animated mascot that reacts to the agent's runtime state.

## Changes Made
- Added `textual` and `rich` dependencies to `pyproject.toml`.
- Created `apps/terminal/mascot.py` implementing the `MascotWidget` with subtle, geometric ASCII frames for `idle`, `thinking`, `searching`, `working`, `success`, `error`, and `sleeping` states.
- Created `apps/terminal/app.py` implementing the `NaradaTerminalUI` Textual application. It combines a `StatusPanel`, a `MascotWidget`, a `Log` for chat, and an `Input` for user queries.
- Wired up `/audit`, `/memory`, and `/forget` slash commands directly into the Textual event loop.
- Ensured background tasks do not freeze the UI when sending HTTP requests to the Narada backend.
- Wrote integration tests for Mascot Widget state changes and Textual application input flow using `asyncio.run()` in `tests/terminal/test_mascot.py`.
- Updated `scripts/narada.py` to launch `NaradaTerminalUI` when running `narada chat`.

## Verification
- Run `pytest tests/terminal/test_mascot.py` to ensure state transition and input submission tests pass.
- Run `python scripts/narada.py chat` to launch the terminal application and verify mascot animations and layout adapt to inputs and window resizing.

## Next Steps
- Consider further styling refinements or integration with the actual Event Bus to stream logs and system events directly to the UI.
