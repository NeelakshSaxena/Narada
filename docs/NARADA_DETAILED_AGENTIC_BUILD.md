# NĀRADA — Detailed Agentic Runtime Build Specification

> **Purpose:** This document is the implementation-grade blueprint for building Nārada as a local-first, persistent, autonomous personal agent runtime.
>
> **Core idea:** Give Nārada a responsibility, and it figures out how to keep that responsibility moving.
>
> **Working motto:** Don't build the bricks. Build the temple.

---


# GitHub / Phase Branch Integration Rules

Every implementation phase in this build plan runs on its own dedicated branch.

```text
main
  ↓
phase/01-foundation
  ↓ merge
main
  ↓
phase/02-config
  ↓ merge
main
  ↓
phase/03-llm-provider
```

A later phase is explicitly allowed to change code from an earlier phase when integration, correctness, security, or the current phase's requirements demand it. The change stays on the later phase branch and is recorded as a cross-phase change in that phase's logbook. Unrelated cleanup remains out of scope.

After a phase passes all technical exit criteria, the agent MUST update the phase logbook, project status/roadmap, and every affected architecture/setup/API/configuration document before opening or finalizing the PR. The PR cannot be merged until the pre-merge checklist passes, required review is complete, CI is green, and merge is explicitly authorized. After merge, the integration branch is smoke-tested and the merge commit is recorded in the phase logbook before the next phase branch is created.

See `NARADA_GITHUB_RULES.md` for the complete Git/GitHub policy.


# 0. How to Read This Document

This is not a high-level product description.

It is a **phased build specification** for an AI coding agent and human developer.

Every phase defines:

- objective
- architecture
- components
- agentic prompts
- expected behavior
- verification conditions
- automated tests
- failure conditions
- stop conditions
- security requirements
- persistence requirements
- observability requirements
- exit criteria
- what must **not** be built yet

The implementation strategy is intentionally conservative:

```text
ONE CORE CONTAINER
        │
        ├── API
        ├── Agent Runtime
        ├── Worker
        ├── Scheduler
        ├── Memory
        ├── Tool Registry
        ├── Event Dispatcher
        └── Gateway
                │
                ├── External APIs
                │     ├── Sarvam
                │     ├── ElevenLabs
                │     ├── OpenAI-compatible APIs
                │     ├── GitHub
                │     └── Email/Telegram/etc.
                │
                ├── Local model services
                │     └── Ollama
                │
                ├── Optional infrastructure containers
                │     └── Qdrant
                │
                └── Ephemeral sandboxes
                      ├── coding
                      ├── browser
                      ├── shell
                      └── specialist agents
```

The goal is **not** to create a Kubernetes-like platform on day one.

The goal is:

> **One reliable local runtime that can stay alive while the user is away.**

---

# 1. Architecture Decision: What Runs Where

## 1.1 Core principle

Nārada should have a single primary container for the backend runtime.

Call it:

```text
narada-core
```

It contains:

```text
FastAPI
Agent runtime
Worker
Scheduler
Event dispatcher
Memory manager
SQLite
Tool registry
Permission engine
Approval engine
Channel gateway
Provider routing
MCP client
Audit logger
```

This keeps local installation simple.

---

## 1.2 Things that do NOT need their own container

Do not containerize external APIs.

Examples:

```text
Sarvam API
ElevenLabs API
OpenAI API
Anthropic API
Gemini API
GitHub API
Telegram API
Twilio API
Google APIs
Notion API
Slack API
```

Nārada calls these through HTTP/SDK adapters.

Conceptually:

```text
narada-core
      │
      ├── HTTPS → Sarvam
      ├── HTTPS → ElevenLabs
      ├── HTTPS → GitHub
      ├── HTTPS → Telegram
      └── HTTPS → other APIs
```

This avoids unnecessary containers and mirrors the project's provider-agnostic architecture.

---

## 1.3 Ollama

Ollama is a local model runtime.

It does not need to be inside the Nārada container.

Preferred local arrangement:

```text
Docker
┌───────────────────────────────┐
│ narada-core                   │
│                               │
│ Agent + API + Worker + Memory │
└───────────────┬───────────────┘
                │
                │ HTTP
                ▼
          Ollama on host
                │
                ▼
             GPU/model
```

On Linux this can be:

```text
http://host.docker.internal:11434
```

or an equivalent host-network configuration.

On Windows/WSL2, use the Docker Desktop/WSL networking mechanism appropriate to the installation.

The exact networking setup must be verified during implementation.

---

## 1.4 SQLite

SQLite should normally **not** be a separate container.

SQLite is a file.

Use:

```text
./data/narada.db
```

mounted into:

```text
narada-core:/data/narada.db
```

Conceptually:

```text
Host
└── data/
    └── narada.db
          ↑
          │ volume
          │
    narada-core
```

SQLite should be the default database in BASE/V1/V2 unless concurrency requirements demonstrate the need for PostgreSQL.

---

## 1.5 Qdrant

Qdrant is optional.

Do not introduce it until semantic/vector memory is actually useful.

If needed:

```text
narada-core
      │
      │ HTTP
      ▼
qdrant
```

Docker Compose:

```text
services:
  narada:
    ...
  qdrant:
    ...
```

Qdrant should be considered infrastructure, not part of the agent's core identity.

If SQLite + FTS is sufficient, do not run Qdrant.

---

## 1.6 Redis

Redis is optional and should not be mandatory in BASE.

Initially:

```text
Python asyncio
+
SQLite
+
in-process scheduler/event dispatcher
```

can be sufficient.

Introduce Redis when:

- background work needs a separate queue
- event delivery must survive process boundaries
- multiple worker processes are required
- local autonomous workloads become concurrent enough to justify it

Then:

```text
narada-core
      │
      ▼
    redis
```

Do not run Redis merely because the architecture diagram contains it.

---

# 2. Target Local Docker Architecture

The preferred local deployment is:

```text
                         USER
                           │
               ┌───────────┴───────────┐
               │                       │
             Browser                Phone
               │                       │
               └───────────┬───────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   NĀRADA CORE   │
                  │   Docker        │
                  │                 │
                  │ FastAPI         │
                  │ Gateway         │
                  │ Agent           │
                  │ Worker          │
                  │ Scheduler       │
                  │ Memory          │
                  │ Tools           │
                  │ Permissions     │
                  │ Approvals       │
                  │ Audit           │
                  │ SQLite          │
                  └───────┬─────────┘
                          │
          ┌───────────────┼─────────────────┐
          │               │                 │
          ▼               ▼                 ▼
       Ollama          Qdrant          External APIs
       optional        optional         ├── Sarvam
                                         ├── ElevenLabs
                                         ├── GitHub
                                         ├── Telegram
                                         ├── Email
                                         ├── Calendar
                                         └── etc.
```

---

# 3. The "Away Mode" Requirement

A major requirement is that Nārada must continue working while the user is away.

This changes the architecture.

A normal chatbot assumes:

```text
User present
   ↓
Message
   ↓
Answer
```

Nārada must support:

```text
User leaves
   ↓
Nārada remains alive
   ↓
Event occurs
   ↓
Nārada wakes
   ↓
Checks responsibility
   ↓
Plans
   ↓
Acts
   ↓
Observes
   ↓
Updates memory
   ↓
Decides
   ↓
Sleeps
   ↓
Notifies user if necessary
```

The runtime therefore needs:

```text
Gateway
Scheduler
Event system
Persistent state
Persistent responsibilities
Notification channels
Failure recovery
Audit trail
```

---

# 4. Hermes-Inspired Architectural Lessons

The goal is not to clone Hermes.

The useful architectural pattern is to treat the agent as a **persistent gateway/runtime** rather than a chat loop.

Current Hermes documentation describes a system with:

- a gateway
- scheduled jobs
- persistent/isolated execution environments
- multiple communication platforms
- skills
- MCP
- subagents
- tool gateways
- browser/web capabilities
- memory/learning mechanisms
- unattended cron execution
- delivery of results back to communication channels

This is particularly relevant to Nārada because Nārada also needs to remain useful when the user is absent.

The key lesson is:

> **The conversation interface should be only one doorway into the agent.**

Other doorways are:

```text
Chat
Phone
Telegram
Email
Webhook
Schedule
GitHub event
Calendar event
File event
System event
```

The agent runtime remains the same.

Hermes also demonstrates an important pattern for scheduled work: a scheduled execution can start a **fresh agent session** with its own context and deliver its result to a configured destination. Scheduled prompts therefore need to be self-contained enough to run without the original conversation. citeturn0search1

Nārada should adopt that principle.

---

# 5. Nārada Gateway

The central process should eventually be called the:

```text
Nārada Gateway
```

It is not merely an HTTP server.

It is the always-on boundary between:

```text
USER / EVENTS
       ↓
    GATEWAY
       ↓
    RUNTIME
       ↓
    ACTIONS
       ↓
    DELIVERY
```

Responsibilities:

- receive messages
- authenticate channel users
- normalize inbound events
- route to sessions
- trigger scheduled responsibilities
- wake background work
- deliver responses
- manage approvals
- expose status
- manage webhooks
- maintain channel bindings

---

# 6. Nārada Core Internal Architecture

Inside `narada-core`:

```text
┌─────────────────────────────────────────────────────┐
│                    NĀRADA CORE                      │
│                                                     │
│  Gateway                                             │
│     │                                                │
│  Session Manager                                     │
│     │                                                │
│  Responsibility Manager                              │
│     │                                                │
│  Agent Runtime                                       │
│     │                                                │
│  ┌──┴──────────┬─────────────┬──────────────┐       │
│  │             │             │              │       │
│ Planner      Executor      Observer      Memory     │
│  │             │             │              │       │
│  └─────────────┴─────────────┴──────────────┘       │
│                    │                                 │
│              Tool Registry                           │
│                    │                                 │
│          Permission / Approval                       │
│                    │                                 │
│               Provider Layer                         │
│                    │                                 │
│        ┌───────────┼───────────┐                     │
│        │           │           │                     │
│      Models      APIs        MCP                     │
│                                                     │
│  Scheduler / Events / Worker                         │
│                                                     │
│  Audit / Logs / Metrics                              │
│                                                     │
│  SQLite                                              │
└─────────────────────────────────────────────────────┘
```

---

# 7. Recommended Directory Structure

```text
narada/
├── apps/
│   └── api/
│       └── main.py
│
├── core/
│   ├── agent/
│   │   ├── loop.py
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── observer.py
│   │   ├── decision.py
│   │   └── state.py
│   │
│   ├── gateway/
│   │   ├── gateway.py
│   │   ├── sessions.py
│   │   ├── channels.py
│   │   └── routing.py
│   │
│   ├── responsibilities/
│   │   ├── model.py
│   │   ├── manager.py
│   │   ├── evaluator.py
│   │   └── lifecycle.py
│   │
│   ├── memory/
│   │   ├── working.py
│   │   ├── episodic.py
│   │   ├── semantic.py
│   │   ├── responsibility.py
│   │   ├── retrieval.py
│   │   └── store.py
│   │
│   ├── tools/
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── permissions.py
│   │   ├── risk.py
│   │   └── approval.py
│   │
│   ├── events/
│   │   ├── model.py
│   │   ├── bus.py
│   │   ├── dispatcher.py
│   │   └── handlers.py
│   │
│   ├── scheduler/
│   │   ├── scheduler.py
│   │   ├── jobs.py
│   │   └── wake.py
│   │
│   ├── sessions/
│   │   ├── session.py
│   │   ├── context.py
│   │   └── lifecycle.py
│   │
│   ├── runtime/
│   │   ├── runtime.py
│   │   ├── local.py
│   │   └── sandbox.py
│   │
│   ├── providers/
│   │   └── registry.py
│   │
│   ├── audit/
│   │   ├── logger.py
│   │   └── models.py
│   │
│   └── config/
│       └── settings.py
│
├── providers/
│   ├── llm/
│   │   ├── sarvam.py
│   │   ├── ollama.py
│   │   └── openai_compatible.py
│   │
│   ├── tts/
│   │   ├── sarvam.py
│   │   └── elevenlabs.py
│   │
│   ├── stt/
│   │   └── sarvam.py
│   │
│   ├── channels/
│   │   ├── telegram.py
│   │   ├── email.py
│   │   ├── discord.py
│   │   ├── slack.py
│   │   └── webhook.py
│   │
│   └── services/
│       ├── github.py
│       ├── google.py
│       └── notion.py
│
├── tools/
│   ├── builtin/
│   ├── mcp/
│   └── browser/
│
├── skills/
│   ├── builtins/
│   └── installed/
│
├── sandboxes/
│   ├── manager.py
│   ├── docker.py
│   └── policies.py
│
├── storage/
│   ├── sqlite/
│   └── migrations/
│
├── infra/
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── compose.yml
│   └── qdrant/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── agent/
│   ├── security/
│   ├── sandbox/
│   ├── channels/
│   └── e2e/
│
├── prompts/
│   ├── system/
│   ├── planner/
│   ├── observer/
│   ├── verifier/
│   ├── responsibility/
│   └── specialists/
│
├── docs/
├── scripts/
├── AGENTS.md
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

---

# 8. Phase 0 — Architecture Freeze

## Goal

Before writing substantial code, establish the boundaries.

## Build

Create:

```text
pyproject.toml
AGENTS.md
README.md
.env.example
docker-compose.yml
core/
providers/
tests/
```

Define interfaces:

```text
LLMProvider
STTProvider
TTSProvider
ToolProvider
MemoryProvider
ChannelProvider
SandboxProvider
SchedulerProvider
EventBus
```

## Verification

The following must be true:

- core imports no vendor SDK
- providers can be swapped
- SQLite is a file, not a service
- external APIs are represented as providers
- Docker is used for the Nārada backend
- optional infrastructure is explicit
- no AWS dependency exists in core

## Tests

Write import-level architecture tests.

Example:

```python
def test_core_does_not_import_vendor_sdk():
    ...
```

Also test that configuration can select providers without changing core code.

## Stop condition

STOP if:

- vendor-specific logic appears in `core/`
- the design requires a database server for BASE
- Docker becomes mandatory for every external API
- the architecture requires AWS for local execution

Do not proceed until the boundaries are corrected.

---

# 9. Phase 1 — NĀRADA CORE Container

## Goal

Create one container that stays alive and provides the complete backend runtime.

## Container responsibilities

The first container should run:

```text
FastAPI
Agent runtime
Worker
Scheduler
SQLite
Memory
Tool registry
Provider registry
Gateway
Audit logger
```

Avoid running multiple backend containers at this stage.

## Docker requirements

The image should:

- be reproducible
- use a pinned Python version
- run as a non-root user where practical
- mount `/data`
- expose the API
- have a health check
- receive configuration through environment variables

## Expected command

```bash
docker compose up -d
```

## Verification

```bash
curl /health
```

must return a healthy state.

The container restart must not lose:

```text
SQLite database
configuration-independent state
responsibilities
tasks
audit history
```

## Test

```text
start
create responsibility
restart container
query responsibility
```

Expected:

```text
responsibility still exists
```

## Stop condition

STOP if restarting the container destroys persistent state.

---

# 10. Phase 2 — Configuration and Provider Gateway

## Goal

Nārada can connect to:

```text
Sarvam
Ollama
other OpenAI-compatible providers
```

without changing agent code.

## Configuration

Conceptual:

```env
NARADA_LLM_PROVIDER=sarvam

SARVAM_API_KEY=
SARVAM_MODEL=

OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=
```

Provider-specific configuration must stay isolated.

## Agentic implementation prompt

```text
You are implementing the Nārada provider layer.

Objective:
Create a provider-neutral LLM interface and implement the first Sarvam
and Ollama adapters.

Constraints:
- Core agent code must not import Sarvam or Ollama SDKs directly.
- Normalize provider responses into internal types.
- Support synchronous generation first.
- Keep streaming as an interface capability even if the first provider
  implementation is minimal.
- Provider errors must be normalized.
- Secrets must only come from configuration.
- Do not add a database or queue dependency.

Verification:
1. FakeLLMProvider passes the interface contract.
2. SarvamProvider can be instantiated from configuration.
3. OllamaProvider can be instantiated from configuration.
4. Agent code depends only on LLMProvider.
5. Unit tests cover success, timeout, malformed response, and auth failure.
6. No secret is printed in logs.

Stop if:
- provider-specific types leak into core,
- credentials are hard-coded,
- tests require live API credentials,
- Ollama must run inside narada-core.
```

## Verification conditions

- switching Sarvam → Ollama requires configuration only
- agent code does not change
- provider failure becomes a controlled runtime error
- logs redact credentials

---

# 11. Phase 3 — First Agent Loop

## Goal

Implement the smallest real Nārada.

The agent must support:

```text
Goal
 ↓
Plan
 ↓
Action
 ↓
Observation
 ↓
Decision
```

At first, the action may be a safe internal operation.

Do not start with browser automation.

## Agent state

Minimum:

```text
run_id
goal
plan
current_step
actions
observations
decision
status
created_at
updated_at
```

## Agentic prompt

```text
Implement the Nārada core agent loop.

The runtime must:
1. receive a goal,
2. create a structured plan,
3. select the next action,
4. execute the action through an explicit executor,
5. normalize the result as an observation,
6. update state,
7. decide whether to continue or finish.

Do not implement multi-agent delegation.
Do not implement autonomous scheduling.
Do not implement browser automation.
Do not bypass the tool registry.

The LLM proposes plans and actions.
The runtime validates and executes them.

Every transition must be observable in logs and testable without a live model.

Create a FakeLLMProvider and deterministic test scenarios.

Success condition:
A test can demonstrate:

goal → plan → action → observation → decision → completion.
```

## Verification

A deterministic fake run must produce:

```text
RUNNING
 → PLANNING
 → EXECUTING
 → OBSERVING
 → DECIDING
 → COMPLETED
```

## Stop conditions

STOP if:

- LLM output directly executes shell commands
- state exists only in prompt text
- the executor cannot distinguish proposed vs authorized actions
- the loop cannot terminate deterministically

---

# 12. Phase 4 — Memory Foundation

## Goal

Give Nārada persistent memory without adding unnecessary infrastructure.

Use:

```text
SQLite
+
FTS
```

## Tables

Initial conceptual tables:

```text
sessions
messages
agent_runs
tasks
responsibilities
memories
events
audit_events
approvals
```

Do not implement every column at once.

## Memory types

```text
working
episodic
semantic
responsibility
```

## Memory write policy

A memory candidate should be evaluated:

```text
candidate
 ↓
relevance?
 ↓
importance?
 ↓
durability?
 ↓
store
```

## Agentic prompt

```text
Implement Nārada's SQLite memory layer.

Requirements:
- SQLite is embedded, not a separate container.
- Database file must live under the persistent /data volume.
- Use migrations.
- Support sessions, messages, tasks, responsibilities, events,
  memories, approvals, and audit events as incremental schemas.
- Separate working memory from durable memory conceptually.
- Do not automatically store every message as permanent memory.
- Provide deterministic retrieval for tests.
- Keep vector search out of this phase.

Verification:
- create memory
- restart process/container
- retrieve memory
- search memory
- associate memory with a responsibility
- delete/test cleanup
- migrate from empty database

Stop if:
- Qdrant becomes mandatory
- PostgreSQL becomes mandatory
- memory is only stored in process memory
- every conversation message is automatically promoted to permanent memory.
```

---

# 13. Phase 5 — Tool Registry

## Goal

Give Nārada controlled capabilities.

Start with:

```text
filesystem.read
filesystem.write
web.search
```

Avoid shell initially if possible.

## Tool object

Conceptually:

```python
Tool(
    name="filesystem.read",
    description="Read a file",
    risk="low",
    requires_confirmation=False,
    input_schema=...,
    output_schema=...
)
```

## Tool lifecycle

```text
discover
 ↓
validate
 ↓
authorize
 ↓
approve if needed
 ↓
execute
 ↓
observe
 ↓
audit
```

## Agentic prompt

```text
Implement the Nārada tool registry.

Rules:
- A tool is a capability, not permission.
- Every tool has a risk classification.
- Every tool has an input schema.
- Every execution is auditable.
- The LLM cannot call tools directly.
- The runtime receives a proposed tool call and evaluates it.
- Tool failures become structured observations.

Implement:
- registration
- discovery
- lookup
- risk metadata
- permission evaluation
- execution
- audit

Tests must prove:
1. unknown tools cannot execute,
2. disabled tools cannot execute,
3. permitted read tools execute,
4. denied tools fail before side effects,
5. tool output becomes an observation.
```

---

# 14. Phase 6 — Permissions and Approval Engine

## Goal

Make safety architectural.

## Permission dimensions

Consider:

```text
identity
scope
tool
resource
action
risk
approval
time
responsibility
```

Example:

```yaml
permission:
  principal: narada
  tool: github.write
  scope: repository:X
  actions:
    - create_issue
  approval: required
```

## Risk levels

Recommended conceptual levels:

```text
NONE
LOW
MEDIUM
HIGH
CRITICAL
```

## Baseline policy

```text
read public web        LOW
read local file        LOW
write local file       MEDIUM
send message           HIGH
shell command          HIGH
delete data            CRITICAL
financial action       CRITICAL
deployment             CRITICAL
```

The exact classification is policy, not a property of the LLM.

## Stop conditions

STOP immediately if:

- permission checks happen after execution
- approval exists only in UI
- an LLM can mark its own action as approved
- approval state cannot be audited
- a retry can bypass approval

---

# 15. Phase 7 — MCP

## Goal

Connect existing tool ecosystems rather than building custom integrations.

Architecture:

```text
Nārada Tool Registry
       ↓
MCP Client
       ↓
MCP Server
       ↓
External Service
```

## First MCP integrations

Prefer:

```text
filesystem
GitHub
browser
Notion
```

depending on availability and need.

## Verification

For every MCP server:

```text
discover server
 ↓
list tools
 ↓
validate schemas
 ↓
apply Nārada permissions
 ↓
execute
 ↓
audit
```

Nārada's permission layer remains authoritative.

An MCP server must not become an authorization bypass.

---

# 16. Phase 8 — Browser and Web Research

## Goal

Allow Nārada to research and inspect public information.

Use:

```text
Playwright
+
web/search provider
+
MCP where useful
```

## First meaningful demo

```text
"Nārada, research X, compare the sources, remember the result,
and explain what you found."
```

## Agentic research prompt

```text
Research the requested topic.

Rules:
1. State what information is needed before searching.
2. Prefer authoritative sources.
3. Search using the available web tool.
4. Open relevant sources.
5. Extract only information needed for the goal.
6. Track source URLs.
7. Distinguish facts from inference.
8. Store durable findings only if they are useful beyond this task.
9. If evidence conflicts, report the conflict.
10. Stop searching when additional search is unlikely to materially improve
    the answer.

Do not:
- fabricate sources,
- claim a page was opened if it was not,
- treat search snippets as verified facts,
- continue searching indefinitely.
```

## Verification

Test:

```text
query
search
open
extract
summarize
memory write
```

## Stop conditions

STOP when:

- search loops indefinitely
- the agent repeatedly opens the same pages
- citations are fabricated
- browser side effects occur without permission

---

# 17. Phase 9 — Skills System

## Goal

Create reusable procedural knowledge.

A skill is not another agent.

A skill is a reusable capability/workflow definition.

Examples:

```text
researcher
github-review
daily-brief
meeting-prep
project-audit
deployment-check
email-triage
```

## Skill structure

Conceptually:

```text
skill/
├── SKILL.md
├── prompts/
├── schemas/
├── tests/
└── examples/
```

Skills should specify:

```text
purpose
inputs
outputs
tools
constraints
verification
failure behavior
```

## Why skills matter

The same workflow should not be rediscovered by the model every time.

Instead:

```text
Responsibility
 ↓
Skill
 ↓
Task
 ↓
Tools
```

---

# 18. Phase 10 — Scheduled Responsibilities

## Goal

Allow Nārada to work without the user being present.

Example:

> "Every six hours, check my GitHub project and tell me if something important changed."

Represent:

```text
Responsibility
 ├── goal
 ├── schedule
 ├── tools
 ├── memory
 ├── delivery target
 └── permissions
```

## Scheduler

Start with an in-process scheduler or APScheduler inside `narada-core`.

Do not create a scheduler container.

## Scheduled execution model

```text
scheduler
   ↓
due responsibility
   ↓
create fresh execution session
   ↓
load responsibility state
   ↓
load required skills
   ↓
run agent
   ↓
update state
   ↓
deliver result
```

This is intentionally similar to the useful part of Hermes's cron model: scheduled work gets a fresh execution context and has an explicit delivery destination. citeturn0search1

## Critical rule

Scheduled prompts must be self-contained.

Bad:

```text
"Check that thing we discussed."
```

Good:

```text
"Check repository X for new pull requests since the previous successful
run. Compare against the stored responsibility state. If there is a
meaningful change, summarize it and send it to the configured Telegram
destination. Otherwise record the check and remain silent."
```

---

# 19. Phase 11 — Responsibility Engine

## Goal

Move from "scheduled prompts" to actual persistent responsibility.

A responsibility should have:

```text
id
name
description
goal
status
priority
schedule
trigger rules
required skills
allowed tools
permissions
memory namespace
delivery targets
last_run
next_run
last_success
last_failure
state
```

## Responsibility lifecycle

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

Failure state:

```text
ACTIVE
 ↓
ERROR
 ↓
RECOVERY
 ↓
ACTIVE
```

## Responsibility agent prompt

```text
You are evaluating a persistent responsibility.

Your job is not to produce a generic response.

Determine:
1. what the responsibility currently requires,
2. what has changed since the last successful evaluation,
3. whether a new task is required,
4. whether the task is safe and authorized,
5. whether the user needs to be notified.

If nothing meaningful changed:
- record the check,
- update last_checked,
- do not notify.

If meaningful progress/change occurred:
- record evidence,
- update responsibility state,
- notify only according to delivery policy.

Never invent change.
Never report a failed check as a successful check.
Never silently change responsibility permissions.
```

---

# 20. Phase 12 — Event-Driven Wakeups

## Goal

Nārada should wake because something happened, not because the LLM is constantly running.

Event types:

```text
timer.triggered
email.received
github.push
github.issue
github.pull_request
calendar.event
file.changed
webhook.received
task.completed
tool.failed
approval.received
user.message
system.alert
```

## Event pipeline

```text
event
 ↓
normalize
 ↓
persist
 ↓
match responsibilities
 ↓
filter irrelevant
 ↓
wake relevant responsibility
 ↓
agent execution
```

---

# 21. Event Filtering Prompt

```text
You are the Nārada event relevance evaluator.

Given:
- event,
- active responsibilities,
- responsibility goals,
- prior state,

determine whether the event requires work.

Return exactly:
- relevant: yes/no
- responsibility_ids
- reason
- urgency
- recommended_action

Rules:
- Ignore events unrelated to active responsibilities.
- Do not wake the agent for duplicate events unless state changed.
- Prefer batching noisy events.
- Never infer importance without evidence.
- A relevant event does not automatically authorize an external action.
```

---

# 22. Phase 13 — Notification Gateway

## Goal

Separate "agent did work" from "user received information."

Create:

```text
DeliveryGateway
```

Potential providers:

```text
Telegram
Email
Discord
Slack
WhatsApp-compatible provider
SMS
Signal
Web push
Mobile push
Webhook
```

The exact provider set is deployment-dependent.

---

# 23. User Communication Model

A user should be able to communicate with Nārada from different places.

Conceptually:

```text
                         NĀRADA
                           │
             ┌─────────────┼─────────────┐
             │             │             │
           Web          Telegram       Email
             │             │             │
             └─────────────┼─────────────┘
                           │
                     Session Router
                           │
                     Agent Runtime
```

Additional future channels:

```text
Phone
SMS
Discord
Slack
Signal
WhatsApp
Google Chat
Teams
Home Assistant
mobile app
```

Hermes demonstrates the value of a single agent gateway supporting many channels; its current documentation lists 20+ messaging/platform integrations and scheduled delivery. citeturn0search0

Nārada should pursue the same architectural property while keeping each connector replaceable.

---

# 24. Channel Identity

A major requirement is mapping external identities to one Nārada identity.

Example:

```text
Telegram user 123
Email user@example.com
Discord user 456
Phone +91...
```

must map to:

```text
Nārada User
    ↓
User identity
```

Do not identify users solely by display name.

Use:

```text
provider
external_user_id
channel
verified_at
account_id
```

---

# 25. Session Routing

A message should resolve to:

```text
channel
 ↓
external identity
 ↓
Nārada user
 ↓
conversation/session
 ↓
responsibility context
 ↓
agent
```

Example:

```text
Telegram:
"How is my GitHub project?"

       ↓

Nārada user
       ↓
GitHub responsibility
       ↓
current state
       ↓
agent
```

The user should not have to explain who they are on every channel.

---

# 26. Email Integration

Email can serve two roles.

## Inbound

```text
email
 ↓
email provider
 ↓
Nārada gateway
 ↓
event
 ↓
agent
```

Examples:

```text
new invoice
GitHub notification
college email
meeting invitation
support response
```

## Outbound

```text
Nārada
 ↓
delivery policy
 ↓
email provider
 ↓
user
```

High-risk outbound email should require approval unless the responsibility explicitly grants permission.

---

# 27. Phone Communication

Phone should be treated as a channel, not as the agent itself.

Potential architecture:

```text
Phone
 ↓
telephony provider
 ↓
voice webhook / stream
 ↓
STT
 ↓
Nārada
 ↓
LLM
 ↓
TTS
 ↓
telephony provider
 ↓
Phone
```

Possible providers include telephony APIs such as Twilio or regional equivalents.

Do not make phone calls automatically merely because the agent can.

Calling a human is a consequential external action.

Default:

```text
call_user → approval or explicit responsibility permission
```

---

# 28. Voice Messaging

A lower-risk alternative to live calls is voice messaging.

Architecture:

```text
Telegram/WhatsApp/etc.
 ↓
voice message
 ↓
STT
 ↓
Nārada
 ↓
response
 ↓
TTS
 ↓
voice reply
```

This can reuse:

```text
Saaras
Bulbul / ElevenLabs / other TTS
```

without requiring a live telephony stack.

---

# 29. Phase 14 — Away-Mode Notification Policy

Nārada should distinguish:

```text
silent
informational
important
urgent
approval_required
```

Example:

```text
routine check        → silent
minor change         → digest
meaningful change    → notify
urgent issue         → immediate notify
dangerous action     → approval request
```

This prevents notification spam.

---

# 30. Notification Deduplication

The same event may arrive through:

```text
webhook
email
polling
GitHub
calendar
```

Nārada should deduplicate.

Use event identity where available:

```text
source
event_type
external_event_id
timestamp
hash
```

Before notifying:

```text
Have I already delivered this fact?
```

If yes:

```text
update state
do not duplicate notification
```

---

# 31. Phase 15 — Sandbox Runtime

Autonomous agents need isolation.

Do not allow the main Nārada container to become an unrestricted shell.

Preferred model:

```text
narada-core
     │
     │ sandbox manager
     ▼
ephemeral sandbox container
     │
     ├── filesystem
     ├── shell
     ├── browser
     ├── code
     └── tests
```

The main container coordinates.

The sandbox performs risky work.

---

# 32. Sandbox Types

Potential sandbox profiles:

```text
python
node
browser
coding
data-analysis
general-linux
```

Example:

```text
coding-sandbox
├── Python
├── Node
├── git
├── package managers
└── test tools
```

Do not put every dependency into `narada-core`.

---

# 33. Sandbox Isolation

A sandbox should ideally have:

- separate filesystem
- limited network
- CPU limit
- memory limit
- execution timeout
- process limit
- non-root user
- explicit mounted workspace
- no host credentials
- no access to Nārada's SQLite database
- no unrestricted Docker socket

The sandbox receives only what it needs.

---

# 34. Sandbox Mount Policy

Bad:

```text
mount entire home directory
```

Better:

```text
mount only task workspace
```

Example:

```text
host:
~/narada/workspaces/task-123

sandbox:
/workspace
```

The agent should not automatically see:

```text
~/.ssh
~/.aws
~/.config
password stores
browser profiles
Nārada secrets
```

---

# 35. Docker Socket Warning

Do not give `narada-core` unrestricted access to:

```text
/var/run/docker.sock
```

unless there is a carefully designed security boundary.

The Docker socket can effectively grant host-level control.

If Nārada needs to launch sandboxes:

Prefer a controlled sandbox runner or narrowly scoped execution service.

Early development may use Docker Engine APIs only in explicitly trusted local environments, but this must be documented as a high-risk capability.

---

# 36. Sandbox Lifecycle

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

Persistent workspaces are separate:

```text
workspace
 ↓
sandbox
 ↓
result
 ↓
workspace remains
```

The sandbox itself can be disposable.

---

# 37. Sandbox Stop Conditions

Hard-stop execution when:

- timeout exceeded
- memory limit exceeded
- process count exceeded
- unexpected network access detected
- approval revoked
- sandbox attempts privileged escalation
- sandbox attempts to access secrets
- execution becomes non-responsive

The agent should receive:

```text
sandbox_stopped
reason
partial_output
```

rather than an ambiguous failure.

---

# 38. Phase 16 — Coding Agent

Use OpenHands or another specialist rather than reinventing a full coding agent.

Flow:

```text
Nārada
 ↓
Create coding task
 ↓
Create sandbox
 ↓
Delegate
 ↓
OpenHands
 ↓
Modify workspace
 ↓
Run tests
 ↓
Collect diff
 ↓
Nārada verifies
 ↓
Approval
 ↓
Apply/publish
```

Important:

```text
coding complete
```

does not imply:

```text
safe to merge/deploy
```

---

# 39. Coding Verification Prompt

```text
You are verifying a delegated coding task.

Inspect:
1. requested change,
2. repository diff,
3. tests added/changed,
4. test results,
5. lint/type results,
6. unexpected modifications,
7. dependency changes,
8. security-sensitive changes.

Return:
- requested_change_satisfied
- tests_pass
- unexpected_changes
- security_concerns
- deployment_ready
- explanation

Never mark deployment_ready solely because tests pass.
```

---

# 40. Phase 17 — Specialist Agents

Specialists should be isolated workers.

Examples:

```text
Researcher
Coder
Browser
Document
Data
Voice
```

Nārada remains the chief agent.

Architecture:

```text
Nārada
   │
   ├── Researcher
   ├── Coder
   ├── Browser
   └── Data
```

---

# 41. Delegation Contract

Every specialist receives:

```text
task_id
parent_run_id
objective
constraints
allowed_tools
permissions
workspace
deadline
expected_output_schema
verification_requirements
```

Every specialist returns:

```text
task_id
status
summary
artifacts
evidence
tests
warnings
recommended_next_action
```

---

# 42. Delegation Prompt

```text
You are a specialist agent working under Nārada.

You are not the owner of the overall responsibility.

Your task is:
{task}

Constraints:
{constraints}

Allowed tools:
{tools}

Required output:
{schema}

Rules:
- Stay within the assigned task.
- Do not create unrelated work.
- Do not change permissions.
- Do not contact the user directly unless explicitly instructed.
- Report uncertainty.
- Report failures honestly.
- Return evidence for important claims.
- Stop when the task is complete.
```

---

# 43. Phase 18 — Autonomous Recovery

Autonomous systems must expect failure.

Failure classes:

```text
provider failure
network failure
tool failure
permission failure
approval timeout
sandbox failure
model failure
invalid output
rate limit
authentication failure
external service outage
```

Each needs different behavior.

---

# 44. Recovery Matrix

| Failure | Action |
|---|---|
| network timeout | bounded retry |
| rate limit | backoff |
| auth failure | stop + notify |
| permission denied | stop; do not retry |
| approval pending | pause |
| provider unavailable | fallback if policy permits |
| malformed model output | retry/re-prompt bounded times |
| sandbox timeout | terminate sandbox |
| external API outage | defer responsibility |
| repeated failure | escalate to user |

---

# 45. Retry Rules

Never retry blindly.

A retry must know:

```text
Is the action idempotent?
Did it execute?
Could it have partially succeeded?
```

For external side effects:

```text
send email
create issue
purchase
deploy
```

a timeout does not prove failure.

The system must reconcile state before retrying.

---

# 46. Phase 19 — Approval While User Is Away

An approval request must survive user absence.

Example:

```text
Nārada:
"I prepared the deployment.
Tests pass.
Deploying will modify production.
Approve deployment?"

User away.
```

State:

```text
approval.pending
```

Later:

```text
Telegram:
"Approve deployment?"

User:
"yes"
```

Then:

```text
approval.granted
 ↓
resume task
```

Approval must be tied to:

```text
task_id
action_id
exact action
scope
expiration
requester
```

Never interpret an unrelated "yes" as approval.

---

# 47. Approval Expiration

Approvals should optionally expire.

Example:

```text
approval:
  action: deploy production
  expires_at: ...
```

If expired:

```text
do not execute
request fresh approval
```

This prevents stale approvals from being reused later.

---

# 48. Phase 20 — Session Model

Nārada needs more than conversations.

Define:

```text
User
Conversation
Session
Run
Task
Responsibility
Event
```

They are different.

## Conversation

Human-facing dialogue.

## Session

A bounded context window / interaction state.

## Run

One execution of the agent.

## Task

A unit of work.

## Responsibility

A persistent assignment.

---

# 49. Fresh Sessions for Autonomous Work

When Nārada wakes from a timer:

Do not necessarily restore the entire historical conversation.

Instead:

```text
fresh run
+
responsibility state
+
relevant memory
+
recent events
+
skill
+
permissions
```

This prevents context growth and makes unattended runs deterministic.

---

# 50. Context Assembly

Before calling the model, build context from:

```text
system identity
+
responsibility
+
goal
+
current task
+
relevant memory
+
recent observations
+
available tools
+
permissions
+
approval state
+
event
```

Do not dump:

```text
entire database
entire conversation history
all memories
all tools
```

into every model call.

---

# 51. Context Budget Policy

Context should be prioritized:

```text
1. current safety/permission state
2. current task
3. current goal
4. relevant responsibility
5. recent observations
6. relevant memory
7. historical context
```

If context must be removed, preserve safety and task state first.

---

# 52. Phase 21 — Model Routing

Nārada should eventually route work between:

```text
Ollama
Sarvam
other providers
specialist models
```

Possible policy:

```text
private/simple → local
complex reasoning → remote
voice language task → suitable provider
coding → coding specialist
browser-heavy → browser specialist
```

Routing must consider:

```text
privacy
cost
latency
quality
availability
task type
```

Never route private content to a remote provider solely because it is higher quality without respecting policy.

---

# 53. Model Routing Verification

Given:

```text
task
privacy policy
cost policy
provider availability
```

the router must produce:

```text
provider
model
reason
policy_basis
```

Test:

```text
private=true
remote_allowed=false
```

must never choose a remote provider.

---

# 54. Phase 22 — Channel Gateway

Implement channels behind:

```text
ChannelProvider
```

Minimum useful progression:

```text
Web
Telegram
Email
Webhook
```

Later:

```text
Discord
Slack
SMS
Signal
WhatsApp
Phone
mobile push
```

---

# 55. Channel Adapter Contract

Each channel should implement concepts such as:

```text
receive()
send()
edit()
typing()
attachments()
voice()
identity()
capabilities()
```

Not every channel supports every capability.

Normalize them internally.

---

# 56. Channel Capability Matrix

Example:

| Capability | Web | Telegram | Email | SMS | Phone |
|---|---:|---:|---:|---:|---:|
| text in | yes | yes | yes | yes | via STT |
| text out | yes | yes | yes | yes | via TTS |
| files | yes | yes | yes | limited | no |
| voice | optional | yes | attachment | no | yes |
| interactive approval | yes | yes | links/reply | limited | voice |
| streaming | yes | limited | no | no | yes |

The exact capabilities depend on provider implementations.

---

# 57. Phase 23 — Webhook Gateway

External services should be able to wake Nārada.

Examples:

```text
GitHub webhook
Stripe webhook
calendar webhook
email webhook
custom service
```

Flow:

```text
POST /webhooks/{provider}
 ↓
authenticate
 ↓
normalize
 ↓
persist event
 ↓
dispatch
```

Webhook endpoints must not directly execute arbitrary agent actions.

---

# 58. Webhook Security

Verify:

- signature
- timestamp
- replay protection
- source
- event ID

Then:

```text
persist
deduplicate
dispatch
```

Never trust a webhook merely because it reached the endpoint.

---

# 59. Phase 24 — "Nārada While I Sleep"

This is a key acceptance milestone.

User says:

> "Watch my project overnight and tell me if anything important happens."

Nārada must:

```text
create responsibility
 ↓
validate schedule
 ↓
validate tools
 ↓
validate permissions
 ↓
validate notification channel
 ↓
activate
 ↓
sleep
```

Then:

```text
event
 ↓
wake
 ↓
check
 ↓
reason
 ↓
act
 ↓
remember
 ↓
notify if necessary
 ↓
sleep
```

---

# 60. Overnight Verification Scenario

Test:

1. Create responsibility.
2. Start Nārada.
3. Stop foreground terminal.
4. Keep Docker container running.
5. Inject a test event.
6. Verify Nārada wakes.
7. Verify action executes.
8. Verify memory updates.
9. Verify notification is delivered.
10. Verify audit trail.
11. Verify responsibility remains active.

Expected:

```text
user does nothing
+
event occurs
=
Nārada handles it
```

---

# 61. Phase 25 — Daily Digest

Nārada should eventually support a digest.

Example:

```text
Every morning:
- summarize what happened overnight
- list completed responsibilities
- list failures
- list pending approvals
- list important changes
- list items needing user attention
```

The digest should be generated from structured state, not from blindly replaying logs.

---

# 62. Daily Digest Prompt

```text
Generate the user's daily Nārada briefing.

Include only:
1. meaningful events,
2. completed work,
3. failures requiring attention,
4. pending approvals,
5. important changes,
6. blocked responsibilities.

For each item:
- state what happened,
- state why it matters,
- state what Nārada did,
- state what the user must do, if anything.

Do not include routine successful checks.
Do not fabricate activity.
Do not expose internal secrets.
```

---

# 63. Phase 26 — Skills + Responsibilities + Channels

At this point the core model becomes:

```text
USER
 ↓
RESPONSIBILITY
 ↓
SKILL
 ↓
TASK
 ↓
AGENT
 ↓
TOOLS
 ↓
EVENTS
 ↓
MEMORY
 ↓
DELIVERY
```

This is the heart of Nārada.

---

# 64. Phase 27 — Qdrant / Semantic Memory

Only now consider Qdrant.

Trigger conditions:

- FTS retrieval is insufficient
- semantic retrieval materially improves outcomes
- memory volume is large enough
- multiple memory types need embedding search

Docker:

```text
narada-core
      │
      ▼
    qdrant
```

Do not move all memory out of SQLite.

Keep canonical metadata/state in SQLite or later PostgreSQL.

Qdrant stores vectors.

---

# 65. Vector Memory Architecture

```text
Memory candidate
      ↓
importance filter
      ↓
embedding
      ↓
Qdrant
      ↓
semantic retrieval
      ↓
SQLite metadata
      ↓
context assembly
```

If Qdrant is unavailable:

```text
fallback → FTS
```

The agent should remain functional.

---

# 66. Phase 28 — PostgreSQL

Only introduce PostgreSQL when:

- SQLite concurrency becomes limiting
- multiple workers require it
- remote/cloud deployment requires it
- transactional requirements justify it

Migration should preserve the domain model.

Do not make PostgreSQL-specific SQL part of core business logic unnecessarily.

---

# 67. Phase 29 — Redis

Introduce Redis when:

```text
one process
```

becomes:

```text
multiple workers
```

or when:

```text
durable event/queue semantics
```

are required.

Potential uses:

```text
job queue
event bus
locks
short-lived coordination
```

Do not store canonical long-term memory only in Redis.

---

# 68. Phase 30 — Cloud / Hybrid

Only after local autonomy is reliable.

Target:

```text
                    AWS
             ┌────────────────┐
             │ API            │
             │ Scheduler      │
             │ State          │
             │ Notifications  │
             └───────┬────────┘
                     │
                  secure link
                     │
                     ▼
                 LOCAL NĀRADA
                 ├── Ollama
                 ├── private files
                 ├── local tools
                 └── GPU
```

The local runtime should remain capable of operating independently.

---

# 69. Local Gateway Security

Hybrid mode creates a major security boundary.

Never expose:

```text
Ollama
filesystem
shell
Docker
```

directly to the public internet.

Instead:

```text
AWS
 ↓
authenticated gateway
 ↓
local Nārada
```

Use:

- authenticated requests
- encrypted transport
- scoped tokens
- request IDs
- replay protection
- explicit allowed operations

---

# 70. Phase 31 — Cloud Scale-to-Zero

For truly unattended cloud deployments, the scheduler should eventually be able to wake the runtime only when work exists.

Conceptually:

```text
scheduled event
 ↓
cloud scheduler
 ↓
wake worker
 ↓
run Nārada
 ↓
deliver
 ↓
shutdown
```

Hermes's current architecture provides a useful example of this idea: its managed cron provider can arm one-shot future triggers so an idle gateway can scale to zero and wake only for an actual scheduled execution. citeturn0search2

Nārada can eventually use an analogous architecture on AWS rather than keeping an expensive process alive continuously.

---

# 71. Phase 32 — Observability

Nārada must explain itself.

Expose:

```text
health
agent runs
responsibilities
tasks
events
approvals
tool calls
provider calls
failures
cost/usage
```

Useful API concepts:

```text
GET /health
GET /status
GET /runs
GET /responsibilities
GET /tasks
GET /events
GET /approvals
GET /tools
GET /logs
```

---

# 72. Run Trace

Every agent run should have:

```text
run_id
parent_run_id
responsibility_id
task_id
session_id
started_at
ended_at
status
provider
model
tool_calls
approvals
memory_updates
result
failure
```

This makes autonomous behavior debuggable.

---

# 73. Phase 33 — Cost Tracking

Track:

```text
provider
model
tokens if available
duration
tool usage
external API calls
sandbox duration
estimated cost
```

Do not block BASE on perfect accounting.

But design the execution model so usage can be measured later.

---

# 74. Phase 34 — Resource Budgets

Responsibilities should eventually support budgets:

```yaml
limits:
  max_runtime: 10m
  max_tool_calls: 20
  max_model_calls: 8
  max_cost: 0.50
  max_retries: 3
```

A budget violation should stop or pause execution.

This is critical for autonomous systems.

---

# 75. Budget Verification

Test:

```text
max_tool_calls = 3
```

and force the agent to request 4 calls.

Expected:

```text
third call executes
fourth call rejected
run status = budget_exceeded
user notified according to policy
audit event recorded
```

---

# 76. Phase 35 — Agentic Prompt Library

Prompts should be versioned.

Directory:

```text
prompts/
├── system/
├── planner/
├── executor/
├── observer/
├── verifier/
├── responsibility/
├── recovery/
├── approval/
└── specialists/
```

Do not bury large prompts in Python source.

---

# 77. Core System Prompt

Recommended conceptual prompt:

```text
You are Nārada, a personal autonomous agent runtime.

Your purpose is to help the user accomplish goals and maintain ongoing
responsibilities.

You operate through explicit tools and permissions.

You must distinguish:
- what the user wants,
- what you know,
- what you infer,
- what you can do,
- what you are authorized to do.

You do not have authority merely because a tool exists.

Before consequential actions:
- inspect permission,
- inspect approval requirements,
- obtain approval when required.

When working on responsibilities:
- preserve state,
- avoid duplicate work,
- record meaningful changes,
- recover from failures,
- notify the user when policy requires it.

Never fabricate tool results, sources, actions, approvals, or memory.

When uncertain about a consequential action:
stop and ask.
```

---

# 78. Planner Prompt

```text
You are Nārada's planner.

Given:
- goal
- responsibility
- current state
- relevant memory
- available tools
- permissions
- event

Produce a minimal executable plan.

For each step include:
- objective
- action type
- required tool
- expected observation
- risk
- approval requirement
- completion condition

Rules:
- do not propose unauthorized actions,
- do not include unnecessary steps,
- do not repeat completed work,
- do not assume tool success,
- stop planning when the goal is satisfied.
```

---

# 79. Executor Prompt

The executor should preferably be deterministic code, not an LLM prompt.

If model assistance is required:

```text
You may propose an action.

You may not authorize it.

The runtime will independently validate:
- tool exists,
- input schema,
- permission,
- risk,
- approval,
- budget.

Do not claim that an action occurred until the tool returns a result.
```

---

# 80. Observer Prompt

```text
You are Nārada's observation interpreter.

Given the raw tool result:

Determine:
- success/failure,
- facts,
- changes,
- warnings,
- uncertainty,
- next relevant state.

Do not invent information absent from the result.

If the tool failed:
mark it as failed.

If the result is ambiguous:
mark uncertainty rather than guessing.
```

---

# 81. Verifier Prompt

```text
You are Nārada's verifier.

Determine whether the requested goal has actually been achieved.

Evidence must come from:
- tool results,
- test results,
- explicit state,
- verified external responses.

Do not accept the agent's own claim as evidence.

Return:
- complete: true/false
- evidence
- unresolved_items
- recommended_next_action
```

---

# 82. Recovery Prompt

```text
A task failed.

Classify the failure:
- transient
- permanent
- permission
- approval
- provider
- external_service
- invalid_state
- unknown

Then determine:
- retry?
- fallback?
- pause?
- notify?
- abandon?

Never retry a consequential side effect merely because no response was received.
First determine whether the side effect may already have occurred.
```

---

# 83. Approval Prompt

```text
A consequential action requires user approval.

Present:
- exact action,
- target,
- expected effect,
- risk,
- relevant context,
- expiration,
- alternatives.

Do not bundle unrelated actions into one approval.

The user must be able to understand exactly what will happen.

Wait for explicit approval.
```

---

# 84. Autonomous Responsibility Prompt

```text
You are executing a persistent Nārada responsibility.

Responsibility:
{responsibility}

Goal:
{goal}

Previous state:
{state}

Relevant memory:
{memory}

Current event:
{event}

Your job:
1. determine whether work is required,
2. perform only authorized work,
3. verify the result,
4. update responsibility state,
5. store useful memory,
6. decide whether the user needs notification.

If no meaningful change occurred:
record the check and remain silent.

If blocked:
record the exact blocker.

If approval is required:
pause and request approval.

Never fabricate progress.
```

---

# 85. Daily Digest Prompt

```text
Generate a concise but complete briefing from Nārada's structured state.

Include:
- meaningful overnight changes,
- completed work,
- failures,
- blocked responsibilities,
- pending approvals,
- important upcoming events.

Exclude:
- routine successful checks,
- internal model reasoning,
- secrets,
- duplicate notifications.

For every item:
state what happened and what the user should do next, if anything.
```

---

# 86. Phase 36 — Verification Harness

Create a fake world for Nārada.

The agent should be testable without real external services.

Implement fake providers:

```text
FakeLLM
FakeGitHub
FakeEmail
FakeCalendar
FakeWeb
FakeTelegram
FakeSandbox
FakeClock
```

Then scenarios can be deterministic.

---

# 87. Fake Clock

Time is critical.

Never write autonomous scheduler tests that depend on real wall-clock waiting.

Use:

```text
FakeClock
```

Tests:

```text
now = 09:00
schedule = every hour

advance 60 minutes

expect:
job fired
```

---

# 88. Fake Event Bus

Tests should be able to inject:

```text
github.push
email.received
timer.triggered
approval.received
```

and observe:

```text
responsibility awakened
agent run created
task executed
memory updated
notification delivered
```

---

# 89. End-to-End Test Scenario 1

## Research

User:

```text
Research topic X and remember the important findings.
```

Expected:

```text
message
 ↓
session
 ↓
agent
 ↓
web search
 ↓
source inspection
 ↓
verification
 ↓
memory
 ↓
response
```

Verification:

- source URLs present
- memory created
- no fabricated source
- no duplicate tool calls
- run complete

---

# 90. End-to-End Test Scenario 2

## Monitoring

User:

```text
Watch repository X and tell me when an important change occurs.
```

Expected:

```text
responsibility created
schedule created
run #1
no change
sleep
event arrives
run #2
change detected
importance evaluated
notification sent
state updated
```

---

# 91. End-to-End Test Scenario 3

## Approval

User:

```text
Prepare deployment.
```

Expected:

```text
inspect
test
build
prepare
STOP BEFORE DEPLOY
request approval
```

Then:

```text
approval granted
 ↓
deploy
 ↓
verify
 ↓
notify
```

Test must prove deployment does not happen before approval.

---

# 92. End-to-End Test Scenario 4

## User Away

```text
user disconnects
```

Then:

```text
event arrives
```

Expected:

```text
Nārada executes
memory updates
notification queued
```

The result should be available when the user returns.

---

# 93. End-to-End Test Scenario 5

## Provider Failure

Simulate:

```text
Sarvam unavailable
```

Expected behavior depends on configured policy:

```text
fallback to Ollama
```

or:

```text
pause and notify
```

Never silently switch to a paid provider without an explicit routing policy.

Hermes's current cron documentation highlights a useful unattended-execution safety pattern: scheduled jobs can snapshot/pin their provider/model so a later global model change does not silently cause an unattended job to use a different or paid provider. Nārada should adopt an equivalent **provider pinning / cost policy** for persistent responsibilities. citeturn0search1

---

# 94. End-to-End Test Scenario 6

## Duplicate Event

Inject the same:

```text
github.push
```

twice.

Expected:

```text
one meaningful processing event
one notification maximum
```

---

# 95. End-to-End Test Scenario 7

## Sandbox Escape Attempt

Sandbox process attempts:

```text
read /root/.ssh
```

Expected:

```text
denied
sandbox remains isolated
audit event recorded
task receives failure
```

---

# 96. End-to-End Test Scenario 8

## Tool Permission Bypass

Model requests:

```text
shell.execute("rm -rf ...")
```

Expected:

```text
permission engine intercepts
no command executed
approval required / blocked
audit event
```

---

# 97. End-to-End Test Scenario 9

## Restart Recovery

1. Start responsibility.
2. Begin task.
3. Kill container.
4. Restart.
5. Resume.

Expected:

```text
state recovered
no duplicate side effect
task continues or safely reconciles
```

---

# 98. End-to-End Test Scenario 10

## Approval During Restart

1. Request approval.
2. Persist pending approval.
3. Restart Nārada.
4. Send approval.
5. Resume task.

Expected:

```text
approval survives restart
```

---

# 99. Phase 37 — Stop Conditions for the Entire System

Nārada must stop autonomous execution when:

```text
authorization is ambiguous
+
action is consequential
```

Also stop when:

- safety boundary is unclear
- required provider is unavailable and no safe fallback exists
- task exceeds budget
- repeated failures exceed retry policy
- state is inconsistent
- verification fails
- sandbox becomes unhealthy
- approval expires
- external side effect cannot be reconciled
- model output is structurally invalid after bounded retries

A safe stop is a successful outcome.

---

# 100. Global "Never Do This" List

Never:

```text
execute arbitrary model-generated shell commands directly
```

Never:

```text
give all secrets to every tool
```

Never:

```text
mount the entire home directory into a sandbox
```

Never:

```text
give the Docker socket to an autonomous agent without a deliberate
security design
```

Never:

```text
treat "yes" from a random channel message as approval
```

Never:

```text
send external messages without checking permission
```

Never:

```text
silently switch a responsibility to an expensive provider
```

Never:

```text
retry a potentially successful financial/deployment/send action blindly
```

Never:

```text
store every conversation as permanent memory
```

Never:

```text
let scheduled jobs inherit arbitrary new capabilities without policy
```

Never:

```text
claim verification when only an LLM said something worked
```

---

# 101. Phase 38 — Provider Pinning for Unattended Work

Persistent responsibilities should have an explicit model policy.

Example:

```yaml
model_policy:
  provider: ollama
  model: qwen...
  allow_fallback: false
```

or:

```yaml
model_policy:
  provider: sarvam
  model: ...
  allow_fallback: true
  fallback:
    provider: ollama
```

This avoids unattended jobs silently changing cost or behavior.

---

# 102. Phase 39 — Toolsets

Do not expose every tool to every agent.

Define toolsets:

```text
research
coding
browser
communication
calendar
admin
```

Example:

```yaml
toolset: research
tools:
  - web.search
  - web.open
  - filesystem.read
```

Coding:

```yaml
toolset: coding
tools:
  - filesystem.read
  - filesystem.write
  - shell.execute
  - git.status
```

The permission engine still applies.

---

# 103. Scheduled Job Toolset Isolation

A scheduled responsibility should have an explicit toolset.

Example:

```text
GitHub monitoring
→ github.read
→ web.open
→ notification.send
```

It should not automatically receive:

```text
shell.execute
filesystem.write
financial actions
deployment
```

This is essential for unattended operation.

---

# 104. Phase 40 — Skill Verification

Every skill should have:

```text
SKILL.md
test fixtures
expected outputs
failure cases
tool requirements
permissions
```

A skill should be executable in a test harness without requiring a human.

Example:

```text
github-review
```

must have fixtures for:

```text
no changes
minor changes
important changes
API failure
permission denied
duplicate event
```

---

# 105. Phase 41 — Responsibility Verification

Every responsibility must have:

```text
activation test
normal run test
no-op test
failure test
recovery test
notification test
pause test
resume test
deletion test
```

A responsibility that cannot be paused safely is not ready for autonomous use.

---

# 106. Pause Semantics

Pause means:

```text
do not start new executions
```

It does not necessarily mean:

```text
kill currently executing work
```

Define separate operations:

```text
pause
cancel
stop
disable
archive
```

These should not be conflated.

---

# 107. Cancellation

Cancellation must propagate:

```text
responsibility
 ↓
task
 ↓
agent run
 ↓
tool
 ↓
sandbox
```

A canceled run should not continue in the background.

For subprocesses:

```text
terminate
 ↓
wait
 ↓
kill if required
 ↓
collect state
```

---

# 108. Phase 42 — Background Worker

Initially:

```text
narada-core
 ├── FastAPI
 ├── scheduler
 └── worker
```

The worker can run as an internal asyncio task or controlled process.

Only split into separate containers when:

```text
API availability
and
background workloads
```

conflict.

The goal is simplicity first.

---

# 109. Worker Queue

Initial:

```text
in-process queue
```

Later:

```text
Redis queue
```

Cloud:

```text
SQS or equivalent
```

Use the same conceptual job interface:

```text
enqueue
claim
run
ack
fail
retry
dead-letter
```

---

# 110. Dead-Letter Tasks

Repeatedly failing tasks should not retry forever.

After policy threshold:

```text
FAILED_PERMANENT
```

or:

```text
BLOCKED
```

Then notify according to responsibility policy.

Store:

```text
failure reason
attempt count
last error
last successful checkpoint
```

---

# 111. Phase 43 — Long-Term Memory Hygiene

Memory needs maintenance.

Potential future jobs:

```text
deduplicate memories
merge similar memories
decay stale memories
summarize episodes
detect contradictions
archive old events
```

Do not run these continuously.

Schedule low-priority maintenance.

---

# 112. Memory Contradiction Handling

If memory contains:

```text
User prefers X
```

and new evidence says:

```text
User prefers Y
```

do not blindly overwrite.

Store:

```text
old memory
new memory
source
timestamp
confidence
```

Then reconcile.

Eventually this becomes a user-visible memory system.

---

# 113. Phase 44 — User-Controlled Memory

Eventually the user should be able to:

```text
show what you remember
forget X
forget this conversation
export memory
pause memory
disable memory category
```

These actions must affect actual persistent storage.

Do not fake deletion by merely hiding results.

---

# 114. Phase 45 — Audit Explorer

The user should eventually be able to inspect:

```text
What did Nārada do yesterday?
```

and see:

```text
Responsibility
Task
Action
Tool
Permission
Approval
Result
Notification
```

This is especially important for an always-on agent.

---

# 115. Phase 46 — Security Review Gate

Before enabling autonomous external actions, run a security review.

Checklist:

```text
[ ] secrets not exposed to LLM
[ ] tool permissions enforced in runtime
[ ] approvals enforced in runtime
[ ] audit trail works
[ ] sandbox isolation works
[ ] channel identity verified
[ ] webhook signatures verified
[ ] replay protection works
[ ] provider credentials isolated
[ ] filesystem mounts restricted
[ ] Docker socket protected
[ ] network access controlled
[ ] budgets enforced
[ ] cancellation works
[ ] retries are safe
[ ] restart recovery works
```

If any critical item fails:

> **Do not enable unattended consequential actions.**

---

# 116. Phase 47 — Reliability Review Gate

Before calling Nārada autonomous:

```text
[ ] scheduler survives restart
[ ] responsibilities survive restart
[ ] approvals survive restart
[ ] events are deduplicated
[ ] tasks do not loop forever
[ ] provider failures are handled
[ ] sandbox failures are handled
[ ] notification failures are handled
[ ] task budgets work
[ ] task cancellation works
[ ] state is recoverable
[ ] important actions are auditable
```

---

# 117. Phase 48 — "Away Mode" Production Test

Run Nārada for at least a real-world soak period.

Test:

```text
user absent
provider intermittently fails
events arrive
noisy events arrive
one important event arrives
approval requested
approval delayed
container restarts
notification delivery fails
```

Expected:

```text
no runaway loops
no duplicate notifications
no unauthorized actions
no data loss
no unbounded cost
```

---

# 118. Phase 49 — Phone + Email + Messaging

At maturity, the communication architecture should look like:

```text
                         NĀRADA GATEWAY
                               │
       ┌───────────────┬───────┼───────────┬──────────────┐
       │               │       │           │              │
      Web           Telegram  Email       SMS           Phone
       │               │       │           │              │
       └───────────────┴───────┼───────────┴──────────────┘
                               │
                         Identity Router
                               │
                        Session Manager
                               │
                         Agent Runtime
```

The same responsibility can be queried from any channel.

Example:

```text
Telegram:
"How is my SIH application?"
```

then later:

```text
Email:
"Anything important overnight?"
```

then:

```text
Web:
"Show me pending approvals."
```

All refer to the same Nārada state.

---

# 119. Phase 50 — Channel Pairing

For security, external channels should be paired.

Example:

```text
Telegram
 ↓
/start
 ↓
pairing code
 ↓
user authenticates
 ↓
channel bound to Nārada account
```

Do not automatically trust arbitrary messages from unknown users.

---

# 120. Channel Approval Security

Approval requests should include:

```text
approval_id
action
target
summary
expires_at
```

An approval response must reference the exact pending approval.

Good:

```text
approve APV-83F21
```

Bad:

```text
yes
```

The UI may support natural language, but the backend should resolve it against pending approval context.

---

# 121. Phase 51 — Web Dashboard

Only after the runtime is stable.

Dashboard sections:

```text
Overview
Responsibilities
Tasks
Runs
Memory
Approvals
Tools
Skills
Channels
Events
Audit
Costs
Providers
System
```

The dashboard is a control plane.

It is not the agent.

---

# 122. Phase 52 — User Away State

Nārada should know whether:

```text
user available
user away
quiet hours
do not disturb
```

This affects delivery.

Example:

```yaml
notification_policy:
  quiet_hours:
    start: 23:00
    end: 07:00

  urgent:
    bypass_quiet_hours: true
```

The exact policy is user-controlled.

---

# 123. Quiet Hours

During quiet hours:

```text
routine → queue
important → queue/digest
urgent → notify
approval → queue unless deadline requires escalation
```

Never silently discard events.

---

# 124. Phase 53 — Batching

If 20 events arrive:

Do not necessarily run:

```text
20 LLM calls
```

Instead:

```text
events
 ↓
deduplicate
 ↓
batch
 ↓
one analysis
```

Example:

```text
10 GitHub commits
3 issues
2 PR comments
```

can become:

```text
one GitHub responsibility evaluation
```

This reduces cost and noise.

---

# 125. Phase 54 — Priority Queue

Tasks should eventually have:

```text
priority
urgency
deadline
cost
risk
responsibility
dependencies
```

Example:

```text
CRITICAL
HIGH
NORMAL
LOW
BACKGROUND
```

The scheduler/worker should prefer work based on policy rather than simple FIFO.

---

# 126. Phase 55 — Dependency Graph

Complex responsibilities may contain:

```text
Task A
 ↓
Task B
 ├── Task C
 └── Task D
       ↓
     Task E
```

Do not implement arbitrary DAG scheduling in BASE.

Introduce it when multi-step responsibilities need it.

---

# 127. Phase 56 — Long-Running Projects

Nārada should eventually support:

```text
Project
 ↓
Responsibility
 ↓
Goals
 ↓
Tasks
 ↓
Milestones
```

Example:

```text
Nārada Project
├── architecture
├── backend
├── memory
├── voice
├── AWS
└── documentation
```

The user can ask:

```text
"How is the project going?"
```

and Nārada can answer from structured state.

---

# 128. Phase 57 — Project Status Prompt

```text
Summarize project state.

Include:
- current goals,
- completed milestones,
- active tasks,
- blocked tasks,
- failures,
- upcoming deadlines,
- user decisions required.

Do not infer completion from lack of recent errors.
Use explicit task state and evidence.
```

---

# 129. Phase 58 — External Service Health

Nārada should know when providers are unavailable.

Maintain:

```text
provider health
last successful call
last failure
failure count
backoff state
```

Avoid hammering an unavailable service.

---

# 130. Phase 59 — Provider Circuit Breaker

For repeated failures:

```text
CLOSED
 ↓ failures
OPEN
 ↓ cooldown
HALF_OPEN
 ↓ success
CLOSED
```

This prevents autonomous responsibilities from generating runaway API traffic.

---

# 131. Phase 60 — Cost Safety

Every unattended responsibility should eventually have:

```text
provider policy
model policy
budget
tool budget
runtime budget
notification policy
```

Example:

```yaml
autonomy:
  max_runtime: 5m
  max_model_calls: 5
  max_tool_calls: 15
  max_estimated_cost: 0.25
```

If exceeded:

```text
pause
audit
notify
```

---

# 132. Phase 61 — Final Local Deployment

The desired simple local installation is:

```bash
git clone ...
cd narada
cp .env.example .env
docker compose up -d
```

Then:

```bash
narada status
```

or:

```text
http://localhost:...
```

The user should be able to configure:

```text
Sarvam API
Ollama
Telegram
Email
GitHub
optional Qdrant
```

without rebuilding the core image.

---

# 133. Final Compose Philosophy

Default:

```text
narada-core
```

Optional:

```text
qdrant
redis
```

External:

```text
Ollama
Sarvam
ElevenLabs
GitHub
Telegram
Email
etc.
```

Ephemeral:

```text
sandbox containers
```

This keeps the local system understandable.

---

# 134. Recommended Docker Compose Shape

Conceptual only:

```yaml
services:

  narada:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile
    env_file:
      - .env
    volumes:
      - ./data:/data
      - ./workspaces:/workspaces
    ports:
      - "8000:8000"
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant
    profiles:
      - memory
    volumes:
      - ./data/qdrant:/qdrant/storage

  redis:
    image: redis:alpine
    profiles:
      - queue
```

This is intentionally illustrative.

Do not enable Qdrant/Redis by default until required.

---

# 135. Core Container Health

Health endpoint should report:

```text
database
scheduler
worker
provider configuration
event system
channel configuration
```

Example:

```json
{
  "status": "healthy",
  "database": "ok",
  "scheduler": "running",
  "worker": "running",
  "llm": "configured",
  "channels": ["telegram"],
  "qdrant": "disabled"
}
```

Do not mark the whole system unhealthy merely because an optional provider is not configured.

---

# 136. Phase 62 — Acceptance Test: The Real Nārada Demo

The strongest early acceptance test is:

> "Nārada, watch my GitHub project and tell me when something important changes."

System must:

```text
parse request
 ↓
create responsibility
 ↓
ask for missing permissions if needed
 ↓
configure schedule
 ↓
save responsibility
 ↓
sleep
```

Then:

```text
GitHub event
 ↓
gateway
 ↓
event persisted
 ↓
responsibility matched
 ↓
fresh agent run
 ↓
inspect changes
 ↓
compare with previous state
 ↓
determine importance
 ↓
memory update
 ↓
notify user
 ↓
audit
 ↓
sleep
```

This is the first true autonomous-agent proof.

---

# 137. Acceptance Test: User Returns

After being away, user asks:

```text
"What happened while I was away?"
```

Nārada should answer from:

```text
events
responsibilities
runs
memory
notifications
approvals
failures
```

It should not need to reconstruct everything from raw conversation history.

---

# 138. Acceptance Test: User Changes Channel

User starts on:

```text
Web
```

then asks through:

```text
Telegram
```

Expected:

```text
same user
same responsibilities
same memory
same pending approvals
```

---

# 139. Acceptance Test: User Goes Offline

If the user is unreachable:

```text
Nārada continues safe work
```

If notification fails:

```text
notification failure
 ↓
persist pending delivery
 ↓
retry according to policy
```

Do not lose the event.

---

# 140. Acceptance Test: User Disables a Responsibility

User:

```text
Stop watching the GitHub project.
```

Expected:

```text
responsibility status = PAUSED/DISABLED
scheduler no longer wakes it
incoming matching events do not execute it
historical state remains
```

---

# 141. Acceptance Test: User Deletes Responsibility

If deletion is supported:

```text
active responsibility
 ↓
delete request
 ↓
confirmation if needed
 ↓
disable future execution
 ↓
preserve audit according to retention policy
 ↓
delete/retain memory according to user policy
```

Do not confuse deleting a responsibility with deleting all associated memory.

---

# 142. Phase 63 — Production Readiness Gate

Do not call Nārada "autonomous" until all of the following pass.

## Agent

```text
[ ] planning works
[ ] execution works
[ ] observation works
[ ] verification works
[ ] completion works
[ ] bounded retries work
```

## Memory

```text
[ ] durable
[ ] searchable
[ ] selective
[ ] restart-safe
[ ] user-controlled
```

## Tools

```text
[ ] registry
[ ] schemas
[ ] permissions
[ ] audit
[ ] failures
```

## Autonomy

```text
[ ] schedules
[ ] events
[ ] wake/sleep
[ ] responsibilities
[ ] notifications
[ ] recovery
```

## Safety

```text
[ ] approval gates
[ ] sandboxing
[ ] secret isolation
[ ] budgets
[ ] cancellation
[ ] identity
```

## Communication

```text
[ ] web
[ ] at least one remote messaging channel
[ ] email or equivalent
[ ] pending delivery
[ ] channel identity
```

## Operations

```text
[ ] restart recovery
[ ] health checks
[ ] logs
[ ] audit
[ ] provider health
[ ] cost controls
```

---

# 143. What "Hermes-like" Should Mean for Nārada

Do not copy Hermes feature-for-feature.

Use the architectural lessons:

```text
Hermes-like property             Nārada equivalent
---------------------------------------------------------------
Gateway                          Nārada Gateway
Cron                             Responsibility Scheduler
Skills                           Nārada Skills
Toolsets                         Permissioned Toolsets
MCP                              MCP Tool Layer
Subagents                        Specialist Agents
Sandboxes                        Nārada Sandbox Runtime
Channels                         Channel Gateway
Persistent state                 Responsibility + Memory
Unattended execution             Away Mode
Delivery                         Notification Gateway
Web/browser                      Research/Browser tools
Provider gateway                 Model/Provider Gateway
Dashboard                        Nārada Control Plane
```

Hermes currently also supports multiple terminal backends and configurable container isolation, including per-session Docker sandboxes. That is a useful reference for Nārada's later sandbox design. citeturn0search3

The Nārada implementation should remain simpler at first.

---

# 144. The Nārada Difference

Nārada should not merely be:

```text
chatbot
+
tools
+
cron
```

It should center on:

```text
RESPONSIBILITY
```

That gives the architecture its own identity.

```text
User:
"Keep this project moving."

Nārada:
"What does success mean?"

User:
"Ship the next release."

Nārada:
"Understood."

         ↓

Responsibility
         ↓
Goals
         ↓
Milestones
         ↓
Tasks
         ↓
Events
         ↓
Tools
         ↓
Memory
         ↓
Verification
         ↓
User updates
```

---

# 145. Final Architecture

The mature local Nārada should look approximately like:

```text
                              USER
                               │
            ┌──────────────────┼───────────────────┐
            │                  │                   │
           WEB              PHONE               MESSAGING
            │                  │                   │
            └──────────────────┼───────────────────┘
                               │
                        CHANNEL GATEWAY
                               │
                         IDENTITY ROUTER
                               │
                         SESSION MANAGER
                               │
                     ┌─────────▼─────────┐
                     │   NĀRADA CORE     │
                     │                   │
                     │ Responsibility    │
                     │ Goal              │
                     │ Planner           │
                     │ Executor          │
                     │ Observer          │
                     │ Verifier          │
                     │ Memory            │
                     │ Scheduler         │
                     │ Events            │
                     │ Approvals        │
                     │ Permissions       │
                     │ Audit             │
                     └───────┬───────────┘
                             │
             ┌───────────────┼────────────────┐
             │               │                │
           TOOLS          PROVIDERS        SANDBOX
             │               │                │
           MCP           Sarvam             Docker
         Browser         Ollama             OpenHands
         GitHub          ElevenLabs         Browser
         Files           APIs               Coding
             │               │                │
             └───────────────┼────────────────┘
                             │
                     PERSISTENT STATE
                             │
                  ┌──────────┴──────────┐
                  │                     │
               SQLite                Qdrant
             canonical state       optional vectors
```

---

# 146. The Core Loop in Its Final Form

Everything eventually reduces to:

```text
                    RESPONSIBILITY
                          │
                          ▼
                         GOAL
                          │
                          ▼
                         PLAN
                          │
                          ▼
                      TASK QUEUE
                          │
                          ▼
                       EXECUTE
                          │
                ┌─────────┴─────────┐
                │                   │
              TOOL                AGENT
                │                   │
                └─────────┬─────────┘
                          ▼
                      OBSERVATION
                          │
                          ▼
                        VERIFY
                          │
                    ┌─────┴─────┐
                    │           │
                 FAILED       SUCCESS
                    │           │
                 RECOVER        │
                    │           │
                    └─────┬─────┘
                          ▼
                        MEMORY
                          │
                          ▼
                       DECISION
                          │
              ┌───────────┼───────────┐
              │           │           │
           CONTINUE     WAIT        COMPLETE
              │           │           │
              ▼           ▼           ▼
            PLAN        EVENT        DELIVER
              │                       │
              └───────────────┬───────┘
                              ▼
                            SLEEP
```

---

# 147. The Three Most Important Rules

If an AI coding agent remembers only three things, they are:

## Rule 1

> **The LLM proposes. The runtime decides.**

Never let model output bypass:

```text
permissions
approvals
budgets
verification
audit
```

## Rule 2

> **The user gives Nārada responsibilities, not just prompts.**

Build persistent state around:

```text
responsibilities
goals
tasks
events
memory
```

## Rule 3

> **Do not build the bricks. Build the temple.**

Use:

```text
Sarvam
Ollama
MCP
LangGraph
Playwright
OpenHands
Docker
Qdrant
APScheduler
Redis
external APIs
```

where they are actually useful.

Nārada owns the orchestration and responsibility model.

---

# 148. Final Build Sequence

The recommended actual sequence is:

```text
PHASE 0   Architecture boundaries
    ↓
PHASE 1   One Docker core container
    ↓
PHASE 2   Provider gateway
    ↓
PHASE 3   Agent loop
    ↓
PHASE 4   SQLite memory
    ↓
PHASE 5   Tool registry
    ↓
PHASE 6   Permissions + approvals
    ↓
PHASE 7   MCP
    ↓
PHASE 8   Web/browser research
    ↓
PHASE 9   Skills
    ↓
PHASE 10  Scheduler
    ↓
PHASE 11  Responsibilities
    ↓
PHASE 12  Events
    ↓
PHASE 13  Notifications/channels
    ↓
PHASE 14  Away mode
    ↓
PHASE 15  Sandboxes
    ↓
PHASE 16  Coding specialist
    ↓
PHASE 17  Specialist agents
    ↓
PHASE 18  Recovery
    ↓
PHASE 19  Model routing
    ↓
PHASE 20  Multi-channel identity
    ↓
PHASE 21  Qdrant if justified
    ↓
PHASE 22  Redis if justified
    ↓
PHASE 23  PostgreSQL if justified
    ↓
PHASE 24  Hybrid AWS
    ↓
PHASE 25  Cloud / scale-to-zero
    ↓
PHASE 26  Control plane
```

Do not skip directly from:

```text
chatbot
```

to:

```text
multi-agent cloud platform
```

The agent loop must earn every layer.

---

# 149. Ultimate Acceptance Test

Nārada is beginning to fulfill its purpose when this works:

The user says:

> **"Keep an eye on my project while I'm away. If something important happens, investigate it, handle anything you're authorized to handle, ask me before consequential actions, and tell me what happened when I come back."**

Nārada should be able to transform that into:

```text
RESPONSIBILITY
     │
     ├── Goal
     ├── Monitoring policy
     ├── Schedule/events
     ├── Tools
     ├── Permissions
     ├── Notification policy
     ├── Memory
     └── Budget
              │
              ▼
            SLEEP
              │
              ▼
            EVENT
              │
              ▼
            WAKE
              │
              ▼
           INVESTIGATE
              │
              ▼
          TAKE SAFE ACTION
              │
              ▼
        REQUEST APPROVAL
         when required
              │
              ▼
           VERIFY
              │
              ▼
           REMEMBER
              │
              ▼
           NOTIFY
              │
              ▼
            SLEEP
```

That is the point where Nārada stops being "an LLM application" and becomes:

> **a personal digital operator that has responsibilities.**

---

# 150. Final Engineering Motto

```text
Don't build the bricks.

Build the temple.

But build the temple one verified brick at a time.
```
