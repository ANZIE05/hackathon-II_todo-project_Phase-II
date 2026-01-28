<!-- SYNC IMPACT REPORT:
Version change: N/A -> 1.0.0
Modified principles: N/A (new constitution)
Added sections: Core Development Principles, Architecture Constraints, Security & Authorization Rules, API & Contract Rules, Agent Governance, Quality & Validation, Termination Conditions
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ updated
  - .specify/templates/spec-template.md ✅ updated
  - .specify/templates/tasks-template.md ✅ updated
  - .specify/templates/commands/*.md ⚠ pending
Follow-up TODOs: None
-->

# Full-Stack Todo Application Constitution

## Core Development Principles

### I. Spec-Driven Development Only
All behavior must be defined in specs before implementation. Specs are the single source of truth. No implicit logic is allowed.

### II. No Manual Coding
Humans do not write application code. All code is generated strictly from specs. Any missing behavior must be added to specs first.

### III. Monorepo Mandate
Frontend and backend live in the same repository. Clear separation of concerns is required.

### IV. Incremental Evolution
Phase-I console app concepts evolve into Phase-II web app. No regression of previously defined behavior.

## Architecture Constraints

### Frontend Requirements
Next.js (App Router) with JWT-based authentication (Better Auth compatible). Must consume REST API only.

### Backend Requirements
FastAPI with SQLModel ORM. JWT authentication required for ALL endpoints.

### Database Requirements
Neon Serverless PostgreSQL with persistent storage mandatory. No in-memory persistence allowed.

## Security & Authorization Rules

### Zero Trust Model
Every API request MUST include a valid JWT. No public or anonymous endpoints (except auth).

### User Isolation
Users can ONLY access their own tasks. Ownership must be enforced at query level.

### Token Enforcement
JWT verification happens before business logic. Expired or invalid tokens result in immediate rejection.

### No Data Leakage
No cross-user reads or writes. Error responses must not expose sensitive data.

## API & Contract Rules

### REST API Only
No GraphQL or RPC patterns.

### Explicit Contracts
Every endpoint must define: Request schema, Response schema, Error schema, Status codes.

### Consistency
Frontend and backend must rely on the same contracts. Contract changes require spec updates.

## Agent Governance

### Product/Spec Orchestrator Authority
Has final authority on specs. Coordinates all agents.

### Agent Scope Limits
Each agent must operate only within its defined role. Agents may reference other specs but not override them.

### Sub-Agent Constraints
Must defer to main agent decisions. Cannot introduce new requirements independently.

## Quality & Validation

### Spec Completeness
No TODOs, assumptions, or placeholders. All edge cases must be documented.

### Security Review
Specs must pass Quality & Security Agent review. Unreviewed specs are not eligible for code generation.

### Failure Handling
All error scenarios must be explicitly defined. Silent failures are forbidden.

## Termination Conditions

Once specs are complete and validated: Agents must stop. Implementation may begin via Claude Code.

If ambiguity is detected: Halt. Request spec clarification.

## Governance

This constitution is the highest authority. All agents, sub-agents, and generated outputs MUST comply with it. All behavior must follow spec-driven development principles. No manual coding is allowed without corresponding spec updates.

**Version**: 1.0.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-01-13