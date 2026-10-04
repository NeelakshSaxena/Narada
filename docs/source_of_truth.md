# NĀRADA — Project Source of Truth

> A local-first, autonomous personal agent runtime built by composing mature open-source components and replaceable service providers.

**Project codename:** NĀRADA  
**Primary goal:** Build a persistent autonomous agent inspired by the “always-on responsibility” concept of modern agent products, while remaining local-first, modular, self-hostable, and deployable to low-cost AWS infrastructure.

---

# 0. Executive Summary

NĀRADA is not intended to be “another ChatGPT.”

The core idea is:

> **Give Nārada a responsibility, and it figures out how to keep that responsibility moving.**

A normal chatbot primarily does:

```text
USER
 ↓
MESSAGE
 ↓
LLM
 ↓
ANSWER
```

Nārada should eventually do:

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

The project should be built as a **Lego-block composition project** rather than reinventing every subsystem.

We should use established components for:

- LLM inference/API
- speech-to-text
- text-to-speech
- voice streaming
- agent orchestration
- tool protocols
- browser automation
- coding agents
- databases
- vector search
- event queues
- scheduling
- web UI
- containers
- cloud infrastructure

Our engineering effort should concentrate on the parts that make Nārada itself distinctive:

- identity
- responsibility model
- orchestration
- permissions
- memory policy
- approval gates
- auditability
- model/tool routing
- local/cloud execution
- user experience

---

# 1. Why the Name NĀRADA?

The project is named **Nārada**, after Nārada Muni from the Purāṇic tradition.

The name was chosen because Nārada is a strong conceptual archetype for an information-moving agent:

- travels between worlds
- gathers information
- communicates it to the right people
- carries messages
- acts independently
- knows what is happening in different places
- connects otherwise separate parties

This maps well onto the project's philosophy.

## Project identity

> **NĀRADA — A personal autonomous agent runtime.**

The mythology can eventually inform the software architecture without requiring the software to become a literal mythology simulator.

Suggested conceptual mapping:

| Nārada concept | Software concept |
|---|---|
| **Nārada** | Main autonomous agent |
| **Vīṇā** | Communication/interface layer |
| **Devaloka / Bhūloka** | Different execution environments |
| **Saṃvāda** | Agent ↔ user communication |
| **Smṛti** | Memory |
| **Dūta** | Tool/action agent |
| **Sūtra** | Workflow/task |
| **Sabha** | Agent workspace |
| **Ākāśa** | Event/message bus |

Potential CLI:

```bash
narada init
narada run
narada status
narada memory
narada tasks
narada tools
narada permissions
narada deploy
```

---

# 2. Core Product Philosophy

## 2.1 Local-first

Nārada must work locally without requiring AWS.

The laptop is the primary development and local execution environment.

Target local architecture:

```text
YOUR COMPUTER
┌───────────────────────────────┐
│            NĀRADA             │
│                               │
│ Agent Runtime                 │
│ Planner                       │
│ Memory                        │
│ Tool System                   │
│ Scheduler                     │
│ Web UI                        │
│                               │
│ LLM Provider                  │
│ ├── Sarvam (cloud)            │
│ └── Ollama (local)            │
└───────────────────────────────┘
```

The system should also work in offline/local-LLM mode where possible.

---

# 3. Local + AWS Requirement

Nārada must be designed so that the **same agent code** can run in multiple execution modes.

## 3.1 Local

```text
Laptop
├── Nārada
├── Ollama
├── Memory
├── Tools
├── Scheduler
└── Voice
```

## 3.2 Hybrid

```text
                    AWS
                     │
              ┌──────┴──────┐
              │ Scheduler   │
              │ API         │
              │ State       │
              └──────┬──────┘
                     │
                  Internet
                     │
                     ▼
                   LAPTOP
                     │
                   Ollama
```

The cloud can handle lightweight coordination while the local machine supplies heavier/private inference.

## 3.3 Cloud

```text
AWS
├── Nārada
├── Workers
├── Database
├── Scheduler
└── External LLM API
```

The architecture must avoid locking the core agent logic to AWS.

---

# 4. AWS Cost Philosophy

The project should be designed to fit within AWS free/low-cost usage where practical.

Important principle:

> **Do not try to run a serious large language model on a tiny free-tier cloud VM.**

Use AWS for lightweight infrastructure:

- API
- authentication
- agent state
- scheduler
- database
- dashboard
- queues
- event orchestration
- notifications
- lightweight workers

Keep serious local inference on the user's GPU where appropriate.

Avoid prematurely introducing expensive infrastructure such as:

- GPU cloud instances
- EKS/Kubernetes
- NAT Gateway
- managed caches
- OpenSearch
- unnecessarily large managed databases

The exact AWS Free Tier changes over time, so deployment configuration must be checked against current AWS pricing/free-tier rules at implementation time.

Cost monitoring should be considered part of the infrastructure from the beginning.

---

# 5. The Central Architecture

Conceptually:

```text
                         NĀRADA
                            │
              ┌─────────────┴─────────────┐
              │       Agent Runtime       │
              │                           │
              │ Planner / Executor / Loop │
              └─────────────┬─────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
       LLM                TOOLS              MEMORY
        │                   │                   │
   ┌────┴────┐        ┌─────┴─────┐       ┌────┴────┐
   │ Sarvam  │        │    MCP    │       │ SQLite/ │
   │ 105B    │        │  servers  │       │ Postgres│
   └─────────┘        └───────────┘       └─────────┘
        │
   ┌────┴─────┐
   │   VOICE  │
   └────┬─────┘
        │
   ┌────┴────────────┐
   │                 │
Saaras v4         Bulbul v3
  STT                TTS
```

Every major box should be replaceable.

---

# 6. The Most Important Architectural Rule

## Nārada must not care where the intelligence comes from.

Use provider interfaces.

Conceptually:

```python
class LLMProvider:
    async def generate(...)
    async def stream(...)
    async def tool_call(...)
```

Potential implementations:

```text
LLMProvider
├── SarvamProvider
├── OllamaProvider
├── OpenAIProvider
├── AnthropicProvider
└── GeminiProvider
```

Likewise, execution:

```text
Runtime
├── LocalRuntime
└── AWSRuntime
```

This means changing models or deployment environments should not require rewriting Nārada's core.

---

# 7. The Lego Philosophy

Do not build everything from scratch.

Prefer existing mature/open-source components whenever they solve a problem well.

Nārada should be the **glue and intelligence layer** connecting those components.

The guiding question for every subsystem:

> “Does this need to be a Nārada invention, or can we plug in an existing component?”

If a mature component exists, use it.

---

# 8. Proposed Technology Stack

## 8.1 Primary LLM — Sarvam

Initial primary cloud LLM:

**Sarvam-105B**

Purpose:

- reasoning
- general agentic tasks
- planning
- tool-use reasoning
- multilingual interaction

Sarvam-specific code should remain behind the LLM provider interface.

---

# 9. Local LLM — Ollama

Ollama remains in the architecture from the beginning.

Conceptually:

```text
                    LLM Gateway
                         │
              ┌──────────┴──────────┐
              │                     │
           Sarvam                 Ollama
              │                     │
          Cloud LLM              Local LLM
```

Local mode:

```text
Nārada
 ↓
Ollama
 ↓
Local model
```

Cloud mode:

```text
Nārada
 ↓
Sarvam
 ↓
Sarvam-105B
```

Eventually support intelligent model routing:

```text
simple task → local
complex task → Sarvam
private task → local
Indic voice → Sarvam
```

---

# 10. Speech-to-Text — Saaras

Use **Sarvam Saaras** as the initial STT provider.

Concept:

```text
Microphone
    ↓
Saaras
    ↓
Text
    ↓
Nārada
```

For voice operation, prefer streaming/realtime mechanisms over waiting for an entire recording where appropriate.

Desired eventual capabilities:

- English
- Indian languages
- code-mixed speech
- transliteration
- translation where useful
- streaming STT

---

# 11. Text-to-Speech — Bulbul

Use **Sarvam Bulbul** as the initial TTS provider.

Concept:

```text
Nārada response
       ↓
    Bulbul
       ↓
     audio
       ↓
    speaker
```

Potential future features:

- multilingual output
- streaming TTS
- multiple voices
- custom/voice-cloned voice where legally and technically appropriate
- Tamil / Hindi / English / Hinglish

---

# 12. Voice Pipeline — Pipecat

Do not build realtime voice infrastructure from scratch.

Initial candidate:

**Pipecat**

Alternative:

**LiveKit**

Concept:

```text
Audio
 ↓
STT
 ↓
LLM
 ↓
TTS
 ↓
Audio
```

Pipecat owns voice plumbing.

Nārada owns:

- agent state
- responsibility
- memory
- tools
- permissions
- orchestration

This separation should remain clean.

---

# 13. Agent Orchestration — LangGraph

Use **LangGraph** rather than immediately inventing a complete agent orchestration engine.

Desired responsibilities:

- stateful agent workflows
- graph execution
- state transitions
- checkpoints
- retries
- conditional branches
- human-in-the-loop
- tool execution patterns

Concept:

```text
                NĀRADA
                   │
               LangGraph
                   │
         ┌─────────┼─────────┐
         │         │         │
       Think      Act      Observe
         │         │         │
         └─────────┼─────────┘
                   │
                 State
```

Important historical design decision:

- BASE may use very simple orchestration.
- LangGraph should become the orchestration layer when Nārada reaches the tool-using stage.
- Do not introduce a huge framework before understanding the core agent loop.

---

# 14. Tools — MCP

**MCP is one of the most important Lego blocks.**

Instead of writing custom integrations for every service, Nārada should consume MCP servers.

Potential tools/services:

```text
Nārada → GitHub
Nārada → Gmail
Nārada → Notion
Nārada → filesystem
Nārada → browser
Nārada → Slack
Nārada → calendars
Nārada → developer tools
```

Concept:

```text
Tool
 ↓
MCP Server
 ↓
External Service
```

Nārada should treat tools as discoverable capabilities rather than embedding every service integration into its core.

---

# 15. Tool Contracts and Permissions

Every tool should declare a contract.

Example:

```json
{
  "name": "filesystem.read",
  "risk": "low",
  "requires_confirmation": false
}
```

High-risk example:

```json
{
  "name": "shell.execute",
  "risk": "high",
  "requires_confirmation": true
}
```

Potential tool classes:

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

---

# 16. The Foundational Safety Rule

## Nārada must never confuse capability with permission.

Just because Nārada can execute something does not mean it may execute it.

Every meaningful action should be modeled with:

```text
CAPABILITY
PERMISSION
RISK
APPROVAL
AUDIT LOG
```

Example:

```text
Tool: shell.execute

Capability: YES
Permission: NO
Risk: CRITICAL
Approval: REQUIRED
```

This should be a first-class part of the architecture, not an afterthought.

---

# 17. Browser Automation — Playwright

Use **Playwright** for web/browser interaction.

Concept:

```text
Nārada
   ↓
Browser Tool
   ↓
Playwright
   ↓
Chromium
```

Expose browser capabilities through MCP where useful.

Nārada should not need to understand browser internals.

---

# 18. Coding Specialist — OpenHands

Use **OpenHands** as a coding specialist rather than building a coding agent from scratch.

Concept:

```text
Nārada
   ↓
Coding Task
   ↓
OpenHands
   ↓
Repository
   ↓
Tests
   ↓
Changes
```

Nārada becomes the manager/coordinator.

OpenHands becomes the specialist.

---

# 19. Memory Architecture

Memory should be divided into different types.

## 19.1 Working Memory

What is happening now:

```text
Current task
Current plan
Current observations
Current tool calls
```

## 19.2 Episodic Memory

What happened previously:

```text
2026-10-01
Nārada researched X.
User rejected option Y.
```

## 19.3 Semantic Memory

Stable knowledge:

```text
Project uses FastAPI.
Database is PostgreSQL.
Ollama runs locally.
```

## 19.4 Responsibility Memory

The most important long-lived layer:

```text
User assigned Nārada:
"Maintain Project X."
```

This turns Nārada from a conversational system into a persistent agent.

---

# 20. Memory Technology Strategy

Do not over-engineer memory in BASE.

Start with:

```text
SQLite
+
Full-text search
```

Later:

```text
PostgreSQL
+
pgvector
```

Potential eventual schema:

```text
PostgreSQL
├── conversations
├── tasks
├── responsibilities
├── events
├── memories
└── embeddings
```

Vector flow:

```text
Memory
 ↓
Embedding
 ↓
Vector Search
```

Do not deploy PostgreSQL or a vector database merely because they sound architecturally impressive.

Use them when the system actually needs them.

---

# 21. Event System

Nārada should not constantly run an LLM.

Instead:

```text
EVENT
  ↓
Should I care?
  ↓
NO → ignore
YES
 ↓
Wake agent
 ↓
Reason
 ↓
Act
```

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

This saves compute and is important for cost control.

---

# 22. Event Bus

Initial local option:

**Redis**

Potential later distributed option:

**NATS**

Event examples:

```text
email.received
file.changed
github.push
timer.triggered
user.message
task.completed
```

Do not introduce NATS prematurely.

---

# 23. Scheduling

Do not build a scheduler from scratch.

Local:

**APScheduler**

AWS:

**EventBridge Scheduler**

Concept:

```text
                   Scheduler
                       │
           ┌───────────┴───────────┐
           │                       │
        Local                    AWS
           │                       │
     APScheduler             EventBridge
```

---

# 24. API — FastAPI

Use **FastAPI** for the backend.

Concept:

```text
Frontend
   ↓
FastAPI
   ↓
Nārada
```

FastAPI should expose:

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

---

# 25. Frontend

Do not build a full ChatGPT clone immediately.

Initial candidate:

**Open WebUI**

Later, build a dedicated Nārada control plane.

Potential control-plane sections:

```text
NĀRADA

Chat

Responsibilities
 ├── Research monitoring
 ├── GitHub project
 └── Personal assistant

Tasks
Memory
Tools
Permissions
Activity
Agents
Approvals
```

Eventually a dedicated frontend can use:

- Next.js
- TypeScript
- Tailwind

---

# 26. Authentication

Do not invent authentication.

Local:

- local-only mode
- simple local authentication if needed

Cloud:

- AWS Cognito or another established identity provider

---

# 27. Containers

Use Docker Compose from the beginning.

Target:

```bash
docker compose up
```

Potential local services:

```text
Nārada API
Nārada Worker
Redis
PostgreSQL
Open WebUI
Ollama
```

Services should be profile-based so lightweight local development does not require every component.

---

# 28. Initial Repository Structure

Proposed monorepo:

```text
narada/
│
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
│
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

The Sarvam-specific implementation must remain isolated under `providers/`.

---

# 29. Development Modes

Nārada should eventually expose:

```bash
narada local
narada hybrid
narada cloud
```

## `narada local`

Everything runs locally.

```text
Ollama
SQLite
FastAPI
Scheduler
Tools
Voice
```

## `narada hybrid`

AWS handles:

```text
API
Scheduler
State
```

Local machine handles:

```text
LLM
private tools
heavy inference
```

## `narada cloud`

AWS handles:

```text
API
Workers
Scheduler
Database
External LLM
```

The agent code remains the same.

---

# 30. Core Agent Loop

The first true milestone is not the UI.

It is:

> Nārada can receive a goal, make a plan, use a tool, observe the result, update memory, and decide whether another action is required.

Core loop:

```text
Goal
 ↓
Plan
 ↓
Action
 ↓
Observation
 ↓
Memory
 ↓
Decision
 ↓
Action...
```

This is the heart of Nārada.

Everything else is infrastructure around it.

---

# 31. Example Responsibility

Example:

> “Keep an eye on my SIH submission.”

Nārada could create:

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

This is the desired abstraction:

> The user gives Nārada a job, not merely a question.

---

# 32. Example Monitoring Responsibility

Example:

> “Watch this GitHub project and tell me if something important changes.”

Flow:

```text
Timer
 ↓
Check GitHub
 ↓
Change?
 ├── No → Sleep
 └── Yes
       ↓
     Analyze
       ↓
     Important?
       ├── No → Sleep
       └── Yes
             ↓
           Notify
```

This is a representative autonomous responsibility.

---

# 33. Example Multi-Step Task

User:

> “Prepare my project for deployment.”

Nārada:

```text
inspect repository
 ↓
understand architecture
 ↓
check dependencies
 ↓
run tests
 ↓
find failures
 ↓
fix safe issues
 ↓
run tests again
 ↓
build Docker image
 ↓
prepare deployment
 ↓
ASK USER BEFORE DEPLOYMENT
```

This illustrates the difference between:

- reasoning
- tool use
- state
- permissions
- approval
- multi-step execution

---

# 34. Long-Term Workspace Vision

Eventually Nārada can operate across a digital workspace:

```text
                     NĀRADA
                        │
       ┌────────────────┼────────────────┐
       │                │                │
    Computer         Internet         Services
       │                │                │
    Files            Web             GitHub
    Docker           APIs            Notion
    Terminal         Search          Calendar
    VS Code                         Discord
       │
       └───────────────┬────────────────┘
                       │
                    Memory
                       │
                      Goals
                       │
                Responsibilities
```

At this stage Nārada becomes an operating layer for digital work rather than an LLM wrapper.

---

# 35. Version Roadmap

The roadmap should be progressive. Each version should produce a genuinely usable milestone.

## BASE — Foundation

### Goal

Get Nārada running locally with the smallest number of moving parts.

Architecture:

```text
User
 ↓
Nārada API
 ↓
Sarvam
 ↓
Response
```

### Stack

- Python
- FastAPI
- Docker Compose
- Sarvam-105B
- SQLite
- simple CLI
- `.env`
- logging

### Commands

```bash
narada start
narada chat
narada status
```

### Interfaces established

```text
LLMProvider
MemoryProvider
ToolProvider
VoiceProvider
```

### Deliverable

> A locally running Nārada API that can converse with Sarvam.

---

# 36. V1 — Nārada Can Act

Nārada gets hands.

### Add

- MCP
- tool registry
- tool permissions
- filesystem tools
- web search
- Playwright browser
- basic shell
- LangGraph

Architecture:

```text
NĀRADA
   │
LangGraph
   │
┌──┴───┐
│      │
LLM   Tools
│      │
Sarvam MCP
       │
   ┌───┼────┐
   │   │    │
Browser Files Shell
```

Example:

> “Find the latest Sarvam documentation and summarize the important API changes.”

Flow:

```text
think
 ↓
search
 ↓
open pages
 ↓
extract
 ↓
reason
 ↓
answer
```

### Security

```text
web.search      → automatic
file.read       → automatic
file.write      → confirmation
shell.execute   → confirmation
delete file     → blocked/explicit approval
```

### Deliverable

> Nārada can reason and use external tools.

---

# 37. V2 — Nārada Remembers

### Add

- conversation history
- episodic memory
- semantic memory
- memory retrieval
- user preferences
- task history
- SQLite → optional PostgreSQL
- embeddings / pgvector when justified

Memory flow:

```text
remember?
 ↓
importance?
 ↓
store
 ↓
retrieve when relevant
```

Do not dump every conversation into memory.

### Deliverable

> Nārada has persistent, useful memory.

---

# 38. V3 — Nārada Takes Responsibility

This is the major conceptual transition.

Until V2:

> You ask → Nārada acts.

V3:

> You assign → Nārada manages.

Introduce:

- tasks
- goals
- responsibilities
- schedules
- triggers
- persistent agent state
- notifications

Example:

> “Keep track of my Nārada GitHub repository.”

```yaml
responsibility:
  name: Nārada GitHub

goal:
  monitor_repository: true

checks:
  - issues
  - pull_requests
  - commits

schedule:
  every: 6h

permissions:
  read: true
  write: false
```

Architecture:

```text
RESPONSIBILITY
      │
   Planner
      │
    Tasks
      │
   Execute
      │
   Observe
      │
   Memory
```

### Deliverable

> Nārada can maintain an ongoing responsibility instead of only answering prompts.

---

# 39. V4 — Nārada Becomes Autonomous

Introduce the actual autonomous loop:

```text
GOAL
 ↓
PLAN
 ↓
EXECUTE
 ↓
OBSERVE
 ↓
REFLECT
 ↓
┌───────────┐
│           │
COMPLETE   CONTINUE
             │
             └────→ PLAN
```

### Add

- event bus
- scheduled execution
- webhooks
- background workers
- retries
- failure recovery
- task prioritization
- state checkpoints
- human approval gates

### Deliverable

> Nārada can wake itself, investigate, act, and go back to sleep.

This is the stage where it becomes conceptually similar to an always-on agent.

---

# 40. V5 — Nārada Gets a Voice

Only after the agent architecture is stable should voice become a major milestone.

Why:

> Voice is an interface, not the core intelligence.

### Sarvam voice stack

```text
MIC
 ↓
Saaras
 ↓
Nārada
 ↓
Sarvam-105B
 ↓
Bulbul
 ↓
SPEAKER
```

Use:

- Saaras — STT
- Bulbul — TTS
- Pipecat — realtime voice

### Features

- activation
- streaming STT
- streaming responses
- interruption/barge-in
- streaming TTS
- multilingual voice
- Hindi/Tamil/English/Hinglish

Example:

> “Nārada, check my GitHub.”

### Deliverable

> Nārada becomes a genuinely conversational voice agent.

---

# 41. V6 — Specialist Agents

Nārada becomes the chief agent.

```text
                     NĀRADA
                  Chief Agent
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    Researcher       Coder          Writer
        │              │              │
      Web           OpenHands       LLM
```

Potential specialists:

```text
Nārada
├── Researcher
├── Coder
├── Browser Agent
├── Document Agent
├── Data Agent
└── Voice Agent
```

Nārada delegates.

Example:

```text
understand request
 ↓
delegate to Coder
 ↓
OpenHands
 ↓
write code
 ↓
run tests
 ↓
return result
 ↓
Nārada reviews
 ↓
ask user for approval
```

### Deliverable

> Nārada can delegate complex work to specialist agents.

---

# 42. V7 — Computer Agent

Nārada gets access to a computer-like environment.

Potential technologies:

- Playwright
- browser-use
- computer-use-style environments
- OpenHands
- OS-level automation where appropriate

Concept:

```text
Nārada
 ↓
Computer
 ├── Browser
 ├── Terminal
 ├── VS Code
 ├── Files
 └── Applications
```

Example:

> “Set up the development environment for this project.”

Potential flow:

```text
open terminal
 ↓
clone repository
 ↓
inspect project
 ↓
install dependencies
 ↓
run tests
 ↓
fix configuration
 ↓
start services
 ↓
report
```

Risky actions remain behind approval gates.

### Deliverable

> Nārada can operate a computer, not just call APIs.

---

# 43. V8 — Hybrid Nārada

Address the local + AWS requirement seriously.

Three execution modes:

## Local

```text
Laptop
├── Nārada
├── Ollama
├── Memory
├── Tools
└── Voice
```

## Hybrid

```text
AWS
├── Scheduler
├── API
└── State
      │
   Internet
      │
      ▼
   LAPTOP
      │
    Ollama
```

## Cloud

```text
AWS
├── Nārada
├── Worker
├── Database
├── Scheduler
└── LLM API
```

### Deliverable

> The same Nārada codebase runs locally, in hybrid mode, or in cloud mode.

---

# 44. V9 — Nārada Cloud

Potential AWS architecture:

```text
Internet
   │
CloudFront
   │
API Gateway
   │
Lambda / EC2
   │
┌──┴───────────────┐
│                  │
PostgreSQL         S3
│
pgvector
```

Additional components when justified:

```text
EventBridge
SQS
Secrets Manager
CloudWatch
```

Do not introduce Kubernetes at this stage by default.

---

# 45. V10 — Nārada Platform

This is the “real platform” stage.

Dashboard:

```text
NĀRADA
────────────────────────────

TODAY

● 3 responsibilities active
● 7 tasks completed
● 2 awaiting approval
● 1 issue detected

RESPONSIBILITIES

▶ GitHub Project
▶ Research monitoring
▶ Personal assistant

MEMORY

1,284 memories

AGENTS

Nārada
 ├── Researcher
 ├── Coder
 └── Browser
```

Features:

- agent marketplace
- plugin system
- MCP server management
- permissions UI
- memory explorer
- task history
- audit logs
- cost tracking
- model routing
- user profiles
- multiple workspaces

---

# 46. Roadmap Summary

| Version | Nārada learns to... | Main Lego |
|---|---|---|
| **BASE** | Talk | FastAPI + Sarvam |
| **V1** | Act | MCP + LangGraph + Playwright |
| **V2** | Remember | SQLite/Postgres + pgvector |
| **V3** | Take responsibility | Tasks + goals + scheduler |
| **V4** | Act autonomously | Events + workers + approvals |
| **V5** | Speak | Saaras + Bulbul + Pipecat |
| **V6** | Delegate | OpenHands + specialist agents |
| **V7** | Operate computers | Browser/computer automation |
| **V8** | Run hybrid | Local + AWS |
| **V9** | Run in cloud | AWS infrastructure |
| **V10** | Become a platform | Dashboard + plugins + multi-agent |

---

# 47. Four Eras

## Era I — The Messenger

**BASE → V2**

```text
Talk
Act
Remember
```

Nārada is an AI assistant.

## Era II — The Agent

**V3 → V4**

```text
Responsibilities
 ↓
Planning
 ↓
Execution
 ↓
Monitoring
```

Nārada becomes an autonomous agent.

## Era III — The Operator

**V5 → V7**

```text
Voice
 ↓
Specialists
 ↓
Computer
```

Nārada becomes an AI operator.

## Era IV — The Network

**V8 → V10**

```text
Local
 ↕
AWS
 ↕
Agents
 ↕
Services
```

Nārada becomes an agent platform.

---

# 48. Recommended Actual Initial Stack

The proposed Lego stack for the project:

| Layer | Component | Role |
|---|---|---|
| LLM | Sarvam-105B | Primary reasoning |
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
| UI initially | Open WebUI | Chat interface |
| Containers | Docker Compose | Local deployment |
| Cloud | AWS | Optional deployment |

---

# 49. What We Are NOT Building From Scratch

Do not reinvent:

- LLM inference
- speech recognition
- TTS
- realtime audio transport
- browser automation
- generic agent graphs
- MCP
- database engines
- vector search
- scheduling
- event queues
- container runtime
- authentication
- cloud primitives
- coding agents
- generic chat UI

Instead, integrate existing technology.

---

# 50. What Nārada SHOULD Own

Nārada's unique intellectual property / core implementation should concentrate on:

## Identity

Who is Nārada?

## Responsibility model

What ongoing jobs has the user given Nārada?

## Goal management

What is Nārada trying to accomplish?

## Planning policy

How does Nārada turn responsibilities into tasks?

## Memory policy

What should be remembered, forgotten, summarized, or retrieved?

## Permission model

What may Nārada do?

## Approval model

When must Nārada ask the user?

## Agent routing

Which model/tool/specialist should handle a task?

## Event interpretation

Which events actually matter?

## Autonomous loop

When should Nārada wake, act, observe, and sleep?

## Auditability

What happened, when, why, and with which permission?

## Local/cloud execution

Where should a task run?

## User experience

How does the user understand what Nārada is doing?

These are the pieces that make Nārada actually Nārada.

---

# 51. Initial MVP Definition

Do not try to build all of “ChatGPT Dots.”

The first autonomous proof should be small.

Example:

> “Research the latest NVIDIA RTX 5060 laptop prices and tell me if anything interesting appears.”

Nārada:

```text
Create responsibility
        ↓
Create schedule
        ↓
Wake up
        ↓
Use web tool
        ↓
Collect information
        ↓
Compare against previous state
        ↓
If meaningful change
        ↓
Notify user
```

If this works reliably, Nārada is already a real autonomous agent.

---

# 52. First Major Milestone

Do not code the UI first.

The first major technical milestone is:

> **Nārada can receive a goal, make a plan, use a tool, observe the result, update memory, and decide whether another action is required.**

Core:

```text
Goal
 ↓
Plan
 ↓
Action
 ↓
Observation
 ↓
Memory
 ↓
Decision
 ↓
Action...
```

Once this works reliably, the following become infrastructure around the core:

- web UI
- scheduling
- notifications
- AWS deployment
- multiple agents
- voice
- specialist delegation

---

# 53. Suggested BASE Build Order

Within BASE, build in this order:

### BASE.1 — Repository

```text
narada/
pyproject.toml
README.md
.env.example
```

### BASE.2 — Configuration

- environment variables
- provider selection
- logging

### BASE.3 — LLM interface

```text
LLMProvider
```

Implement:

```text
SarvamProvider
```

### BASE.4 — Minimal FastAPI

Endpoints:

```text
GET /health
POST /chat
GET /status
```

### BASE.5 — Minimal CLI

```bash
narada start
narada chat
narada status
```

### BASE.6 — SQLite

Store:

- conversations
- basic task state
- basic agent state

### BASE.7 — Docker

```bash
docker compose up
```

### BASE.8 — Ollama adapter

Add:

```text
OllamaProvider
```

Now Nārada can switch between Sarvam and local inference.

---

# 54. V1 Build Order

### V1.1

Tool abstraction.

### V1.2

MCP client.

### V1.3

First MCP tools:

- filesystem
- web
- GitHub
- browser

### V1.4

LangGraph integration.

### V1.5

Tool permission system.

### V1.6

Approval flow.

### V1.7

Audit log.

### V1.8

Multi-step tool-use tests.

---

# 55. V2 Build Order

### V2.1

Conversation persistence.

### V2.2

Working memory.

### V2.3

Episodic memory.

### V2.4

Semantic memory.

### V2.5

Memory retrieval.

### V2.6

Memory importance scoring.

### V2.7

Optional pgvector.

---

# 56. V3 Build Order

### V3.1

Task model.

### V3.2

Goal model.

### V3.3

Responsibility model.

### V3.4

Scheduler.

### V3.5

Triggers.

### V3.6

Notifications.

### V3.7

Responsibility dashboard.

---

# 57. V4 Build Order

### V4.1

Event bus.

### V4.2

Worker process.

### V4.3

Wake/sleep cycle.

### V4.4

Retries.

### V4.5

Failure recovery.

### V4.6

Checkpointing.

### V4.7

Approval gates.

### V4.8

Autonomous monitoring.

---

# 58. V5 Build Order

### V5.1

Microphone input.

### V5.2

Saaras integration.

### V5.3

Streaming pipeline.

### V5.4

Bulbul integration.

### V5.5

Audio output.

### V5.6

Interruption/barge-in.

### V5.7

Pipecat integration.

### V5.8

Voice activation.

---

# 59. V6 Build Order

### V6.1

Specialist agent interface.

### V6.2

Research specialist.

### V6.3

Coding specialist.

### V6.4

OpenHands integration.

### V6.5

Delegation policy.

### V6.6

Specialist permissions.

### V6.7

Result verification.

---

# 60. V7 Build Order

### V7.1

Browser agent.

### V7.2

Computer-use environment.

### V7.3

Terminal environment.

### V7.4

Workspace isolation.

### V7.5

High-risk approval gates.

### V7.6

Screenshot/state observation.

### V7.7

Action audit.

---

# 61. V8/V9 Build Order

### V8.1

Runtime abstraction.

### V8.2

Local runtime.

### V8.3

Hybrid runtime.

### V8.4

Secure local gateway.

### V8.5

AWS API.

### V8.6

AWS scheduler.

### V8.7

AWS state.

### V9.1

Cloud deployment.

### V9.2

Cloud worker.

### V9.3

Cloud database.

### V9.4

Cloud monitoring.

### V9.5

Secrets management.

### V9.6

Cost controls.

---

# 62. Open Questions / Decisions to Make Later

These should remain explicitly open rather than being silently decided:

1. Exact Sarvam API model/version to use at implementation time.
2. Exact local Ollama model.
3. Whether LangGraph becomes permanent or only an orchestration component.
4. Exact MCP server set.
5. Whether Redis remains the event layer or transitions to NATS.
6. SQLite → PostgreSQL migration point.
7. Exact frontend technology after Open WebUI.
8. Authentication provider.
9. AWS deployment mechanism: CDK, Terraform, CloudFormation, or another approach.
10. Exact AWS Free Tier assumptions at deployment time.
11. Whether voice should be always-listening, push-to-talk, or wake-word activated.
12. Exact computer-use environment.
13. Specialist-agent boundaries.
14. Multi-user support.
15. Cloud/local synchronization model.
16. Encryption strategy for memory.
17. Backup strategy.
18. Data retention policy.
19. User-controlled memory deletion/export.
20. Cost/usage quotas.

---

# 63. Design Principles

## Principle 1 — Local first

If Nārada can work locally, it should.

## Principle 2 — Provider agnostic

No single LLM, TTS, STT, database, or cloud should own the architecture.

## Principle 3 — Lego, not monolith

Prefer mature components.

## Principle 4 — Capability ≠ permission

A tool being available does not mean Nārada can use it without authorization.

## Principle 5 — Human approval for consequential actions

Especially:

- sending messages
- deleting data
- financial actions
- account changes
- deployments
- destructive shell commands
- publishing content

## Principle 6 — Event-driven autonomy

Do not constantly invoke the LLM.

## Principle 7 — Persistent responsibility

The core product abstraction is not “conversation.”

It is “responsibility.”

## Principle 8 — Audit everything important

The user should be able to understand:

- what happened
- when
- why
- which tool was used
- what permission was used
- what result occurred

## Principle 9 — Build the agent before the interface

The agent loop matters more than a pretty dashboard.

## Principle 10 — Avoid premature complexity

Do not introduce:

- Kubernetes
- distributed databases
- complex event systems
- vector infrastructure
- multi-agent architectures

until the simpler architecture proves insufficient.

---

# 64. Desired End-State

The eventual vision:

```text
                         NĀRADA
                    Chief Personal Agent
                              │
             ┌────────────────┼────────────────┐
             │                │                │
          Memory           Planning          Events
             │                │                │
             └────────────────┼────────────────┘
                              │
                       Agent Orchestrator
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
      Researcher            Coder              Browser
         │                    │                    │
        Web                OpenHands          Playwright
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                             MCP
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
       GitHub              Notion             Calendar
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                         Model Gateway
                              │
                ┌─────────────┴─────────────┐
                │                           │
             Sarvam                      Ollama
                │                           │
           Cloud LLM                    Local LLM
                │
          ┌─────┴──────┐
          │            │
       Saaras        Bulbul
         STT           TTS
          │            │
          └──── Pipecat┘
```

And the runtime can exist in:

```text
LOCAL
  ↕
HYBRID
  ↕
AWS CLOUD
```

---

# 65. The Final Product Idea

Nārada should eventually feel less like:

> “a chatbot that has tools”

and more like:

> **“a personal digital operator that has responsibilities.”**

The user should be able to say:

```text
"Handle this."
```

or:

```text
"Keep an eye on this."
```

or:

```text
"Take care of this project."
```

and Nārada should transform that into:

```text
Goal
 ↓
Responsibility
 ↓
Plan
 ↓
Tasks
 ↓
Tools
 ↓
Events
 ↓
Memory
 ↓
Progress
 ↓
User updates
```

while respecting:

```text
Permissions
Approvals
Safety
Privacy
Cost
```

---

# 66. Immediate Next Step

The project should begin with:

## NĀRADA BASE

Target stack:

```text
Python
FastAPI
Docker Compose
SQLite
Sarvam-105B
Ollama adapter
CLI
Logging
```

First technical objective:

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

Then establish the interfaces before adding complexity.

The next major milestone after BASE is:

```text
NĀRADA V1

Nārada
 ↓
LangGraph
 ↓
MCP
 ↓
Tools
```

The first genuinely meaningful demo should be:

> **“Nārada, research X, use the available tools, remember the result, and explain what you found.”**

After that:

> **“Nārada, keep watching X and tell me when something important changes.”**

That second sentence is the moment the project stops being merely a chatbot and starts becoming an autonomous agent.

---

# 67. Source Conversation

This document consolidates the project discussion that established:

- the Nārada name and rationale
- the local-first philosophy
- AWS compatibility
- free/low-cost infrastructure constraints
- agent runtime architecture
- responsibility as the central abstraction
- memory architecture
- event-driven execution
- scheduler design
- provider abstraction
- permissions and approval model
- Lego-block/open-source strategy
- Sarvam as the initial LLM/STT/TTS provider family
- Ollama as the local model layer
- MCP as the universal tool interface
- LangGraph as orchestration
- Pipecat as voice plumbing
- Playwright for browser automation
- OpenHands for coding specialization
- SQLite/PostgreSQL/pgvector strategy
- Redis/NATS event strategy
- FastAPI backend
- Open WebUI initial interface
- Docker Compose local deployment
- the BASE → V10 roadmap
- the four development eras
- the initial implementation order

The original conversation is the source from which this project specification was consolidated. fileciteturn0file0L23-L33

---

# 68. Working Motto

> **Don't build the bricks. Build the temple.**

Nārada's job is to connect proven components into a coherent autonomous system.

The value is not in recreating every subsystem.

The value is in making the whole thing work together — reliably, safely, locally, and eventually across the cloud.
