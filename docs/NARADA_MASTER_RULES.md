# NĀRADA — MASTER ENGINEERING RULES

> **Status:** Authoritative
>
> **Applies to:** Human developers, AI coding agents, autonomous implementation agents, reviewers, and future contributors.
>
> **Purpose:** Define the non-negotiable rules for designing, implementing, testing, operating, documenting, and evolving Nārada.
>
> **Core principle:** Nārada is a personal autonomous agent runtime. The user gives Nārada responsibilities; Nārada turns them into goals, tasks, actions, observations, memory, and continued work while respecting permissions, approvals, safety, privacy, and cost.
>
> **Motto:** **Don't build the bricks. Build the temple. But build the temple one verified brick at a time.**

---

# 1. Authority and Precedence

These rules are the default engineering authority for Nārada.

When implementing anything:

1. Read this file.
2. Read `AGENTS.md`.
3. Read the current phase specification in the detailed build document.
4. Read `NARADA_GITHUB_RULES.md` before creating or modifying a phase branch.
5. Read the current phase logbook.
6. Inspect the existing implementation before changing it.
7. Preserve established interfaces unless there is a documented reason to change them.
8. Record important deviations in the phase logbook.

If documents conflict:

```text
Safety / security rule
        ↓
This MASTER RULES file
        ↓
AGENTS.md
        ↓
Phase-specific specification
        ↓
Implementation preference
```

If ambiguity remains, **stop and document the ambiguity rather than guessing**.

---

# 2. The Golden Rule

> **The LLM proposes. The runtime decides.**

The model may propose:

- plans
- actions
- tool calls
- hypotheses
- classifications
- next steps

The runtime must independently enforce:

- permissions
- approvals
- tool availability
- schemas
- budgets
- sandbox boundaries
- identity
- authentication
- safety policy
- execution limits
- audit requirements

Never allow model output to bypass runtime controls.

---

# 3. The Second Golden Rule

> **Capability is not permission.**

The fact that Nārada can technically perform an action does not mean Nārada is authorized to perform it.

Every action must be evaluated as:

```text
CAPABILITY
PERMISSION
RISK
APPROVAL
AUDIT
```

Example:

```text
shell.execute
    capability: YES
    permission: MAYBE
    risk: HIGH
    approval: REQUIRED
    audit: REQUIRED
```

---

# 4. The Third Golden Rule

> **Persistent responsibilities are more important than individual conversations.**

Nārada is not primarily a chatbot.

The core abstraction is:

```text
USER
 ↓
RESPONSIBILITY
 ↓
GOAL
 ↓
PLAN
 ↓
TASKS
 ↓
ACTIONS
 ↓
OBSERVATIONS
 ↓
MEMORY
 ↓
RE-EVALUATION
 ↓
CONTINUE / WAIT / COMPLETE
```

A conversation is one interface into this system.

---

# 5. NON-NEGOTIABLE LOGBOOK RULE

## Every implementation phase MUST have a logbook.

This is mandatory.

No phase is considered complete without its logbook.

The logbook must record, throughout implementation:

- what was done
- what remains
- what was attempted
- what worked
- what failed
- exact errors encountered
- why the error happened
- how the error was fixed
- files changed
- important design decisions
- tests run
- tests failed
- verification performed
- unresolved issues
- deviations from the specification
- temporary workarounds
- commands or procedures that were useful
- lessons learned

---

# 6. Logbook Must Be Maintained DURING Work

Do not reconstruct the logbook at the end from memory.

The agent must update the logbook as work happens.

Bad:

```text
build phase
build everything
write summary afterward
```

Required:

```text
start phase
 ↓
create logbook
 ↓
implement step
 ↓
record result
 ↓
encounter error
 ↓
record error
 ↓
fix error
 ↓
record fix
 ↓
run test
 ↓
record test
 ↓
continue
```

The logbook is an engineering artifact, not a diary.

---

# 7. Phase Logbook Naming

Every phase should have its own logbook.

Recommended:

```text
docs/
└── logs/
    ├── phase-00-logbook.md
    ├── phase-01-logbook.md
    ├── phase-02-logbook.md
    ├── phase-03-logbook.md
    └── ...
```

Do not use one enormous continuously edited log for every phase.

Each phase gets its own working log.

---

# 8. Phase Logbook Template

Every phase logbook MUST begin with:

```markdown
# Phase XX — <Phase Name> — Logbook

## Phase Objective

<What this phase is supposed to achieve>

## Start Date

YYYY-MM-DD

## Status

IN_PROGRESS

## Specification

<Reference to phase specification>

## Exit Criteria

- [ ] criterion
- [ ] criterion
- [ ] criterion

---

## Work Log
```

---

# 9. Work Log Format

Each significant implementation step should look like:

```markdown
### YYYY-MM-DD HH:MM — <Short Description>

**Action**

<What was attempted>

**Result**

<SUCCESS / PARTIAL / FAILED / BLOCKED>

**Files**

- `path/to/file.py`
- `path/to/test.py`

**Tests**

- `pytest ...`
- Result: PASS / FAIL

**Notes**

<Relevant details>
```

---

# 10. Error Log Format

Every meaningful error gets an explicit entry.

```markdown
## Error: <Short Error Name>

### Symptom

<What happened>

### Error

```text
<relevant error output>
```

### Cause

<Why it happened>

### Fix

<What was changed>

### Verification

<How the fix was proven>

### Regression Test

<Test added or updated>

### Status

RESOLVED
```

Do not hide failures because they were eventually fixed.

Failures are valuable engineering history.

---

# 11. Unresolved Issue Format

If an issue cannot be solved:

```markdown
## Unresolved Issue: <Name>

### Problem

...

### Impact

...

### What Was Tried

...

### Current Workaround

...

### Why It Is Not Yet Resolved

...

### Required Follow-up

...

### Blocking?

YES / NO
```

Never silently leave known broken behavior.

---

# 12. Phase Completion Logbook Rule

When all phase work is complete:

1. Stop implementation.
2. Run the complete phase verification suite.
3. Confirm every exit criterion.
4. Review the entire logbook.
5. Produce a concise but technically complete phase summary.
6. Append the summary to the **end of the phase logbook**.
7. Mark the phase `COMPLETE`.
8. Record unresolved/non-blocking issues.
9. Record lessons learned.
10. Only then begin the next phase.

The next phase MUST NOT start before the previous phase has been formally closed.

---

# 13. Phase Summary Format

Append this to the end of the phase logbook:

```markdown
---

# Phase Completion Summary

## Final Status

COMPLETE

## Objective

<What the phase was intended to achieve>

## What Was Implemented

- ...
- ...
- ...

## What Was Verified

- ...
- ...
- ...

## Tests

- Total:
- Passed:
- Failed:
- Skipped:
- Known limitations:

## Errors Encountered

- <error>
  - cause:
  - fix:

## Important Decisions

- ...
- ...

## Deviations From Specification

- None

OR:

- ...
  - reason:
  - impact:
  - follow-up:

## Remaining Issues

- None

OR:

- ...

## Lessons Learned

- ...
- ...

## Files / Components Added

- ...

## Files / Components Changed

- ...

## Readiness For Next Phase

READY

## Next Phase

Phase XX+1 — <Name>

## Completion Date

YYYY-MM-DD
```

---

# 14. Never Delete Engineering History

Do not erase:

- failed attempts
- errors
- temporary fixes
- test failures
- reverted approaches
- important decisions

If something becomes obsolete, mark it obsolete.

History helps future agents understand why the system looks the way it does.

---

# 15. No Silent Changes

Never make an architectural change silently.

If implementation differs from the specification:

```text
change
+
reason
+
impact
+
verification
```

must be recorded.

---

# 16. Inspect Before Editing

Before modifying code:

1. locate the relevant module
2. read the surrounding implementation
3. inspect tests
4. understand interfaces
5. check configuration
6. check existing dependencies
7. check the current phase logbook

Do not blindly overwrite files.

---

# 17. Minimal Change Principle

Make the smallest change that correctly solves the current problem.

Do not:

- refactor unrelated modules
- rename unrelated APIs
- introduce a framework unnecessarily
- rewrite working code for style
- migrate infrastructure without a reason

Prefer:

```text
small change
+
test
+
verification
```

over:

```text
large refactor
+
hope
```

---

# 18. One Phase at a Time

Do not implement future phases prematurely.

If the current phase is:

```text
SQLite memory
```

do not simultaneously build:

```text
Qdrant
Redis
PostgreSQL
AWS
mobile app
voice
```

unless the current phase explicitly requires them.

Future work may be documented as:

```text
NEXT PHASE
```

but should not leak into implementation without justification.

---

# 19. Phase Exit Criteria Are Gates

A phase is not complete because:

```text
code exists
```

It is complete only when:

```text
implementation
+
tests
+
verification
+
documentation
+
logbook summary
+
exit criteria
```

all pass.

---

# 20. Stop Conditions Are Real

When a specification says:

```text
STOP
```

the agent must stop.

Do not bypass a stop condition because:

- the next step looks easy
- the model thinks it knows the answer
- the user may appreciate extra work
- a dependency is inconvenient
- a test is annoying

Stop conditions exist to prevent architectural drift and unsafe behavior.

---

# 21. Verification Before Progression

After every significant implementation unit:

```text
IMPLEMENT
 ↓
TEST
 ↓
VERIFY
 ↓
LOG
 ↓
CONTINUE
```

Never:

```text
IMPLEMENT
 ↓
IMPLEMENT
 ↓
IMPLEMENT
 ↓
TEST EVERYTHING
```

This makes failures harder to isolate.

---

# 22. Test-First Where Practical

For core logic, prefer:

```text
test
 ↓
implementation
 ↓
test
 ↓
verification
```

Especially for:

- permissions
- approvals
- scheduler
- responsibilities
- memory
- event routing
- tool registry
- provider routing
- sandbox policy
- state transitions

---

# 23. Deterministic Tests

Tests must not depend unnecessarily on:

- real LLM behavior
- real internet
- real API availability
- real time
- external messaging
- production credentials

Use fakes:

```text
FakeLLM
FakeClock
FakeEventBus
FakeGitHub
FakeEmail
FakeTelegram
FakeSandbox
```

Live integration tests should be separate.

---

# 24. Live API Tests

Live API tests must:

- be explicitly marked
- require credentials
- never run accidentally in the normal unit suite
- avoid expensive calls
- avoid destructive actions
- never expose credentials in logs

Example categories:

```text
unit
integration
live
e2e
security
```

---

# 25. No Secret Leakage

Never log:

- API keys
- access tokens
- refresh tokens
- passwords
- cookies
- private keys
- session secrets
- webhook signing secrets

Redact:

```text
Authorization
X-API-Key
Bearer ...
token=...
api_key=...
```

when they appear in errors.

---

# 26. Environment Configuration

Secrets belong in environment/configuration systems.

Never hard-code:

```python
API_KEY = "..."
```

Use:

```env
SARVAM_API_KEY=
ELEVENLABS_API_KEY=
GITHUB_TOKEN=
```

and load through configuration.

---

# 27. Provider-Agnostic Core

Core code must not depend directly on:

```text
Sarvam SDK
ElevenLabs SDK
Ollama implementation
GitHub SDK
Telegram SDK
```

Use provider interfaces.

Conceptually:

```python
class LLMProvider:
    ...
```

Then:

```text
SarvamProvider
OllamaProvider
OpenAICompatibleProvider
```

---

# 28. External APIs Should Usually NOT Be Containers

Do not create containers for:

```text
Sarvam
ElevenLabs
OpenAI
Anthropic
GitHub
Telegram
Google
Notion
Slack
```

These are external services.

Nārada uses adapters.

---

# 29. Local Model Services

Ollama should normally run outside the Nārada core container.

Preferred:

```text
host
└── Ollama
       ↑
       │ HTTP
       │
Docker
└── narada-core
```

Do not duplicate the GPU model runtime inside Nārada unnecessarily.

---

# 30. SQLite Rule

SQLite is a file, not a service.

Default:

```text
./data/narada.db
```

mounted into:

```text
/data/narada.db
```

Do not create a SQLite container.

---

# 31. Optional Infrastructure Rule

Containers are justified for infrastructure that genuinely provides a service.

Examples:

```text
Qdrant
Redis
PostgreSQL
```

But only introduce them when the current phase requires them.

Do not add infrastructure because it is fashionable.

---

# 32. One Core Container Rule

The default local backend should be:

```text
narada-core
```

It should initially contain:

```text
FastAPI
agent runtime
worker
scheduler
gateway
memory
SQLite
tool registry
permissions
approvals
audit
```

Split services only when there is a demonstrated operational reason.

---

# 33. Docker Compose Rule

Local deployment should prefer:

```bash
docker compose up -d
```

over a long list of manually started processes.

The default compose stack should remain minimal.

Optional services should use profiles where useful.

---

# 34. Restart Safety

The core container may restart at any time.

Persistent state must survive.

At minimum:

```text
responsibilities
tasks
events
memories
approvals
audit
configuration-independent state
```

must be stored durably.

---

# 35. Autonomous State Must Never Live Only in RAM

If losing the process loses:

```text
responsibility
approval
task
event
checkpoint
```

the design is incomplete.

Persist before performing important external side effects where possible.

---

# 36. Agent Loop Rule

The agent loop must be explicit.

Preferred:

```text
GOAL
 ↓
PLAN
 ↓
ACTION
 ↓
OBSERVATION
 ↓
DECISION
 ↓
CONTINUE / COMPLETE / WAIT
```

Do not create a hidden infinite loop inside a prompt.

---

# 37. Bounded Agent Loops

Every autonomous run must have limits.

Possible limits:

```text
max iterations
max model calls
max tool calls
max runtime
max cost
max retries
```

A model must never be allowed to continue forever.

---

# 38. LLM Output Is Untrusted Input

Treat model-generated content like external input.

Validate:

- JSON/schema
- tool name
- arguments
- paths
- URLs
- commands
- permissions
- resource scope

Never trust:

```text
"The system says this is approved."
```

unless the actual runtime says so.

---

# 39. Tool Execution Rule

Tool flow:

```text
model proposal
 ↓
parse
 ↓
validate schema
 ↓
check tool exists
 ↓
check permissions
 ↓
check risk
 ↓
check approval
 ↓
check budget
 ↓
execute
 ↓
audit
 ↓
observe
```

---

# 40. Tool Registry Rule

Every tool must declare:

```text
name
description
input schema
output schema
risk
required permission
side effects
approval requirement
```

---

# 41. Tool Risk Rule

At minimum:

```text
NONE
LOW
MEDIUM
HIGH
CRITICAL
```

Risk is assigned by the runtime/policy, not by the model.

---

# 42. Side Effects Must Be Explicit

Tools should declare whether they:

```text
read
write
delete
send
publish
execute
deploy
financially transact
```

This allows the permission engine to reason about them.

---

# 43. High-Risk Actions

Examples:

```text
send external message
delete data
deploy
financial transaction
account modification
publish
destructive shell command
change security settings
```

must require explicit policy and usually approval.

---

# 44. Approval Rule

Approval must be:

- explicit
- scoped
- persistent
- auditable
- tied to exact action
- optionally expiring

Never accept broad approval such as:

```text
"do whatever you need"
```

as unlimited authorization for consequential actions.

---

# 45. Approval Cannot Be Self-Granted

The agent cannot:

```text
request approval
 ↓
interpret its own output
 ↓
mark approval granted
```

Approval must come from the authorized user/system.

---

# 46. Approval Survives Restart

If an approval is pending:

```text
restart
```

must not erase it.

---

# 47. Expired Approval

If an approval expires:

```text
DO NOT EXECUTE
```

Request fresh approval.

---

# 48. No Blind Retry of Side Effects

For:

```text
email
message
deployment
purchase
commit
external API mutation
```

a timeout does not prove failure.

Before retrying:

```text
determine whether the action may already have happened
```

Then reconcile.

---

# 49. Idempotency

Where possible, external actions must use idempotency keys or equivalent reconciliation.

Example:

```text
action_id
```

should uniquely identify one intended side effect.

---

# 50. Audit Everything Important

Record:

```text
who
what
when
why
tool
target
permission
approval
result
run_id
```

Especially:

- external writes
- deletions
- deployments
- messages
- permission changes
- memory deletion
- provider changes

---

# 51. Memory Rule

Do not store everything.

Memory should pass through:

```text
candidate
 ↓
relevance
 ↓
importance
 ↓
durability
 ↓
store
```

---

# 52. Memory Categories

Maintain conceptual separation:

```text
working
episodic
semantic
responsibility
```

---

# 53. Working Memory

Working memory is temporary execution state.

It may include:

```text
current plan
current observations
current task
tool results
temporary hypotheses
```

It should not automatically become permanent memory.

---

# 54. Episodic Memory

Episodic memory records meaningful past events.

Examples:

```text
completed project
important decision
successful deployment
important failure
user-approved action
```

---

# 55. Semantic Memory

Semantic memory contains stable knowledge.

Examples:

```text
project architecture
important preferences
stable facts
long-term information
```

---

# 56. Responsibility Memory

Responsibility memory tracks ongoing work:

```text
last checked
last meaningful change
current state
known blockers
last successful action
next expected check
```

This is essential for autonomous monitoring.

---

# 57. Vector Database Rule

Qdrant is optional.

Do not introduce it until:

```text
SQLite + FTS
```

is insufficient.

If Qdrant fails, Nārada should ideally degrade to simpler retrieval rather than becoming completely unusable.

---

# 58. Scheduler Rule

The scheduler triggers work.

It is not the agent.

Flow:

```text
scheduler
 ↓
responsibility due
 ↓
create run
 ↓
agent
```

---

# 59. Event Rule

Events should wake relevant responsibilities.

Do not wake the entire agent for every event.

Flow:

```text
event
 ↓
persist
 ↓
match
 ↓
filter
 ↓
wake relevant responsibility
```

---

# 60. Event Deduplication

Use external event IDs where available.

Otherwise derive stable event identity.

Never notify repeatedly because the same event arrived through:

```text
webhook
polling
email
```

---

# 61. Event Batching

If many related events arrive:

```text
deduplicate
 ↓
batch
 ↓
evaluate once
```

This reduces:

- cost
- latency
- notification spam

---

# 62. Away Mode Rule

Nārada must be able to operate while the user is absent.

Required capabilities:

```text
persistent state
scheduler
event wakeups
background worker
notification delivery
approval persistence
recovery
audit
```

---

# 63. Quiet Hours

User may configure:

```text
quiet hours
do-not-disturb
urgent bypass
```

Never silently discard notifications.

Queue them when appropriate.

---

# 64. Notification Priority

At minimum:

```text
silent
informational
important
urgent
approval_required
```

---

# 65. Notification Deduplication

Before notifying:

```text
Was this fact already delivered?
```

If yes:

```text
update state
do not spam user
```

---

# 66. Channel Rule

Channels are interfaces, not separate agents.

All channels feed the same:

```text
identity
session
responsibility
memory
agent
```

---

# 67. Channel Identity

Never rely solely on:

```text
display name
```

Use:

```text
provider
external user ID
channel
verified identity
```

---

# 68. Channel Pairing

New messaging channels should be explicitly paired with the Nārada account.

Unknown users should not gain access to private responsibilities.

---

# 69. Email Rule

Email may be:

```text
input channel
notification channel
event source
```

Inbound emails should be normalized into events.

Outbound email should obey communication permissions.

---

# 70. Phone Rule

Phone calls are consequential external actions.

Nārada must not call people automatically merely because it can.

Phone architecture should be a channel adapter:

```text
telephony
 ↓
STT
 ↓
Nārada
 ↓
TTS
 ↓
telephony
```

---

# 71. Voice Rule

Voice is an interface.

It is not the core intelligence.

Core:

```text
Nārada runtime
```

Interface:

```text
STT
TTS
voice transport
```

---

# 72. Provider Rule for Voice

Sarvam, ElevenLabs, or other providers should remain behind:

```text
STTProvider
TTSProvider
```

---

# 73. Sandbox Rule

Autonomous code execution must be isolated.

Preferred:

```text
narada-core
 ↓
sandbox manager
 ↓
ephemeral Docker sandbox
```

---

# 74. Never Give Full Host Access

Do not mount:

```text
entire home directory
```

into autonomous sandboxes.

Mount only the required workspace.

---

# 75. Secret Isolation

Never expose:

```text
~/.ssh
~/.aws
browser profiles
password stores
Nārada .env
private keys
```

to generic sandboxes.

---

# 76. Docker Socket Rule

Treat:

```text
/var/run/docker.sock
```

as effectively privileged host access.

Do not give it to an autonomous agent casually.

---

# 77. Sandbox Limits

Use limits for:

```text
CPU
memory
runtime
processes
filesystem
network
```

---

# 78. Sandbox Lifecycle

```text
CREATE
 ↓
PREPARE
 ↓
EXECUTE
 ↓
COLLECT
 ↓
VERIFY
 ↓
DESTROY
```

---

# 79. Sandbox Stop Conditions

Stop sandbox execution if:

- timeout
- memory violation
- process violation
- policy violation
- unexpected privileged access
- secret access attempt
- approval revoked
- sandbox becomes unhealthy

---

# 80. Specialist Agent Rule

Specialists are workers under Nārada.

Nārada remains responsible for:

```text
goal
delegation
permissions
verification
final decision
```

A specialist does not become the system owner.

---

# 81. Specialist Output Rule

Specialists must return structured results:

```text
status
summary
evidence
artifacts
tests
warnings
recommended next action
```

---

# 82. OpenHands Rule

OpenHands or another coding specialist may perform coding work.

But:

```text
coding completed
```

does not mean:

```text
deployment authorized
```

or:

```text
merge authorized
```

Verification remains separate.

---

# 83. Browser Rule

Browser automation is not inherently safe.

Reading:

```text
public website
```

is different from:

```text
logging into account
sending message
purchasing
publishing
changing settings
```

Permissions must reflect this.

---

# 84. Research Rule

Never fabricate:

- source
- URL
- quote
- search result
- page visit
- evidence

If evidence is unavailable:

```text
say so
```

---

# 85. Verification Rule

The agent's claim is not evidence.

For example:

```text
LLM:
"Tests passed."
```

is not sufficient.

The runtime must actually have:

```text
test command result
```

---

# 86. Definition of Done

A task is done only when:

```text
implementation
+
tests
+
verification
+
documentation
+
logbook update
```

are complete.

For risky work:

```text
approval
+
audit
```

must also be complete.

---

# 87. Documentation Rule

When behavior changes, update documentation in the same phase.

Do not leave:

```text
code says X
docs say Y
```

---

# 88. API Compatibility

Avoid breaking public interfaces without:

- migration
- compatibility plan
- documentation
- tests

---

# 89. Database Migration Rule

Any schema change requires:

```text
migration
+
upgrade test
+
fresh install test
```

Never assume the database is empty.

---

# 90. Restart Test Rule

Every persistent feature must have a restart test.

At minimum:

```text
create
 ↓
restart
 ↓
retrieve
```

---

# 91. Crash Recovery Rule

Important operations must be recoverable after:

```text
process crash
container restart
machine restart
```

where practical.

---

# 92. Concurrency Rule

Assume:

```text
two events
```

may arrive simultaneously.

Protect:

- state transitions
- approvals
- side effects
- responsibility runs
- event deduplication

---

# 93. Duplicate Run Rule

A responsibility must not accidentally execute twice because of:

```text
scheduler restart
duplicate webhook
retry
race condition
```

Use execution IDs and appropriate locking/idempotency.

---

# 94. Cost Rule

Every autonomous process must have bounded cost.

Track:

```text
model calls
tokens
tool calls
runtime
API calls
sandbox time
```

where available.

---

# 95. Unattended Provider Rule

Persistent responsibilities should have explicit:

```text
provider
model
fallback policy
cost limit
```

Do not silently change providers for unattended work.

---

# 96. Model Privacy Rule

Model routing must respect:

```text
data sensitivity
user policy
provider policy
```

Private data must not be sent to remote providers if policy forbids it.

---

# 97. Provider Failure Rule

Provider failure must be explicit.

Never convert:

```text
provider failed
```

into:

```text
successful answer
```

---

# 98. Fallback Rule

Fallback providers may only be used when policy permits.

Example:

```text
remote provider unavailable
 ↓
fallback to Ollama
```

is valid only if configured.

---

# 99. Circuit Breaker Rule

Repeated provider failures should trigger bounded backoff/circuit-breaking.

Do not repeatedly hammer a failing API.

---

# 100. Security Boundary Rule

Treat every external boundary as untrusted:

```text
LLM
web
MCP server
webhook
email
Telegram
browser
sandbox
API
```

Validate input.

---

# 101. Prompt Injection Rule

External content may contain instructions.

Never treat webpage/email/document text as trusted system instructions.

Separate:

```text
instructions
```

from:

```text
untrusted content
```

The runtime's system/security policies always outrank content retrieved by tools.

---

# 102. MCP Security Rule

MCP provides capabilities.

It does not override Nārada permissions.

Flow:

```text
Nārada permission layer
 ↓
MCP client
 ↓
MCP server
```

not:

```text
MCP server
 ↓
unrestricted Nārada action
```

---

# 103. Webhook Rule

Verify:

- signature
- source
- timestamp
- replay protection
- event ID

before processing.

---

# 104. Attachment Rule

Treat uploaded files as untrusted content.

Before executing:

```text
code
scripts
macros
commands
```

inspect and isolate them.

---

# 105. Shell Rule

Shell execution is high risk.

Prefer:

```text
sandbox
```

over:

```text
host shell
```

Host shell access should be exceptional.

---

# 106. Filesystem Rule

Use explicit roots.

Example:

```text
allowed:
~/narada/workspaces/project-x
```

not:

```text
/
```

---

# 107. Path Validation

Prevent:

```text
../
symlink escapes
absolute-path bypass
```

when tools operate in restricted roots.

---

# 108. Network Rule

Sandbox network access should be explicitly controlled.

Possible policies:

```text
none
allowlist
restricted
full
```

Use the least privilege necessary.

---

# 109. Responsibility Permission Rule

A responsibility should declare its allowed capabilities.

Example:

```yaml
tools:
  - github.read
  - web.search
  - notification.send
```

Do not let it inherit every installed tool.

---

# 110. Skill Permission Rule

A skill should declare required tools.

The runtime still decides whether those tools are actually permitted.

---

# 111. Scheduled Job Isolation

Scheduled work should receive a bounded toolset and explicit model/provider policy.

It should not inherit arbitrary new capabilities merely because the system installed them later.

---

# 112. Fresh Session Rule

Autonomous scheduled runs should generally use:

```text
fresh session
+
responsibility state
+
relevant memory
+
current event
```

rather than endlessly growing conversation history.

---

# 113. Context Rule

Prioritize context:

```text
1. safety/permissions
2. current task
3. goal
4. responsibility
5. observations
6. relevant memory
7. history
```

Never sacrifice safety information to fit more conversation history.

---

# 114. Prompt Versioning Rule

Important prompts must be version-controlled.

Do not hide major system prompts inside arbitrary Python strings.

---

# 115. Prompt Change Rule

Changing a major prompt requires regression tests.

Prompt behavior is part of the system.

---

# 116. Autonomous Loop Rule

Every loop must have:

```text
entry condition
exit condition
iteration limit
failure behavior
```

No infinite loops.

---

# 117. No Busy Polling

Do not keep calling the LLM constantly just to see whether something happened.

Prefer:

```text
event
or
scheduled wakeup
```

---

# 118. Event-Driven Rule

Preferred autonomous pattern:

```text
EVENT
 ↓
SHOULD I CARE?
 ↓
NO → IGNORE / RECORD
YES
 ↓
WAKE
 ↓
ACT
 ↓
SLEEP
```

---

# 119. Notification Rule

Agent activity should not automatically become user notification.

First classify:

```text
silent
digest
important
urgent
approval
```

---

# 120. No Notification Spam

Batch related events.

Do not send:

```text
10 notifications
```

when:

```text
1 useful summary
```

is sufficient.

---

# 121. User Return Rule

Nārada must support:

```text
"What happened while I was away?"
```

using structured records.

Do not reconstruct solely from raw logs.

---

# 122. Daily Digest Rule

A digest should be generated from:

```text
events
responsibilities
runs
tasks
approvals
failures
```

not simply from conversation history.

---

# 123. Control Plane Rule

The UI is a control plane.

The UI must not contain the core authorization logic.

Authorization belongs in the backend runtime.

---

# 124. CLI Rule

CLI commands should call the same underlying APIs/services as other interfaces.

Do not duplicate business logic.

---

# 125. API Rule

FastAPI is an interface layer.

Do not place core agent business logic directly in route handlers.

---

# 126. Dependency Rule

Every dependency must answer:

```text
Why do we need it?
Why this one?
Can an existing component do it?
What does it cost?
What operational burden does it add?
Can it be removed later?
```

---

# 127. Lego Rule

Prefer mature existing components for:

```text
LLM
STT
TTS
agent orchestration
MCP
browser
coding
vector storage
scheduling
queues
```

Nārada should own the glue:

```text
identity
responsibility
permissions
orchestration
memory policy
approval
audit
provider routing
event routing
```

---

# 128. Do Not Rebuild Mature Infrastructure

Before writing a subsystem, search the existing ecosystem.

Ask:

```text
Is this already solved?
Is it mature?
Does it fit our interfaces?
Can we wrap it?
```

Build custom only when the project's actual differentiation requires it.

---

# 129. Avoid Framework Sprawl

Do not add:

```text
LangGraph
+ another agent framework
+ another workflow engine
+ another queue
+ another scheduler
```

without a concrete reason.

---

# 130. Current Preferred Local Stack

Default preference:

```text
Python
FastAPI
Docker Compose
SQLite
Sarvam
Ollama
MCP
Playwright
LangGraph when stateful graph behavior is justified
OpenHands for coding
APScheduler or equivalent local scheduler
Qdrant only when justified
Redis only when justified
```

---

# 131. Local-First Rule

The core system must work locally without AWS.

AWS must remain optional until the cloud phase.

---

# 132. Hybrid Rule

Hybrid mode should connect:

```text
cloud control plane
```

to:

```text
local execution
```

without exposing local infrastructure directly to the public internet.

---

# 133. AWS Rule

Do not introduce:

```text
Kubernetes
EKS
NAT Gateway
GPU instances
Elasticache
OpenSearch
```

unless a demonstrated requirement justifies them.

---

# 134. Cloud Cost Rule

Every AWS component must have:

```text
reason
cost estimate
alternative
shutdown strategy
```

---

# 135. Cloud Parity Rule

The same conceptual Nārada runtime should work in:

```text
local
hybrid
cloud
```

Do not create three unrelated implementations.

---

# 136. Environment Rule

Configuration should distinguish:

```text
local
hybrid
cloud
test
```

without changing core business logic.

---

# 137. Test Environment Rule

Tests must not accidentally use production:

```text
database
API keys
Telegram channel
GitHub repository
email
```

Use isolated configuration.

---

# 138. Destructive Test Rule

Destructive tests must use:

```text
fake resources
test accounts
isolated sandboxes
```

Never production data.

---

# 139. Real User Communication Tests

When testing Telegram/email/SMS:

- use dedicated test destinations
- clearly mark test messages
- never accidentally message unrelated contacts

---

# 140. Data Retention Rule

Define retention for:

```text
events
audit logs
messages
tool outputs
sandbox artifacts
memories
```

Do not retain everything forever by accident.

---

# 141. Privacy Rule

Collect the minimum data required.

Do not store:

```text
credentials
unnecessary personal data
raw secrets
```

in ordinary memory.

---

# 142. Memory Security Rule

Memory retrieval must respect:

```text
user
workspace
responsibility
permission
```

A tool or specialist should not automatically receive every memory.

---

# 143. Multi-User Future Rule

Even if Nārada begins single-user, design IDs explicitly:

```text
user_id
workspace_id
session_id
responsibility_id
task_id
run_id
```

Do not assume one global anonymous user forever.

---

# 144. Workspace Rule

Future multi-project support should isolate:

```text
files
memory
responsibilities
credentials
tools
```

by workspace where appropriate.

---

# 145. Credential Scope Rule

Use credentials with the narrowest possible scope.

Prefer:

```text
repo-specific token
```

over:

```text
all-GitHub-admin token
```

---

# 146. Secrets Never Enter Memory

Do not store API keys or passwords as ordinary memories.

If credentials must be referenced:

```text
secret manager/configuration
```

not:

```text
semantic memory
```

---

# 147. Error Handling Rule

Errors should be classified.

At minimum:

```text
TRANSIENT
PERMANENT
AUTH
PERMISSION
APPROVAL
VALIDATION
PROVIDER
EXTERNAL
SANDBOX
INTERNAL
UNKNOWN
```

---

# 148. User-Facing Errors

Do not expose raw internal stack traces to users by default.

Provide:

```text
what happened
what Nārada did
what is blocked
what the user can do
```

Keep detailed trace in logs.

---

# 149. Internal Error Rule

Every important error must have:

```text
timestamp
run_id
task_id
responsibility_id if applicable
component
error type
message
stack trace internally
```

---

# 150. Retry Rule

Retries must be:

```text
bounded
classified
backoff-aware
idempotency-aware
audited
```

---

# 151. Backoff Rule

Use increasing delay for transient provider/network failures.

Do not hammer services.

---

# 152. Failure Recovery Rule

After repeated failures:

```text
STOP
 ↓
PERSIST
 ↓
NOTIFY / QUEUE
```

Do not endlessly retry.

---

# 153. Dead Letter Rule

Tasks that exceed retry limits move to:

```text
FAILED
```

or:

```text
BLOCKED
```

and require explicit recovery.

---

# 154. Recovery Must Be Explainable

Nārada should be able to answer:

```text
Why did this task fail?
What did you retry?
Why did you stop?
```

This requires structured execution history.

---

# 155. Observability Rule

Nārada must expose enough state to debug autonomous behavior.

At minimum:

```text
health
runs
tasks
responsibilities
events
approvals
tool calls
provider calls
failures
```

---

# 156. Run IDs

Every execution gets:

```text
run_id
```

Child work should preserve lineage:

```text
parent_run_id
```

---

# 157. Trace Rule

A user-facing activity should be traceable:

```text
message
 ↓
run
 ↓
task
 ↓
tool
 ↓
result
 ↓
notification
```

---

# 158. Cost Observability

Where provider data allows, record:

```text
model
tokens
duration
estimated cost
```

---

# 159. Resource Budget Rule

Responsibilities may eventually specify:

```text
max_runtime
max_model_calls
max_tool_calls
max_cost
max_retries
```

Exceeding a budget must stop or pause the work.

---

# 160. Phase Transition Rule

A phase can transition only after:

```text
exit criteria = PASS
```

and:

```text
logbook summary = appended
```

---

# 161. Phase Transition Checklist

Before moving on:

```text
[ ] implementation complete
[ ] unit tests pass
[ ] integration tests pass
[ ] security checks pass
[ ] restart test passes where applicable
[ ] documentation updated
[ ] errors recorded
[ ] fixes recorded
[ ] unresolved issues recorded
[ ] exit criteria checked
[ ] logbook summary appended
[ ] phase marked COMPLETE
```

---

# 162. Next Phase Initialization

At the beginning of a new phase:

1. Create a new logbook.
2. Copy in the phase objective.
3. Copy in exit criteria.
4. Record dependencies on previous phases.
5. Record known issues inherited from previous phase.
6. Mark status `IN_PROGRESS`.

Never continue using the previous phase's logbook.

---

# 163. Phase Logbook Chain

Maintain a visible chain:

```text
Phase 00
   ↓
summary
   ↓
Phase 01
   ↓
summary
   ↓
Phase 02
   ↓
summary
   ↓
...
```

This creates a historical implementation trail.

---

# 164. Decision Record Rule

Major architecture decisions should also be recorded in:

```text
docs/decisions/
```

Example:

```text
ADR-001-core-container.md
ADR-002-sqlite-default.md
ADR-003-provider-abstraction.md
```

The phase logbook should reference important decisions.

---

# 165. Do Not Over-Document Triviality

Documentation should explain:

```text
why
what
how
constraints
verification
```

Do not create enormous prose for a one-line obvious change.

---

# 166. AI Agent Working Protocol

Every AI coding agent must follow:

```text
READ
 ↓
UNDERSTAND
 ↓
PLAN
 ↓
LOG
 ↓
IMPLEMENT
 ↓
TEST
 ↓
VERIFY
 ↓
LOG
 ↓
REVIEW
 ↓
SUMMARY
```

---

# 167. AI Agent Must Not Pretend

Never claim:

```text
implemented
tested
verified
deployed
sent
remembered
```

unless it actually happened.

---

# 168. AI Agent Must Report Limitations

If something could not be tested:

```text
say exactly why
```

Example:

```text
Live Sarvam verification was not performed because no API credential
was available. Unit tests use FakeLLMProvider.
```

---

# 169. AI Agent Must Not Hide Warnings

If a workaround is needed:

```text
record it
```

Do not silently downgrade behavior.

---

# 170. AI Agent Stop Rule

Stop and ask for clarification when:

- two requirements conflict
- security implications are unclear
- external side effect is ambiguous
- data deletion scope is unclear
- production impact is unclear
- a required credential is missing for an action that cannot be safely mocked
- an architectural boundary must be broken

---

# 171. AI Agent Continue Rule

The agent may continue without asking when:

- behavior is clearly specified
- action is local and reversible
- tests exist
- permissions are satisfied
- no consequential side effect is involved

---

# 172. Do Not Ask Needless Questions

Do not interrupt for trivial choices that can safely follow established conventions.

Use:

```text
existing architecture
existing style
phase specification
```

as defaults.

Ask when the choice affects:

```text
security
data loss
cost
external side effects
architecture
user intent
```

---

# 173. Test Failure Rule

A failing test is information.

Do not simply delete or weaken the test to make the suite green.

First determine:

```text
implementation bug?
test bug?
specification bug?
environment problem?
```

Then document.

---

# 174. Flaky Test Rule

Do not ignore flaky tests.

Record:

```text
frequency
cause
environment
workaround
planned fix
```

---

# 175. No False Green Rule

Never:

```text
skip
mock
disable
weaken
```

a test merely to make CI pass unless the reason is explicit and documented.

---

# 176. Integration Test Rule

Integration tests should verify boundaries:

```text
core ↔ provider
core ↔ SQLite
core ↔ MCP
core ↔ sandbox
core ↔ channel
scheduler ↔ responsibility
event ↔ responsibility
```

---

# 177. End-to-End Test Rule

At least one end-to-end scenario must represent the actual user journey for each major capability.

---

# 178. Regression Rule

Every important bug should result in:

```text
bug
 ↓
fix
 ↓
regression test
 ↓
logbook entry
```

---

# 179. Bug Memory Rule

The phase logbook should preserve recurring failure patterns.

If the same class of bug occurs repeatedly, promote the lesson into:

```text
AGENTS.md
```

or:

```text
MASTER RULES
```

as appropriate.

---

# 180. Dependency Update Rule

Do not blindly upgrade dependencies.

Before upgrading:

```text
check compatibility
run tests
check security
record changes
```

---

# 181. Version Pinning

Production/reproducible environments should pin dependencies appropriately.

Avoid unconstrained:

```text
latest
```

for critical infrastructure.

---

# 182. Docker Image Rule

Prefer reproducible images.

Document:

```text
base image
Python version
system dependencies
```

---

# 183. Container Security

Prefer:

```text
non-root
read-only filesystem where practical
minimal packages
explicit mounts
resource limits
```

---

# 184. Health Checks

Every persistent service should have a meaningful health check.

Health must represent actual ability to perform its responsibility.

---

# 185. Graceful Shutdown

The core should handle shutdown:

```text
stop accepting new work
finish/cancel according to policy
persist state
release resources
exit
```

---

# 186. Scheduler Shutdown

Do not trigger new jobs during shutdown.

Persist job state.

---

# 187. Worker Shutdown

Workers must either:

```text
finish safe work
```

or:

```text
cancel and persist checkpoint
```

according to policy.

---

# 188. External Action Before Shutdown

If a consequential action is in progress, reconcile its state after restart.

Never assume:

```text
process stopped
=
external action failed
```

---

# 189. Database Rule

Use transactions for related state updates.

Example:

```text
event processed
+
responsibility updated
+
run recorded
```

should not leave contradictory partial state when atomicity is required.

---

# 190. Migration Rule

Database migrations must be:

```text
versioned
repeatable
tested
reversible where practical
```

---

# 191. Backup Rule

Persistent user data should eventually support:

```text
backup
restore
export
```

Do not wait until after data loss to design this.

---

# 192. Export Rule

The user should eventually be able to export:

```text
memory
responsibilities
tasks
audit
configuration metadata
```

without exposing secrets.

---

# 193. Restore Test

A backup is not real until restore has been tested.

---

# 194. Data Integrity Rule

After restart/restore verify:

```text
foreign keys
IDs
timestamps
responsibility state
pending approvals
event identity
```

---

# 195. Time Rule

Store timestamps consistently.

Prefer timezone-aware timestamps.

Do not assume:

```text
UTC = user's local time
```

for user-facing schedules.

---

# 196. Scheduler Timezone Rule

Every recurring responsibility should have an explicit timezone or inherit a clearly defined user timezone.

---

# 197. Daylight Saving Rule

If relevant to the deployment timezone, test recurring schedules around DST transitions.

---

# 198. Clock Testing Rule

Use fake clocks for deterministic scheduler tests.

Never make the unit test wait for real time.

---

# 199. Responsibility State Machine

State transitions must be explicit.

Example:

```text
DRAFT
 ↓
ACTIVE
 ↓
PAUSED
 ↓
ACTIVE
 ↓
COMPLETED
```

Errors may produce:

```text
ERROR
 ↓
RECOVERY
 ↓
ACTIVE
```

---

# 200. Invalid State Transitions

Do not permit arbitrary state changes.

For example:

```text
COMPLETED → ACTIVE
```

must require an explicit reopen/restart operation if supported.

---

# 201. Task State

Task state should be explicit:

```text
PENDING
RUNNING
WAITING
BLOCKED
FAILED
COMPLETED
CANCELLED
```

---

# 202. Approval State

Approval state:

```text
PENDING
APPROVED
DENIED
EXPIRED
CANCELLED
```

---

# 203. Event State

Events may track:

```text
RECEIVED
PERSISTED
MATCHED
PROCESSED
IGNORED
FAILED
```

---

# 204. No Hidden State

Important state must exist in structured storage.

Do not rely solely on:

```text
prompt text
```

or:

```text
LLM memory
```

for system state.

---

# 205. Responsibility Creation Rule

When user gives a long-term instruction, determine whether it is:

```text
question
one-time task
responsibility
```

Do not turn every question into a persistent job.

---

# 206. Responsibility Confirmation

If a request clearly implies ongoing monitoring, create a responsibility only when required by the product flow.

Do not create persistent work from ambiguous casual conversation.

---

# 207. Responsibility Scope

A responsibility should define:

```text
what
why
when
how
allowed tools
permissions
delivery
budget
```

---

# 208. Responsibility Completion

A responsibility must have a completion or stop condition when possible.

Avoid:

```text
forever
```

without a clear reason.

---

# 209. Responsibility Pause

Pause must prevent new work while preserving:

```text
state
history
memory
configuration
```

---

# 210. Responsibility Delete

Deletion must clearly distinguish:

```text
stop future execution
```

from:

```text
delete historical data
```

---

# 211. Event Relevance Rule

An event being related to a responsibility does not automatically mean it is important.

Evaluate:

```text
relevance
change
importance
urgency
required action
```

---

# 212. No-Op Runs

No-op runs are valid.

Example:

```text
checked repository
nothing changed
```

should be recorded without notifying the user.

---

# 213. Meaningful Change

"Meaningful" must eventually be represented by explicit policy or model evaluation with evidence.

Do not invent importance after the fact.

---

# 214. Notification Escalation

If an important event remains unacknowledged and policy requires escalation:

```text
first channel
 ↓
wait
 ↓
second channel
```

Only if explicitly configured.

---

# 215. No Intrusive Monitoring

Do not create monitoring that is:

- unnecessary
- invasive
- excessive
- unrelated to the user's responsibility

Respect privacy.

---

# 216. Communication Consent

Nārada must know which channels it may use.

Example:

```yaml
notifications:
  telegram: allowed
  email: allowed
  phone: approval_required
```

---

# 217. Contact Scope

Do not let Nārada message arbitrary people simply because it has a contact tool.

Recipient scope must be controlled.

---

# 218. Publishing Rule

Publishing to public destinations is consequential.

Treat:

```text
tweet
post
release
public document
public comment
```

as high-risk actions unless explicitly authorized.

---

# 219. Git Rule

Git operations differ by risk:

```text
git.status       low
git.diff         low
git.branch       low/medium
git.commit       medium
git.push         high
release          high/critical
```

Policy decides final classification.

---

# 220. GitHub Phase Branch Rule

Every implementation phase MUST have its own dedicated Git branch.

Example:

```text
phase/01-foundation
phase/02-config
phase/03-llm-provider
...
```

A later phase MAY modify code introduced by an earlier phase when the current phase requires the change. The modification belongs to the current phase branch and MUST be recorded in that phase logbook with its origin, reason, impact, and verification.

A later phase MUST NOT use this freedom as permission for unrelated refactoring.

---

# 221. GitHub Phase Completion Rule

A phase is not complete merely because its code works locally. Before merge, the phase MUST complete:

```text
implementation
 ↓
tests
 ↓
fix + retest
 ↓
exit criteria
 ↓
logbook update
 ↓
project status / roadmap update
 ↓
affected documentation update
 ↓
pre-merge checks
 ↓
PR review
 ↓
explicit merge authorization
 ↓
merge
 ↓
post-merge verification
```

The phase logbook MUST record the branch, important commits, cross-phase changes, PR, review state, merge commit, and post-merge verification.

---

# 222. GitHub Pre-Merge Gate

Before merging a phase branch, verify:

- [ ] phase objective is satisfied
- [ ] all exit criteria pass
- [ ] relevant tests pass
- [ ] regression tests pass
- [ ] security/permission checks pass where applicable
- [ ] restart/recovery checks pass where applicable
- [ ] no secrets are present
- [ ] diff contains no unexplained changes
- [ ] cross-phase changes are documented
- [ ] phase logbook is complete
- [ ] completion summary is appended
- [ ] project status/roadmap is updated
- [ ] affected documentation is updated
- [ ] PR description is complete
- [ ] required review is complete
- [ ] CI is green
- [ ] no blocking review comments remain
- [ ] merge is explicitly authorized

A green CI run is NOT equivalent to merge authorization.

---

# 223. Post-Success Documentation Update Rule

After every successfully verified phase, but before merge, update all project files whose truth changed. At minimum, evaluate:

```text
phase logbook
project status / roadmap
architecture/design documentation
README/setup/API/config documentation
changelog/release notes when applicable
verification evidence when applicable
```

Do not create meaningless documentation changes just to satisfy the checklist. If a category does not require an update, record that determination in the phase logbook.

---

# 220. Deployment Rule

Deployment should generally be:

```text
prepare
 ↓
test
 ↓
verify
 ↓
approval
 ↓
deploy
 ↓
verify deployment
```

---

# 221. Financial Rule

Financial actions require explicit authorization and appropriate confirmation.

Do not allow autonomous spending merely because an API exists.

---

# 222. Account Change Rule

Changes to:

```text
password
MFA
security settings
billing
permissions
```

are high-risk.

---

# 223. Delete Rule

Deletion must be:

```text
explicit
scoped
audited
recoverable where practical
```

---

# 224. Human-in-the-Loop Rule

Human approval should be used where:

```text
risk
irreversibility
cost
external impact
```

justify it.

Do not require approval for every harmless read.

---

# 225. Avoid Approval Fatigue

If everything requires approval:

```text
user stops paying attention
```

Use risk-based approval.

---

# 226. Approval UX Rule

Approval requests should be concise but sufficient.

Include:

```text
what
where
why
risk
effect
expiry
```

---

# 227. Human Override

The user must be able to:

```text
pause
cancel
disable
revoke approval
```

---

# 228. Emergency Stop

Provide a global stop mechanism.

It should prevent new autonomous actions.

Ideally:

```text
POST /control/emergency-stop
```

or equivalent.

The emergency stop must be enforced in runtime, not just UI.

---

# 229. Emergency Stop Persistence

If emergency stop is active:

```text
restart
```

must not silently re-enable autonomous work.

---

# 230. Recovery From Emergency Stop

Requires explicit user action.

---

# 231. Skill Safety

A skill cannot grant itself additional permissions.

Required tools must still pass the permission engine.

---

# 232. MCP Skill Safety

Installing an MCP server does not automatically authorize all its tools.

---

# 233. Plugin Safety

Plugins/providers must declare:

```text
capabilities
permissions
side effects
credentials
```

---

# 234. External Service Rule

Do not assume external APIs are reliable.

Handle:

```text
timeout
rate limit
auth failure
schema changes
outage
partial response
```

---

# 235. API Schema Rule

Validate external responses before using them for consequential decisions.

---

# 236. Versioned Provider Adapters

Provider adapters should isolate vendor API changes from core.

---

# 237. Sarvam Rule

Sarvam-specific code stays in:

```text
providers/
```

Never spread Sarvam assumptions throughout Nārada.

---

# 238. Ollama Rule

Ollama-specific connection logic stays in its provider adapter.

The agent should not know whether the model is local.

---

# 239. TTS/STT Rule

Voice providers remain replaceable.

Examples:

```text
Saaras
Bulbul
ElevenLabs
other provider
```

should implement common interfaces.

---

# 240. Voice Failure Rule

If TTS fails:

```text
do not assume the response was delivered
```

Record delivery failure.

---

# 241. Channel Delivery Rule

Sending a message and the user receiving it are different states.

Track:

```text
queued
sent
delivered where available
failed
```

---

# 242. Notification Retry Rule

Retry only according to channel/provider semantics.

Avoid duplicate sends.

---

# 243. Attachment Rule

Attachments need:

```text
type
size
source
permissions
retention
```

---

# 244. Browser Session Rule

Browser sessions should not expose arbitrary saved user credentials to autonomous agents.

Use isolated profiles where possible.

---

# 245. Browser Action Risk

Reading:

```text
public web
```

is not equivalent to:

```text
authenticated action
```

---

# 246. Browser Verification

After browser actions, verify the resulting state.

Do not assume a click succeeded.

---

# 247. Coding Workspace Rule

Every coding task gets an explicit workspace.

Example:

```text
/workspaces/task-123
```

---

# 248. Coding Diff Rule

Before accepting delegated code:

```text
inspect diff
run tests
inspect unexpected files
inspect dependency changes
```

---

# 249. Specialist Boundary

A specialist should not:

```text
change parent responsibility
grant itself tools
message user independently
modify global policy
```

unless explicitly authorized.

---

# 250. Parent-Child Task Rule

Child tasks must reference:

```text
parent_run_id
parent_task_id
```

where applicable.

---

# 251. Specialist Failure Rule

A specialist failure becomes a structured result.

Do not hide it from the parent agent.

---

# 252. Verification Specialist

For high-risk work, verification should be separate from generation where practical.

Example:

```text
coder
 ↓
verifier
```

not:

```text
coder says "looks good"
```

---

# 253. No Self-Certification

An agent should not be the sole verifier of its own consequential action.

---

# 254. Research Verification

Important research should retain:

```text
source
timestamp
claim
evidence
```

---

# 255. Freshness Rule

For time-sensitive information, record when it was checked.

Do not present stale information as current.

---

# 256. User Query vs Responsibility Rule

A user can ask:

```text
"What happened?"
```

without changing the responsibility.

Do not accidentally mutate persistent state from informational queries.

---

# 257. User Intent Rule

When an instruction could mean either:

```text
one-time
```

or:

```text
persistent
```

resolve before creating a long-running responsibility if the distinction materially affects behavior.

---

# 258. No Surprise Persistence

Do not silently create recurring jobs from ordinary conversation.

---

# 259. No Surprise External Action

Do not turn:

```text
"prepare this"
```

into:

```text
"publish this"
```

---

# 260. No Surprise Cost

Do not silently move from:

```text
local model
```

to:

```text
paid API
```

without policy.

---

# 261. No Surprise Communication

Do not contact:

```text
third parties
```

without authorization.

---

# 262. No Surprise Data Collection

Do not begin monitoring unrelated sources merely because they might be useful.

---

# 263. Project Scope Rule

Nārada should stay focused on the user's declared responsibility.

Do not broaden tasks unnecessarily.

---

# 264. Goal Completion Rule

Once the goal is demonstrably complete:

```text
stop
```

Do not create additional work merely to keep the agent busy.

---

# 265. Agentic Restraint

An autonomous agent should optimize for:

```text
useful progress
```

not:

```text
maximum activity
```

---

# 266. Silence Is Sometimes Success

If a responsibility says:

```text
notify only if important
```

then:

```text
no notification
```

can be the correct result.

---

# 267. No-Op Is Not Failure

A successful check with no meaningful change is:

```text
SUCCESS / NO_OP
```

not:

```text
FAILED
```

---

# 268. Waiting Is a State

If work depends on:

```text
approval
external event
deadline
provider recovery
```

use:

```text
WAITING
```

rather than repeatedly running.

---

# 269. Polling Rule

Use polling only when:

```text
no event mechanism exists
```

and define:

```text
frequency
cost
stop condition
```

---

# 270. Event Preference

Prefer:

```text
webhook
push
notification
```

over frequent polling when reliable.

---

# 271. Background Work Rule

Background work must be observable.

The user should be able to discover:

```text
what is running
```

---

# 272. Worker Concurrency

Do not increase concurrency until:

```text
state locking
budgeting
provider limits
```

are understood.

---

# 273. Rate Limit Rule

Respect external provider rate limits.

Use:

```text
backoff
batching
caching where appropriate
```

---

# 274. Caching Rule

Cache only where:

```text
staleness is acceptable
```

and define invalidation behavior.

---

# 275. External State Rule

Never treat local cache as authoritative when the external system is authoritative.

---

# 276. Reconciliation Rule

When uncertain after a failed external mutation:

```text
query external state
```

before retrying.

---

# 277. Idempotent Responsibility Rule

Where possible, a responsibility run should be safe to repeat.

---

# 278. Checkpoint Rule

Long-running tasks should checkpoint progress.

Checkpoint:

```text
after meaningful milestones
```

not only at the very end.

---

# 279. Resume Rule

A resumed task should know:

```text
what completed
what did not
what may have side effects
```

---

# 280. State Reconciliation

After restart:

```text
load checkpoint
 ↓
reconcile external state if needed
 ↓
resume
```

---

# 281. Memory Retrieval Rule

Retrieve memory because it is relevant, not because it exists.

---

# 282. Memory Importance

A memory should have a reason to persist.

Possible signals:

```text
user explicitly asked to remember
repeated relevance
long-term preference
important decision
project fact
```

---

# 283. Memory Source

Record where a memory came from when practical:

```text
conversation
document
tool
user
system
```

---

# 284. Memory Confidence

For inferred memories, record uncertainty.

Do not treat model inference as user-confirmed fact.

---

# 285. User-Correctable Memory

Users must eventually be able to correct important memory.

---

# 286. Memory Deletion

Deletion must actually remove or appropriately invalidate the underlying stored data according to retention policy.

---

# 287. Semantic Search Rule

Vector similarity does not equal truth.

Retrieved memory must still be interpreted in context.

---

# 288. Contradiction Rule

When memories conflict:

```text
detect
record
resolve
```

Do not silently overwrite important historical information.

---

# 289. Logbook and Memory Are Different

The logbook records:

```text
engineering process
```

Memory records:

```text
agent/user/project knowledge
```

Do not confuse them.

---

# 290. Logbook Must Not Become Agent Memory

Engineering logs belong in project documentation.

They should not automatically be injected into the agent's runtime context.

---

# 291. Phase Summary Must Be Appended

This is mandatory.

At phase completion:

```text
working log
 ↓
review
 ↓
summary
 ↓
APPEND TO SAME FILE
 ↓
mark COMPLETE
```

Do not create a separate summary that replaces the logbook.

---

# 292. Next Phase Gets Fresh Logbook

Immediately after closing:

```text
phase-01-logbook.md
```

create:

```text
phase-02-logbook.md
```

with its own objective and exit criteria.

---

# 293. Logbook Summary Must Mention Errors

Even if all errors were fixed, include:

```text
errors encountered
cause
fix
verification
```

This creates institutional memory.

---

# 294. Logbook Summary Must Mention Deviations

If implementation differed from plan:

```text
what changed
why
impact
```

must be recorded.

---

# 295. Logbook Summary Must Mention Tests

Include:

```text
test count
pass/fail
important scenarios
known limitations
```

---

# 296. Logbook Summary Must Mention Next Phase Readiness

Explicitly state:

```text
READY
```

or:

```text
BLOCKED
```

---

# 297. Phase Cannot Be "Almost Complete"

Allowed statuses:

```text
NOT_STARTED
IN_PROGRESS
BLOCKED
COMPLETE
```

Avoid vague:

```text
almost done
mostly done
probably works
```

---

# 298. Blocked Phase Rule

If blocked:

```text
status = BLOCKED
```

and document:

```text
blocker
impact
what is needed
```

Do not silently jump ahead if the blocked phase is a dependency.

---

# 299. Exception Rule

If an explicit user decision overrides a rule:

Record:

```text
user decision
date
scope
impact
```

Do not generalize a one-off exception into a permanent rule unless instructed.

---

# 300. Final Rule

Everything in Nārada should move toward one property:

> **Nārada should be able to take responsibility for useful work, continue that work while the user is away, act only within its authority, recover honestly from failure, remember what matters, and explain what it did.**

The implementation process must embody the same discipline.

Therefore:

```text
PLAN
 ↓
BUILD
 ↓
TEST
 ↓
VERIFY
 ↓
LOG
 ↓
FIX
 ↓
VERIFY AGAIN
 ↓
SUMMARIZE
 ↓
CLOSE PHASE
 ↓
START NEW LOGBOOK
 ↓
NEXT PHASE
```

And the most important operational rule remains:

> **Never move to the next phase without closing the current phase's logbook and appending its completion summary.**
