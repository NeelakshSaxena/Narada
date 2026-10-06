![Nārada Banner](public/NARADA_BANNER.png)

# NĀRADA

> **A personal autonomous agent runtime.**

**Give Nārada a responsibility, and it figures out how to keep that responsibility moving.**

Nārada is a local-first autonomous agent runtime designed to move beyond the traditional chatbot model.

A normal chatbot follows:

```text
USER → MESSAGE → LLM → ANSWER
```

Nārada is designed around:

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
EXECUTION
  ↓
OBSERVATION
  ↓
MEMORY
  ↓
RE-EVALUATION
  ↓
NEXT ACTION
```

The goal is not to build another chat interface. The goal is to build a system that can **own ongoing responsibilities**, act through tools, remember relevant state, wake up when something matters, ask for approval when necessary, and continue working while the user is away.

---

## Philosophy

### Don't build the bricks. Build the temple.

Nārada is intentionally designed as a **Lego-block system**.

Where mature technologies already exist, Nārada should integrate them rather than reinvent them.

Examples include:

- LLM providers
- Ollama
- MCP
- LangGraph
- Playwright
- OpenHands
- FastAPI
- SQLite
- Qdrant / pgvector
- Docker
- APScheduler
- AWS services
- voice providers
- communication channels

Every major subsystem should have a clear boundary so that it can be replaced without rewriting the entire runtime.

---

# Project Status

Nārada is being built incrementally.

The project is organized into phases rather than one large implementation.

| Era | Focus |
|---|---|
| Era I — Messenger | Talk, Act, Remember |
| Era II — Agent | Responsibilities, Planning, Execution, Monitoring |
| Era III — Operator | Voice, Specialists, Computer Operation |
| Era IV — Network | Local, Hybrid, Cloud, Services |

The initial priority is the **agent loop**, not the UI.

> **Prove that Nārada can reason, act, observe, remember, and continue before building a sophisticated interface around it.**

---

# Core Architecture

The intended local architecture is deliberately simple at first:

```text
                         NĀRADA
                    ┌───────────────┐
                    │ Docker        │
                    │ Core          │
                    │               │
                    │ FastAPI       │
                    │ Agent Runtime │
                    │ Worker        │
                    │ Scheduler     │
                    │ Gateway       │
                    │ Memory        │
                    │ Tool Registry │
                    │ Permissions   │
                    │ Approvals     │
                    │ Audit         │
                    └───────┬───────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
          Ollama       External APIs    Optional
          (host)       Sarvam/etc.     Services
                                           │
                                      Qdrant/Redis
```

The core backend should initially remain in **one main Docker container**.

Additional containers are introduced only when they provide a meaningful isolation, infrastructure, or runtime boundary.

SQLite is treated as a mounted database file rather than as a separate service.

---

# Local / Hybrid / Cloud

Nārada is designed to support three operating modes.

### Local

```text
Laptop
 ├── Nārada
 ├── Ollama
 ├── SQLite
 ├── Docker
 └── local tools
```

Private computation and state remain local.

### Hybrid

```text
AWS
 ├── API
 ├── scheduler
 └── lightweight state/services
          │
          ▼
Local machine
 ├── Nārada runtime
 ├── Ollama
 └── private tools
```

### Cloud

```text
AWS
 ├── API
 ├── workers
 ├── scheduler
 ├── database
 ├── storage
 └── external model provider
```

The agent logic should remain independent of the deployment environment.

---

# Technology Stack

The current planned Lego stack is:

| Layer | Technology | Purpose |
|---|---|---|
| Primary LLM | Sarvam-105B | Reasoning |
| Local LLM | Ollama | Local/private inference |
| STT | Saaras v4 | Speech → text |
| TTS | Bulbul v3 | Text → speech |
| Voice pipeline | Pipecat | Realtime voice |
| Agent orchestration | LangGraph | Stateful workflows |
| Tool interface | MCP | Tool interoperability |
| Browser | Playwright | Web interaction |
| Coding specialist | OpenHands | Autonomous coding |
| API | FastAPI | Backend API |
| Database | SQLite → PostgreSQL | Persistent state |
| Vector memory | pgvector / Qdrant | Semantic retrieval |
| Events | Redis when justified | Event/queue layer |
| Scheduler | APScheduler → EventBridge | Scheduled work |
| Local deployment | Docker Compose | Reproducible environment |
| Cloud | AWS | Optional deployment |

These are replaceable components, not permanent dependencies of the core architecture.

---

# Agent Loop

The fundamental Nārada loop is:

```text
GOAL
 ↓
PLAN
 ↓
ACTION
 ↓
OBSERVATION
 ↓
MEMORY
 ↓
DECISION
 ↓
ACTION
 ↓
...
 ↓
COMPLETE / CONTINUE / WAIT / ASK
```

A responsibility may therefore continue across multiple executions.

For example:

```text
"Keep an eye on my SIH submission."
```

Nārada may create a persistent responsibility:

```yaml
responsibility:
  name: SIH Submission

goal:
  monitor_submission_status: true

checks:
  - SIH portal
  - email
  - relevant notifications

frequency:
  6h

actions:
  - notify_user
  - summarize_changes

permissions:
  submit: false
  modify_submission: false
```

The important distinction is:

> **A task is something Nārada does. A responsibility is something Nārada owns over time.**

---

# Capability ≠ Permission

Nārada must never confuse the ability to perform an action with permission to perform it.

Every meaningful action should be evaluated using:

```text
CAPABILITY
PERMISSION
RISK
APPROVAL
AUDIT
```

Example:

```json
{
  "name": "filesystem.read",
  "risk": "low",
  "requires_confirmation": false
}
```

Higher-risk actions may require approval:

```json
{
  "name": "shell.execute",
  "risk": "high",
  "requires_confirmation": true
}
```

Examples of actions that may require explicit approval:

- sending messages
- deleting data
- financial actions
- account changes
- deployments
- destructive shell commands
- publishing content

---

# Memory

Nārada separates memory by purpose.

### Working memory

Current task state, plan, observations, and tool calls.

### Episodic memory

What happened during previous executions.

### Semantic memory

Stable knowledge that may be useful later.

### Responsibility memory

Persistent information about ongoing responsibilities.

The system should **not** blindly dump every conversation into permanent memory.

The initial storage strategy is intentionally simple:

```text
SQLite
  ↓
FTS / structured retrieval
  ↓
Later:
PostgreSQL + pgvector / Qdrant when justified
```

---

# Events

Nārada should not continuously run an LLM just to discover that nothing happened.

Instead:

```text
EVENT
  ↓
Should I care?
  ├── NO → ignore / sleep
  │
  └── YES
        ↓
      WAKE
        ↓
      REASON
        ↓
      ACT
        ↓
      OBSERVE
        ↓
      SLEEP / CONTINUE
```

Potential events include:

- user messages
- timers
- email received
- file changes
- GitHub events
- webhooks
- calendar events
- tool results
- task completion
- system alerts

---

# Tools

Nārada uses a tool abstraction instead of hard-coding every integration into the agent.

Potential capabilities include:

```text
web.search
web.open
filesystem.read
filesystem.write
shell.execute
git.status
git.commit
docker.ps
docker.logs
calendar.read
email.read
notification.send
```

MCP is intended to provide a universal interface wherever appropriate.

Existing MCP servers should be preferred over custom integrations when they satisfy the requirement.

---

# Browser and Coding

Nārada is the coordinator.

Specialist systems do specialist work.

For example:

```text
NĀRADA
   │
   ├── Researcher
   ├── Browser Agent
   ├── Document Agent
   ├── Data Agent
   └── Coder
             │
             └── OpenHands
```

Nārada should decide:

- whether delegation is necessary
- which specialist is appropriate
- what permissions it receives
- what execution budget it has
- how its result is verified

---

# Away Mode

A major goal of Nārada is that it should continue useful work while the user is away.

The intended pattern is:

```text
USER ASSIGNS RESPONSIBILITY
          ↓
      NĀRADA STORES IT
          ↓
       SCHEDULE / EVENT
          ↓
       USER LEAVES
          ↓
       NĀRADA WAKES
          ↓
       CHECKS STATE
          ↓
       REASONS
          ↓
        ACTS
          ↓
       OBSERVES
          ↓
    NEEDS USER INPUT?
       /          \
     NO            YES
     ↓              ↓
  CONTINUE       REQUEST
                  APPROVAL
                    ↓
                WAIT / RESUME
```

This requires persistent state, scheduled execution, notifications, approvals, recovery, and auditability.

---

# Security Principles

Nārada is intended to become increasingly autonomous without becoming blindly permissive.

Core rules include:

1. **Capability does not imply permission.**
2. High-risk actions require approval unless explicitly authorized by policy.
3. Every consequential action should be auditable.
4. Autonomous execution must have bounded budgets.
5. Sandboxes must isolate risky execution.
6. Secrets must not be exposed unnecessarily to tools or models.
7. Prompt injection must be treated as an untrusted-input problem.
8. Docker socket access is privileged access.
9. Destructive operations require stronger controls than read operations.
10. Restarting Nārada must not accidentally duplicate consequential actions.

---

# Repository Structure

The intended repository structure is:

```text
narada/
├── apps/
│   ├── api/
│   └── web/
│
├── core/
│   ├── agent/
│   │   ├── loop.py
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── observer.py
│   │   └── state.py
│   │
│   ├── memory/
│   │   ├── working.py
│   │   ├── episodic.py
│   │   ├── semantic.py
│   │   └── store.py
│   │
│   ├── tools/
│   │   ├── registry.py
│   │   ├── permissions.py
│   │   └── base.py
│   │
│   ├── events/
│   │   ├── bus.py
│   │   └── handlers.py
│   │
│   ├── scheduler/
│   │   └── scheduler.py
│   │
│   └── llm/
│       ├── base.py
│       ├── ollama.py
│       └── remote.py
│
├── providers/
│   ├── llm/
│   │   ├── sarvam.py
│   │   └── ollama.py
│   │
│   └── voice/
│       ├── saaras.py
│       └── bulbul.py
│
├── agent/
│   └── graph.py
│
├── tools/
│   └── mcp.py
│
├── plugins/
│   ├── filesystem/
│   ├── web/
│   ├── shell/
│   ├── git/
│   └── notifications/
│
├── memory/
├── storage/
│
├── infra/
│   ├── docker/
│   └── aws/
│
├── tests/
├── docs/
├── scripts/
│
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

---

# Development Method

Nārada is built **phase by phase**.

Each phase has:

- a defined objective
- explicit exit criteria
- a dedicated Git branch
- a phase logbook
- deterministic tests where possible
- verification conditions
- stop conditions
- a completion summary

## Branching rule

Every phase gets its own dedicated branch.

Example:

```text
main
  │
  └── phase/01-foundation
          │
          └── implementation
                 │
                 └── verification
                        │
                        └── pull request
                               │
                               └── merge
                                      ↓
                                     main
                                      │
                                      └── phase/02-config
```

No phase should casually develop directly on `main`.

---

# Cross-Phase Changes

A later phase **is allowed to modify code originally created in an earlier phase**.

This is intentional.

For example:

```text
Phase 1
  └── creates core/config.py

Phase 5
  └── discovers that config.py must change
       ↓
    modify it on:
    phase/05-<name>
```

The later phase does **not** need to create a separate Phase 1 branch just because the file originated there.

However, the phase logbook must record:

- what earlier code was changed
- why it needed changing
- which earlier phase created it
- what behavior changed
- what regression risk exists
- which tests verify the change

The rule is:

> **Later phases may evolve earlier code, but never silently.**

---

# Phase Completion

A phase is not complete merely because the code runs.

The required lifecycle is:

```text
START PHASE
    ↓
CREATE PHASE LOGBOOK
    ↓
IMPLEMENT
    ↓
LOG WORK
    ↓
TEST
    ↓
ERROR?
 ┌──YES───────────────┐
 ↓                    │
LOG ERROR             │
 ↓                    │
FIX                   │
 ↓                    │
VERIFY                │
 ↓                    │
LOG FIX ──────────────┘
    ↓
COMPLETE EXIT CRITERIA
    ↓
UPDATE DOCUMENTATION
    ↓
PRE-MERGE CHECK
    ↓
PULL REQUEST
    ↓
REVIEW
    ↓
MERGE
    ↓
POST-MERGE VERIFICATION
    ↓
PHASE COMPLETE
    ↓
CREATE NEXT PHASE BRANCH
```

Every successful phase must update the relevant:

- phase logbook
- roadmap/status
- architecture documentation
- README sections where necessary
- configuration/API documentation where necessary
- known limitations
- test documentation where necessary

---

# GitHub Merge Gate

Before merging a phase branch, verify:

- [ ] Phase objective is satisfied.
- [ ] All exit criteria pass.
- [ ] Tests pass.
- [ ] Regression tests pass.
- [ ] Relevant integration tests pass.
- [ ] No unexplained changes remain.
- [ ] Cross-phase changes are documented.
- [ ] Security implications were reviewed.
- [ ] Permissions were reviewed.
- [ ] Secrets are not committed.
- [ ] Restart/recovery behavior is verified where relevant.
- [ ] Phase logbook is complete.
- [ ] Phase completion summary is appended.
- [ ] Documentation is updated.
- [ ] PR description explains the implementation.
- [ ] CI passes.
- [ ] Review comments are resolved.
- [ ] No blocking issues remain.
- [ ] Merge authorization has been obtained.

> **Green CI is not the same thing as permission to merge.**

After merging, the merged `main` state must be verified again before the phase is officially marked complete.

---

# Roadmap

## BASE — Foundation

Build the minimum working Nārada:

- Python
- FastAPI
- Docker Compose
- Sarvam provider
- SQLite
- simple CLI
- configuration
- logging
- provider interfaces
- Ollama adapter

Deliverable:

> A locally running Nārada API that can converse through a replaceable LLM provider.

---

## V1 — Can Act

Add:

- tool abstraction
- MCP
- tool registry
- permissions
- approvals
- filesystem tools
- web tools
- Playwright
- basic shell
- LangGraph
- audit log

Deliverable:

> Nārada can reason and use external tools safely.

---

## V2 — Remembers

Add:

- conversation persistence
- working memory
- episodic memory
- semantic memory
- retrieval
- user preferences
- task history
- optional PostgreSQL
- optional Qdrant / pgvector

Deliverable:

> Nārada can retain and retrieve useful context.

---

## V3 — Takes Responsibility

Add:

- tasks
- goals
- responsibilities
- schedules
- triggers
- notifications
- persistent agent state

Deliverable:

> The user can assign something to Nārada instead of repeatedly asking it to do the same thing.

---

## V4 — Autonomous

Add:

- event bus
- workers
- wake/sleep
- retries
- failure recovery
- checkpoints
- task prioritization
- approval gates
- autonomous monitoring

Deliverable:

> Nārada can wake, investigate, act, and sleep.

---

## V5 — Voice

Add:

```text
MIC
 ↓
SAARAS
 ↓
NĀRADA
 ↓
SARVAM
 ↓
BULBUL
 ↓
SPEAKER
```

Potential components:

- Saaras
- Bulbul
- Pipecat
- streaming
- barge-in
- voice activation

Voice is an interface layer, not the core intelligence.

---

## V6 — Specialist Agents

Add specialist interfaces and delegation:

- researcher
- coder
- browser agent
- document agent
- data agent
- OpenHands integration
- specialist permissions
- result verification

---

## V7 — Computer Agent

Expand Nārada's operating environment:

- browser
- terminal
- filesystem
- coding workspace
- computer-use environments
- screenshots/state observation
- isolated sandboxes

High-risk operations remain behind approval gates.

---

## V8 — Hybrid

Support:

```text
LOCAL
  ↕
HYBRID
  ↕
CLOUD
```

The same core agent architecture should operate across deployment modes.

---

## V9 — Cloud

Potential AWS components include:

- API
- workers
- EventBridge
- SQS
- PostgreSQL
- S3
- secrets management
- monitoring
- cost controls

AWS services should be introduced only where they solve a real requirement.

---

## V10 — Platform

Long-term control plane:

- responsibilities
- tasks
- memory
- agents
- approvals
- activity
- audit logs
- MCP management
- plugin management
- model routing
- cost tracking
- workspaces

---

# Project Rules

The authoritative engineering rules are maintained separately.

Important documents:

- `NARADA_MASTER_RULES.md` — authoritative project rules
- `NARADA_DETAILED_AGENTIC_BUILD.md` — detailed phased implementation plan
- `NARADA_GITHUB_RULES.md` — Git/GitHub workflow
- `NARADA_PHASE_PRE_MERGE_CHECKLIST.md` — pre-merge verification

These documents define how Nārada is to be built, verified, documented, and merged.

---

# Guiding Principles

### 1. Don't build the bricks. Build the temple.

Prefer mature components and stable interfaces.

### 2. Capability ≠ permission.

An agent having a tool does not mean it may use it without authorization.

### 3. The LLM proposes. The runtime decides.

Policies, permissions, budgets, approvals, and execution boundaries belong outside the model.

### 4. Responsibilities outlive conversations.

A responsibility must have persistent state independent of a single chat session.

### 5. Events wake the agent.

Nārada should not burn compute continuously when nothing has changed.

### 6. Everything consequential should be auditable.

Actions, approvals, failures, retries, and important state transitions should leave a trail.

### 7. Every major component should be replaceable.

Nārada should not become permanently coupled to one provider or infrastructure service.

### 8. Start simple.

Do not introduce distributed infrastructure merely because it might eventually be useful.

### 9. Security is part of the architecture.

Sandboxing, permissions, secrets, approvals, and auditability are not afterthoughts.

### 10. Build the agent loop first.

The interface is secondary.

---

# The Vision

Nārada should eventually feel less like:

> "Ask me a question."

and more like:

> "Give me a responsibility."

You should be able to leave Nārada with something important and come back later asking:

```text
"What happened while I was away?"
```

And Nārada should be able to answer from actual execution history:

```text
I checked the project three times.

At 10:00:
No changes.

At 16:00:
A dependency update appeared.

I investigated it, ran the tests, and found no regression.

There is one decision that requires your approval:
...

Nothing else needs your attention.
```

That is the system Nārada is being built to become.

---

# License

License information has not yet been defined.

---

# Status

**Early development.**

- **Phase 0 (Architecture Freeze):** Completed. Initial architectural boundaries, core interfaces, and configurations have been defined.
- **Phase 1 (NĀRADA CORE Container):** Completed. Backend FastAPI container stubbed with persistence layer attached.
- **Phase 2 (Configuration and Provider Gateway):** Completed. Provider abstraction layer (Sarvam, Ollama, Fake) implemented with strict type normalization.
- **Phase 3 (First Agent Loop):** Completed. Stateful agent runtime loop developed featuring deterministic planning and execution boundaries.
- **Phase 4 (Memory Foundation):** Skipped/Pending.
- **Phase 5 (Tool Registry):** Completed. Rigorous tool execution lifecycle and metadata bounds established.
- **Phase 6 (Permissions Engine):** Completed. Architectural safety guarantees implemented; high-risk actions require explicit human backend approval.
- **Phase 7 (MCP):** Completed. External Model Context Protocol tools safely bridged behind Nārada's authoritative permission gate.
- **Phase 8 (Browser and Web Research):** Completed. Agentic web research pipeline established with infinite-loop prevention and structured fact extraction.
- **Phase 9 (Skills System):** Completed. Reusable procedural workflows established to prevent workflow hallucination.
- **Phase 10 (Scheduled Responsibilities):** Completed. Background in-process scheduler and self-contained execution model implemented.
- **Phase 11 (Responsibility Engine):** Completed. Lifecycle state machine, priority rules, and execution memory bounds established.
- **Phase 12 (Event-Driven Wakeups):** Completed. Autonomous reactive event pipeline with LLM relevance filtering implemented.
- **Phase 13 (Notification Gateway):** Completed. Multi-channel delivery gateway built to separate work execution from message delivery.
- **Phase 14 (Away-Mode Notification Policy):** Completed. Spam-prevention policies and event deduplication engine implemented.
- **Phase 15 (Sandbox Runtime):** Completed. Ephemeral execution boundary and sandbox manager implemented.
- **Phase 16 (Coding Agent):** Completed. Coding Specialist workflow with sandbox integration and secure verification prompt implemented.
- **Phase 17 (Specialist Agents):** Completed. Specialist architecture and strict Delegation Contract implemented.
- **Phase 18 (Autonomous Recovery):** Completed. Recovery Matrix, failure handling, and idempotency checks implemented.
- **Phase 19 (Approval While User Is Away):** Completed. Asynchronous approval request system with safe state transitions and expirations built.
- **Phase 20 (Session Model):** Completed. Distinct entities for Session/Run/Conversation defined, and Context Budget Policy implemented.
- **Phase 21 (Model Routing):** Completed. Dynamic model router evaluating privacy, cost, and latency built.
- **Phase 22 (Channel Gateway):** Completed. `ChannelProvider` abstraction and Capability Matrix implemented.
- **Phase 23 (Webhook Gateway):** Completed. Secure webhook receiver with signature, timestamp, and replay validation implemented.
- **Phase 24 ("Nārada While I Sleep"):** Completed. Core overnight autonomy loop (sleep/wake/reason/act) engineered.
- **Phase 25 (Daily Digest):** Completed. Structured state daily briefing generator implemented.
- **Phase 26 (Skills + Responsibilities + Channels):** Completed. End-to-end core event flow (User → Responsibility → Agent → Delivery) fully integrated.
- **Phase 27 (Qdrant / Semantic Memory):** Completed. Vector Memory Architecture implemented with graceful FTS fallback.
- **Phase 28 (PostgreSQL):** Completed. Canonical state abstraction migrated to PostgreSQL with preserved domain integrity.
- **Phase 29 (Redis):** Completed. Redis event bus and distributed locking coordinator implemented for multi-worker support.
- **Phase 30 (Cloud / Hybrid):** Completed. Local Gateway Security boundary implemented for safe cloud-to-local communication.
- **Phase 31 (Ollama LLM Provider Integration):** Completed. HTTP-backed Ollama provider implemented with native tool-calling support.
- **Phase 32 (FastAPI Server Core):** Completed. Core FastAPI application bootstrapped with OpenAI-compatible endpoint schema.
- **Phase 33 (CLI Entrypoint):** Completed. Python CLI interface built to manage daemon lifecycles and interact natively.
- **Phase 34 (Open WebUI Compatibility):** Completed. Chat endpoint configured to bridge Open WebUI clients directly into the Agent Execution flow.
