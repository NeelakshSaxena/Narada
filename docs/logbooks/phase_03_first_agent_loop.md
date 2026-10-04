# Phase 3: First Agent Loop Logbook

## Objective
Implement the foundational, stateful agent loop (Goal → Plan → Action → Observation → Decision) natively in the backend runtime. Establish strict execution boundaries so the LLM can only propose actions, while the runtime validates and executes them.

## Branch
`phase/03-first-agent-loop`

## Changes Made
- Defined `AgentState` schema (`core/agent/state.py`) capturing `run_id`, `goal`, `plan`, `current_step`, `actions`, `observations`, `decision`, `status`, and timestamps.
- Implemented `AgentStatus` Enum mapping the transitions: `RUNNING → PLANNING → EXECUTING → OBSERVING → DECIDING → COMPLETED`.
- Created `ToolRegistry` (`core/tools/registry.py`) to manage allowed tools.
- Built `Executor` (`core/agent/executor.py`) to explicitly validate that requested actions exist in the `ToolRegistry` before execution, preventing raw LLM shell command execution.
- Engineered `AgentLoop` (`core/agent/loop.py`) handling the deterministic while-loop iterating over the `AgentStatus` states.
- Authored a deterministic test in `tests/agent/test_loop.py` using a `ScriptedLLMProvider` to mathematically prove the state machine terminates and behaves correctly without needing a live LLM model.

## Testing & Verification
- Test `test_agent_loop_deterministic_completion` verifies that the state transitions perfectly from `RUNNING` through the steps to `COMPLETED`.
- Verifies that `Executor` properly catches unauthorized/unknown tool requests by enforcing registry lookup.
- Validated that agent state exists as a strictly typed Python `dataclass`, not merely as prompt text.

## Exit Criteria Checklist
- [x] State is explicitly typed (`AgentState`), not just prompt text.
- [x] Execution goes through an explicit executor (`Executor` + `ToolRegistry`).
- [x] LLM output cannot directly execute shell commands (all actions route through registered tools).
- [x] The loop terminates deterministically (proven via test).
- [x] FakeLLMProvider / ScriptedLLMProvider demonstrates the loop fully.

## Pre-Merge Status
All requirements for Phase 3 are fulfilled.
