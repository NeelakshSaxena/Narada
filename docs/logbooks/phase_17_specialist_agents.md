# Phase 17: Specialist Agents Logbook

## Objective
Build the core architecture for `Specialist` agents, allowing Nārada to act as the chief agent delegating isolated tasks to sub-agents (e.g., Researcher, Coder) via a strict delegation contract.

## Branch
`phase/17-specialist-agents`

## Changes Made
- Engineered the `Specialist` base class in `core/specialists/base.py`.
- Formally defined the `DelegationInput` and `DelegationOutput` schemas to ensure a strict contract (inputs: `task_id`, `objective`, `constraints`, `allowed_tools`, `workspace`; outputs: `status`, `summary`, `artifacts`, `evidence`).
- Implemented the "Delegation Prompt" system into the core architecture, enforcing that specialists understand they are isolated workers and must strictly report failures and stay within boundaries.

## Testing & Verification
- Test `test_specialist_delegation_contract` successfully mocks a delegation to a Researcher specialist, ensuring inputs are correctly injected into the delegation prompt and the output JSON schema is accurately enforced and parsed.
- Test `test_specialist_parse_failure` proves that the system handles malformed output from sub-agents gracefully.

## Exit Criteria Checklist
- [x] Built the core `Specialist` architecture.
- [x] Defined the standard "Delegation Contract".
- [x] Implemented the "Delegation Prompt" system.
- [x] Tested delegation and failure gracefully.

## Pre-Merge Status
All requirements for Phase 17 are fulfilled.
