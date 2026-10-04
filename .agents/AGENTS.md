# AGENTS.md — NĀRADA Engineering Guide

> **NĀRADA — A local-first, autonomous personal agent runtime built by composing mature open-source components and replaceable service providers.**
>
> **Working motto:** Don't build the bricks. Build the temple.

This document is the operating guide for AI coding agents and human contributors working on Nārada. It is derived from the project source of truth and turns its architecture, roadmap, safety model, and Lego-block philosophy into implementation rules. fileciteturn1file0L53-L84

---

## 1. Mission

Nārada is **not another ChatGPT clone**. Its central product idea is:

> **Give Nārada a responsibility, and it figures out how to keep that responsibility moving.**

The fundamental loop is:

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

The first technical milestone is therefore the **agent loop**, not the UI: Nārada must be able to receive a goal, plan, use a tool, observe the result, update memory, and decide whether another action is required. fileciteturn1file0L1154-L1182

---

## 2. Core Principles

### 2.1 Local first

Nārada must work locally without AWS. AWS is an optional execution/deployment environment, not a prerequisite. The same agent code should eventually run in local, hybrid, and cloud modes. fileciteturn1file0L140-L168

### 2.2 Provider agnostic

Core agent code must not care where intelligence comes from. Use provider interfaces such as:

```python
class LLMProvider:
    async def generate(...): ...
    async def stream(...): ...
    async def tool_call(...): ...
```

Potential implementations include Sarvam and Ollama; other providers can be added without rewriting the core. fileciteturn1file0L298-L332

### 2.3 Lego, not monolith

Use mature components for LLMs, STT, TTS, realtime voice, orchestration, MCP, browser automation, coding agents, databases, queues, schedulers, containers, authentication, and cloud infrastructure. Nārada should own the glue: identity, responsibility, orchestration, permissions, memory policy, approvals, routing, auditability, runtime selection, and UX. fileciteturn1file0L336-L348

### 2.4 Capability ≠ permission

This is foundational. A tool being available does not mean Nārada may use it. Meaningful actions must be evaluated through:

```text
CAPABILITY
PERMISSION
RISK
APPROVAL
AUDIT LOG
```

For example, `shell.execute` may exist as a capability while still being denied until explicit approval is granted. fileciteturn1file0L637-L664

### 2.5 Human approval for consequential actions

Actions such as sending messages, deleting data, financial actions, account changes, deployments, destructive shell commands, and publishing content should remain behind appropriate approval gates. The runtime, not merely the UI, must enforce these gates. fileciteturn1file0L2564-L2578

### 2.6 Event-driven autonomy

Do not constantly run the LLM. Prefer:

```text
EVENT → Should I care? → NO: sleep
                       → YES: wake → reason → act
```

This is important for compute, cost, and predictable autonomous behavior. fileciteturn1file0L812-L848

### 2.7 Persistent responsibility

The core product abstraction is **responsibility**, not conversation. A responsibility should eventually connect goals, tasks, schedules/triggers, permissions, state, memory, actions, and notifications. fileciteturn1file0L1482-L1504

### 2.8 Audit important actions

The user should be able to understand what happened, when, why, which tool was used, which permission was used, and what result occurred. fileciteturn1file0L2580-L2600

### 2.9 Avoid premature complexity

Do not introduce Kubernetes, distributed databases, complex event systems, vector infrastructure, or multi-agent architecture until the simpler design proves insufficient. fileciteturn1file0L2601-L2615

---

## 3. Reference Stack

The current proposed Lego stack is:

| Layer | Component | Role |
|---|---|---|
| Primary LLM | Sarvam-105B | Primary reasoning |
| Local LLM | Ollama | Offline/private/local inference |
| STT | Saaras | Voice → text |
| TTS | Bulbul | Text → voice |
| Voice | Pipecat | Realtime audio pipeline |
| Agent | LangGraph | Stateful orchestration |
| Tools | MCP | Universal tool interface |
| Browser | Playwright | Web interaction |
| Coding | OpenHands | Coding specialist |
| API | FastAPI | Backend |
| Database | SQLite → PostgreSQL | State |
| Vector | pgvector | Semantic memory |
| Events | Redis | Event/queue layer |
| Scheduler | APScheduler → EventBridge | Scheduled jobs |
| Initial UI | Open WebUI | Chat interface |
| Containers | Docker Compose | Local deployment |
| Cloud | AWS | Optional deployment |

These are project architecture choices. Exact package versions, API versions, model versions, and AWS pricing/free-tier assumptions must be verified at implementation time. fileciteturn1file0L1968-L1989

---

## 4. Architecture Boundaries

Preferred dependency direction:

```text
Application
    ↓
Core interfaces
    ↑
Providers / adapters
```

The core should depend on abstractions such as `LLMProvider`, `MemoryProvider`, and `ToolProvider`, not directly on vendor SDKs.

Vendor-specific code belongs under `providers/`.

The proposed repository layout is:

```text
narada/
├── apps/
│   ├── api/
│   └── web/
├── core/
│   ├── agent/
│   │   ├── loop.py
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── observer.py
│   │   └── state.py
│   ├── memory/
│   │   ├── working.py
│   │   ├── episodic.py
│   │   ├── semantic.py
│   │   └── store.py
│   ├── tools/
│   │   ├── registry.py
│   │   ├── permissions.py
│   │   └── base.py
│   ├── events/
│   │   ├── bus.py
│   │   └── handlers.py
│   ├── scheduler/
│   │   └── scheduler.py
│   └── llm/
│       ├── base.py
│       ├── ollama.py
│       └── remote.py
├── providers/
│   ├── llm/
│   │   ├── sarvam.py
│   │   └── ollama.py
│   └── voice/
│       ├── saaras.py
│       └── bulbul.py
├── agent/
│   └── graph.py
├── tools/
│   └── mcp.py
├── plugins/
├── memory/
├── storage/
├── infra/
│   ├── docker/
│   └── aws/
├── tests/
├── docs/
└── scripts/
```

The source of truth explicitly requires Sarvam-specific implementation to remain isolated under `providers/`. fileciteturn1file0L1011-L1093

---

## 5. Agent Runtime

The agent loop is the heart of Nārada:

```text
GOAL
 ↓
PLAN
 ↓
EXECUTE
 ↓
OBSERVE
 ↓
MEMORY
 ↓
DECIDE
 ├── COMPLETE
 └── CONTINUE → PLAN
```

Recommended conceptual responsibilities:

- `planner` — turns goals into executable steps.
- `executor` — performs authorized actions.
- `observer` — normalizes tool/action results.
- `state` — represents current execution state.
- `loop` — coordinates transitions.

The LLM proposes actions; the runtime decides whether those actions are authorized and executes them through tools.

### LangGraph

LangGraph is the planned orchestration component for stateful workflows, checkpoints, retries, branches, human-in-the-loop flows, and tool execution. BASE should remain simple enough to understand the loop before LangGraph becomes a major dependency. fileciteturn1file0L515-L549

---

## 6. Tools and MCP

MCP is a major Lego block. Prefer existing MCP servers over custom integrations where suitable.

Conceptually:

```text
Nārada
  ↓
Tool abstraction
  ↓
MCP
  ↓
MCP Server
  ↓
External service
```

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

Tools should expose metadata for capability, risk, permission, approval, input/output contracts, and auditability. fileciteturn1file0L554-L611

### Tool execution rule

Never let an LLM response directly execute arbitrary side effects.

Use:

```text
LLM proposes
 ↓
Tool registry
 ↓
Permission/risk evaluation
 ↓
Approval if required
 ↓
Execute
 ↓
Observe
 ↓
Audit
```

---

## 7. Browser and Coding Specialists

### Browser

Use Playwright for browser automation. Expose browser capabilities through MCP where useful. Nārada should reason about browser goals, not browser internals. fileciteturn1file0L668-L686

### Coding

Use OpenHands as a coding specialist rather than building a second coding agent. Nārada should eventually coordinate the task, delegate, review the result, and enforce approval boundaries. fileciteturn1file0L690-L712

Specialist agents belong later in the roadmap. Do not introduce multi-agent complexity before the single-agent loop is reliable.

---

## 8. Memory

Nārada has four conceptual memory types:

### Working memory

Current task, plan, observations, and tool calls.

### Episodic memory

What happened previously.

### Semantic memory

Stable knowledge useful across tasks.

### Responsibility memory

Long-lived jobs assigned by the user.

Memory should follow:

```text
remember?
 ↓
importance?
 ↓
store
 ↓
retrieve when relevant
```

Do not dump every conversation into permanent memory. fileciteturn1file0L716-L760

### Storage progression

Start with:

```text
SQLite + full-text search
```

Later, when justified:

```text
PostgreSQL + pgvector
```

Potential entities:

```text
conversations
tasks
responsibilities
events
memories
embeddings
```

Do not introduce PostgreSQL/vector infrastructure merely because it appears in the long-term design. fileciteturn1file0L764-L806

---

## 9. Responsibilities, Goals, Tasks, Actions

Keep these concepts distinct.

### Responsibility

A persistent job assigned by the user.

### Goal

The outcome the responsibility is trying to achieve.

### Task

A concrete unit of work.

### Action

A tool operation performed to advance a task.

### Observation

The result of an action.

### Decision

What Nārada should do next.

Example:

```text
Responsibility: Monitor GitHub project
Goal: Identify important changes
Task: Check recent commits
Action: Call GitHub tool
Observation: Three commits found
Decision: Analyze whether they matter
```

This separation is essential for persistent autonomy.

---

## 10. Events and Scheduling

Nārada should react to events rather than continuously poll with an LLM.

Potential events:

```text
timer
email_received
file_changed
github_push
webhook
calendar_event
user_message
system_alert
tool_result
task_completed
```

Initial local event layer: **Redis**.

Potential later distributed alternative: **NATS**.

Do not introduce NATS prematurely. fileciteturn1file0L852-L873

Scheduling:

```text
Local → APScheduler
AWS   → EventBridge Scheduler
```

Keep scheduling infrastructure separate from responsibility business logic. fileciteturn1file0L877-L899

---

## 11. API and CLI

FastAPI is the backend boundary. It should eventually expose capabilities such as:

- chat
- task creation
- responsibility management
- status
- tools
- memory operations
- approvals
- health checks
- events
- agent execution

Initial CLI:

```bash
narada start
narada chat
narada status
```

Longer-term commands include:

```bash
narada init
narada run
narada memory
narada tasks
narada tools
narada permissions
narada deploy
```

Keep business logic in the core; route handlers and CLI commands should be transport interfaces. fileciteturn1file0L903-L928

---

## 12. Voice

Voice is an interface, not the core intelligence. It belongs after the agent architecture is stable.

Planned stack:

```text
MIC
 ↓
Saaras
 ↓
Nārada
 ↓
LLM
 ↓
Bulbul
 ↓
SPEAKER
```

Pipecat owns realtime voice plumbing. Nārada owns agent state, responsibility, memory, tools, permissions, and orchestration. fileciteturn1file0L1592-L1638

Keep Saaras/Bulbul code behind provider interfaces.

---

## 13. Local / Hybrid / Cloud

### Local

```text
Laptop
├── Nārada
├── Ollama
├── Memory
├── Tools
├── Scheduler
└── Voice
```

### Hybrid

```text
AWS
├── API
├── Scheduler
└── State
     │
   Internet
     │
   Laptop
   ├── Ollama
   ├── Private tools
   └── Heavy inference
```

### Cloud

```text
AWS
├── Nārada
├── Workers
├── Database
├── Scheduler
└── External LLM
```

Use a runtime abstraction rather than scattering `if aws:` throughout the core. The architecture explicitly calls for `LocalRuntime` and `AWSRuntime`. fileciteturn1file0L324-L330

---

## 14. AWS Rules

AWS should provide lightweight infrastructure when needed:

- API
- authentication
- agent state
- scheduler
- database
- dashboard
- queues
- events
- notifications
- lightweight workers

Do not prematurely add:

- GPU cloud inference
- EKS/Kubernetes
- NAT Gateway
- managed caches
- OpenSearch
- unnecessarily large managed databases

Keep serious inference local where appropriate. AWS free-tier/pricing assumptions must be rechecked at deployment time because they change. Cost monitoring is part of the architecture. fileciteturn1file0L224-L256

---

## 15. Docker and Local Development

Use Docker Compose from the beginning.

Potential services:

```text
Nārada API
Nārada Worker
Redis
PostgreSQL
Open WebUI
Ollama
```

Use profiles so BASE development does not require every future service. The initial local environment should remain lightweight. fileciteturn1file0L986-L1007

Do not require AWS for core development.

Always use a Python virtual environment (`venv` or `.venv`) for local development, tests, and dependency execution when available.

---

## 16. Security and Secrets

Never commit:

- API keys
- access tokens
- passwords
- private credentials
- production secrets

Use `.env` locally and `.env.example` as the documented configuration surface. Cloud secrets should eventually use an established secrets system.

Do not invent custom authentication. Local mode can remain simple; cloud mode should use an established identity provider. fileciteturn1file0L971-L983

---

## 17. Testing Requirements

Tests should cover behavior, not just implementation details.

### Unit tests

Cover:

- state transitions
- permission checks
- risk classification
- memory policies
- provider adapters
- event parsing
- scheduling logic

### Integration tests

Cover where applicable:

- provider adapters
- MCP tools
- storage
- event flow
- browser integration
- API endpoints

### Agent-loop tests

At minimum test:

```text
Goal
 → Plan
 → Tool
 → Observation
 → Memory
 → Decision
```

### Safety tests

Explicitly test that:

```text
capability != permission
```

Examples:

- denied tool does not execute
- missing approval blocks consequential action
- destructive action cannot bypass the approval layer
- important actions produce audit records

### Deterministic tests

Use fake/mock providers for core tests rather than depending on free-form live LLM output. Live provider tests should be separated where practical.

---

## 18. Error Handling and Recovery

Errors should preserve enough context to answer:

```text
What failed?
Where?
Which responsibility/task?
Which action?
Was it retried?
Was approval involved?
```

Do not silently swallow errors.

Retries should distinguish:

```text
Transient failure → maybe retry
Permanent failure → stop/report
Permission failure → do not blindly retry
Approval required → pause
Invalid input → correct or stop
Rejected destructive action → do not retry
```

Never retry consequential side effects without considering idempotency.

As V4 develops, long-running tasks should use checkpoints so Nārada can recover from process failures. The roadmap explicitly includes retries, failure recovery, and checkpointing. fileciteturn1file0L1550-L1586

---

## 19. Observability and Audit

For important autonomous execution, make it possible to reconstruct:

```text
Responsibility
 ↓
Task
 ↓
Plan
 ↓
Action
 ↓
Tool
 ↓
Observation
 ↓
Decision
```

Logs must never unnecessarily expose secrets.

The user should eventually be able to inspect meaningful activity, permissions, approvals, and outcomes.

---

## 20. Privacy and Model Routing

Local-first should be treated as a privacy property.

The architecture should eventually support policies such as:

```text
private task  → local
public research → remote allowed
sensitive file → local
```

Never send private data to a remote provider merely because it is the default provider.

Model routing must respect permission and privacy policy.

---

## 21. AI Coding Agent Workflow

When modifying Nārada:

### Step 1 — Identify the capability

Ask:

```text
What user capability is changing?
Which roadmap phase owns it?
```

### Step 2 — Find the correct boundary

Decide whether the change belongs in:

```text
core/
providers/
tools/
plugins/
apps/
infra/
tests/
```

### Step 3 — Reuse existing components

Search before implementing. Prefer an existing interface, provider, MCP server, or library when it already solves the problem.

### Step 4 — Make the smallest coherent change

Prefer a small interface + adapter + tests over a speculative framework.

### Step 5 — Preserve replaceability

Vendor SDKs should remain behind adapters.

### Step 6 — Check safety

Ask:

```text
Does this create a capability?
Does it create permission?
What is the risk?
Does it require approval?
What must be audited?
```

### Step 7 — Test

Run the relevant unit/integration/agent/safety tests.

### Step 8 — Report honestly

Summarize:

- what changed
- why
- which boundary owns it
- tests run
- known limitations
- decisions intentionally left open

Never claim tests passed if they were not run.

---

## 22. What Not to Do

Do not:

- build the UI before the agent loop
- couple core logic directly to Sarvam
- couple core logic directly to AWS
- let the LLM bypass permissions
- execute arbitrary shell commands without authorization
- treat capability as permission
- store every conversation as permanent memory
- introduce pgvector before it is justified
- introduce Kubernetes early
- create custom protocols when MCP solves the need
- introduce multi-agent architecture before the single-agent loop works
- hide consequential actions from the user
- implement future roadmap stages without a concrete need

---

## 23. Dependency Decision Framework

Before adding a dependency, ask:

1. Does the stack already solve this?
2. Is there a mature component available?
3. Does it create vendor lock-in?
4. Can it be isolated behind an interface?
5. Does it increase operational complexity?
6. Can it run locally?
7. Can it be replaced later?
8. Does it introduce security/privacy consequences?
9. Does it belong to the current roadmap phase?
10. Is the smallest viable implementation enough?

If a mature Lego block exists, prefer integrating it over rebuilding it.

---

## 24. Roadmap Gates

### BASE — Foundation

Target:

```text
User
 ↓
FastAPI
 ↓
Nārada
 ↓
LLMProvider
 ├── Sarvam
 └── Ollama
 ↓
Response
```

Stack: Python, FastAPI, Docker Compose, Sarvam-105B, SQLite, CLI, `.env`, logging.

### V1 — Can Act

MCP, tool registry, permissions, filesystem, web, Playwright, shell, LangGraph, approvals, audit.

### V2 — Remembers

Conversation history, working/episodic/semantic memory, retrieval, preferences, task history, optional PostgreSQL/pgvector.

### V3 — Takes Responsibility

Tasks, goals, responsibilities, schedules, triggers, persistent state, notifications.

### V4 — Autonomous

Events, workers, wake/sleep, retries, recovery, prioritization, checkpoints, approval gates, monitoring.

### V5 — Voice

Microphone, Saaras, streaming, Bulbul, output, barge-in, Pipecat, activation.

### V6 — Specialists

Specialist interface, researcher, coder, OpenHands, delegation, specialist permissions, result verification.

### V7 — Computer

Browser agent, computer-use environment, terminal, workspace isolation, high-risk approvals, screenshots/state observation, audit.

### V8/V9 — Hybrid and Cloud

Runtime abstraction, local/hybrid runtime, secure gateway, AWS API/scheduler/state, cloud deployment/worker/database/monitoring/secrets/cost controls.

### V10 — Platform

Dashboard, marketplace, plugins, MCP management, permissions UI, memory explorer, task history, audit, cost tracking, model routing, profiles, workspaces.

The roadmap is progressive: each version should produce a genuinely usable milestone. fileciteturn1file0L1324-L1376

---

## 25. Open Decisions

Do not silently make these permanent architecture decisions:

1. Exact Sarvam API/model version.
2. Exact local Ollama model.
3. Long-term role of LangGraph.
4. Exact MCP server set.
5. Redis → NATS migration point.
6. SQLite → PostgreSQL migration point.
7. Dedicated frontend after Open WebUI.
8. Authentication provider.
9. AWS deployment mechanism.
10. AWS Free Tier assumptions.
11. Voice activation model.
12. Computer-use environment.
13. Specialist-agent boundaries.
14. Multi-user support.
15. Cloud/local synchronization.
16. Memory encryption strategy.
17. Backup strategy.
18. Data retention.
19. User-controlled memory deletion/export.
20. Cost/usage quotas.

When one becomes necessary, document the decision and its rationale.

---

## 26. Definition of Done

A Nārada change is not complete merely because code exists.

For a normal feature, verify:

- correct architectural boundary
- provider isolation where needed
- permission implications considered
- approval implications considered
- persistence implications considered
- tests added
- relevant checks run
- errors handled
- documentation updated when architecture changed
- no unnecessary future infrastructure introduced

For autonomous features, additionally verify:

- can it recover?
- can it stop safely?
- can the user understand its state?
- can it explain important actions?
- can it avoid unauthorized side effects?

---

## 27. Product Mental Model

Think of Nārada as a chief personal agent surrounded by replaceable Lego blocks:

```text
                         NĀRADA
                    Chief Personal Agent
                            │
              ┌─────────────┼─────────────┐
              │             │             │
           Memory        Planning       Events
              │             │             │
              └─────────────┼─────────────┘
                            │
                     Agent Orchestrator
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
      Researcher          Coder            Browser
          │                 │                 │
         Web             OpenHands        Playwright
                            │
                           MCP
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
       GitHub             Notion           Calendar
                            │
                     Model Gateway
                      ┌─────┴─────┐
                      │           │
                   Sarvam       Ollama
                      │           │
                   Cloud        Local
```

Nārada is the responsibility owner and orchestrator. The surrounding systems are replaceable components. fileciteturn1file0L2619-L2667

---

## 28. Final Rule

When implementing any new feature, ask:

```text
1. What responsibility or user capability does this enable?
2. Which roadmap phase owns it?
3. Does Nārada actually need to own this functionality?
4. Is there a mature component we can plug in?
5. What interface keeps that component replaceable?
6. What state must be persisted?
7. What permissions does it require?
8. Does it need user approval?
9. What should be audited?
10. How does it behave locally?
11. How does it behave in hybrid/cloud mode?
12. How will it be tested?
13. What is the smallest implementation that proves it works?
```

If a mature Lego block exists, integrate it.

If an action is consequential, do not bypass approval.

If a feature cannot run locally, document why.

If the smallest proof is unclear, reduce the scope.

> **Nārada's value is not in recreating every subsystem. Its value is in making proven components work together as one coherent, reliable, safe, persistent agent.**

> **Don't build the bricks. Build the temple.**
