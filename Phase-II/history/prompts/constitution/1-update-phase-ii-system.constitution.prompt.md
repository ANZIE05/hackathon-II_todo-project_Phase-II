---
id: 1
title: Update Phase-II System Constitution
stage: constitution
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: claude
command: /sp.constitution
labels: [constitution, spec-driven-development, full-stack, todo-application]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
You are operating under the Phase-II System Constitution for a Full-Stack Todo Application.

This constitution is the highest authority.
All agents, sub-agents, and generated outputs MUST comply with it.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I. CORE DEVELOPMENT PRINCIPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SPEC-DRIVEN DEVELOPMENT ONLY
- All behavior must be defined in specs before implementation
- Specs are the single source of truth
- No implicit logic is allowed

2. NO MANUAL CODING
- Humans do not write application code
- All code is generated strictly from specs
- Any missing behavior must be added to specs first

3. MONOREPO MANDATE
- Frontend and backend live in the same repository
- Clear separation of concerns is required

4. INCREMENTAL EVOLUTION
- Phase-I console app concepts evolve into Phase-II web app
- No regression of previously defined behavior

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
II. ARCHITECTURE CONSTRAINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Frontend:
- Next.js (App Router)
- JWT-based authentication (Better Auth compatible)
- REST API consumption only

Backend:
- FastAPI
- SQLModel ORM
- JWT authentication required for ALL endpoints

Database:
- Neon Serverless PostgreSQL
- Persistent storage is mandatory
- No in-memory persistence allowed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
III. SECURITY & AUTHORIZATION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ZERO TRUST MODEL
- Every API request MUST include a valid JWT
- No public or anonymous endpoints (except auth)

2. USER ISOLATION
- Users can ONLY access their own tasks
- Ownership must be enforced at query level

3. TOKEN ENFORCEMENT
- JWT verification happens before business logic
- Expired or invalid tokens result in immediate rejection

4. NO DATA LEAKAGE
- No cross-user reads or writes
- Error responses must not expose sensitive data

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IV. API & CONTRACT RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. REST API ONLY
- No GraphQL or RPC patterns

2. EXPLICIT CONTRACTS
- Every endpoint must define:
  - Request schema
  - Response schema
  - Error schema
  - Status codes

3. CONSISTENCY
- Frontend and backend must rely on the same contracts
- Contract changes require spec updates

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
V. AGENT GOVERNANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. PRODUCT / SPEC ORCHESTRATOR
- Has final authority on specs
- Coordinates all agents

2. AGENT SCOPE LIMITS
- Each agent must operate only within its defined role
- Agents may reference other specs but not override them

3. SUB-AGENTS
- Must defer to main agent decisions
- Cannot introduce new requirements independently

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VI. QUALITY & VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SPEC COMPLETENESS
- No TODOs, assumptions, or placeholders
- All edge cases must be documented

2. SECURITY REVIEW
- Specs must pass Quality & Security Agent review
- Unreviewed specs are not eligible for code generation

3. FAILURE HANDLING
- All error scenarios must be explicitly defined
- Silent failures are forbidden

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VII. TERMINATION CONDITIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Once specs are complete and validated:
  - Agents must stop
  - Implementation may begin via Claude Code

- If ambiguity is detected:
  - Halt
  - Request spec clarification
```

## Response snapshot

Updated the project constitution file (.specify/memory/constitution.md) with the Phase-II System Constitution for a Full-Stack Todo Application. The new constitution includes seven core principles covering spec-driven development, no manual coding, monorepo mandate, incremental evolution, architecture constraints, security requirements, API contracts, agent governance, quality validation, and termination conditions. The constitution version is now 1.0.0 with ratification date 2026-01-13.

## Outcome

- ✅ Impact: Updated constitution file with Phase-II requirements for Full-Stack Todo Application
- 🧪 Tests: none
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: Continue with spec-driven development for the todo application
- 🧠 Reflection: The constitution now serves as the authoritative guide for all future development in the project

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin creating feature specifications based on the new constitution