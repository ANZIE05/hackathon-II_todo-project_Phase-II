---
id: 1
title: backend-spec
stage: spec
date: 2026-01-20
surface: agent
model: claude-sonnet-4-5-20250929
feature: backend-spec
branch: 001-backend-spec
user: claude
command: /sp.specify
labels: ["backend", "specification", "authentication", "api"]
links:
  spec: specs/001-backend-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-backend-spec/spec.md
  - specs/backend/overview.md
  - specs/backend/auth.md
  - specs/backend/api.md
  - specs/backend/middleware.md
  - specs/backend/db.md
  - specs/backend/errors.md
  - specs/backend/integration.md
  - specs/001-backend-spec/checklists/requirements.md
tests:
---

## Prompt

```text
You are executing /sp.specify for the BACKEND of Phase-II Full-Stack Todo Application.

You are strictly bound by:
- /sp.constitution
- Approved frontend specs under /specs/ui
- Existing API expectations under /specs/contracts

Your task is to produce COMPLETE, production-grade backend specifications
that can be implemented without ambiguity and integrate cleanly with the frontend.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I. SCOPE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This specification applies ONLY to the backend.

You MUST:
- Define backend behavior via specs only
- Cover auth, API, DB, middleware, and integration points
- Ensure frontend compatibility via existing contracts

You MUST NOT:
- Write FastAPI / Python code
- Modify frontend specs
- Invent UI behavior
- Hardcode secrets or credentials

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
II. TECH CONSTRAINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backend Framework:
- FastAPI

ORM:
- SQLModel

Database:
- Neon Serverless PostgreSQL
- Connection via environment variable: NEON_DB_URL

Authentication:
- JWT-based authentication
- Better Auth compatible
- Secrets via environment variables:
  - BETTER_AUTH_SECRET
  - BETTER_AUTH_URL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
III. ARCHITECTURE REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST define:

- Application startup behavior
- Dependency injection boundaries
- Middleware order
- Auth verification layer
- Request lifecycle (auth → validation → logic → response)

The backend must be:
- Stateless
- Secure by default
- Frontend-contract driven

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IV. AUTHENTICATION & AUTHORIZATION (CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST specify:

- Signup endpoint behavior
- Login endpoint behavior
- JWT creation & validation rules
- Token expiry handling
- Middleware-based token enforcement

Authorization Rules:
- Every protected endpoint REQUIRES valid JWT
- User identity is extracted from token
- All task queries MUST be user-scoped
- Cross-user access is strictly forbidden

Reference:
- @specs/auth/jwt.md
- @specs/contracts/auth-api.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
V. DATABASE & PERSISTENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST specify:

Entities:
- User
- Task

Relationships:
- One User → Many Tasks

Rules:
- Task ownership enforced at query level
- No orphaned tasks
- Deletions scoped to owner only

Persistence Expectations:
- SQLModel-compatible schema
- Neon PostgreSQL constraints
- Migration-ready design

Reference:
- @specs/db/schema.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VI. API SPECIFICATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST fully specify:

Task APIs:
- Create task
- List tasks (user-filtered)
- Update task
- Complete task
- Delete task

For EACH endpoint, define:
- HTTP method & path
- Auth requirement
- Request schema
- Response schema
- Error cases
- Status codes

Error behavior MUST follow:
- @specs/contracts/error-format.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VII. FRONTEND INTEGRATION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST ensure:

- API shapes exactly match frontend expectations
- JWT is accepted in Authorization headers
- Status codes are frontend-safe
- Error messages are non-sensitive
- Pagination / filtering behavior (if any) is explicit

Reference:
- @specs/ui/flows.md
- @specs/contracts/task-api.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VIII. ENVIRONMENT & CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST specify:

- Required environment variables (names only)
- Fail-fast behavior if env vars are missing
- Secure defaults
- Local vs production configuration expectations

You MUST NOT:
- Embed secrets
- Output actual credentials

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IX. DELIVERABLE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST output specs under:

/specs/backend/
  ├─ overview.md
  ├─ auth.md
  ├─ api.md
  ├─ middleware.md
  ├─ db.md
  ├─ errors.md
  └─ integration.md

Each file must be:
- Complete
- Explicit
- Implementation-ready
- Constitution-compliant

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
X. STOP CONDITIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Do NOT generate code
- Do NOT proceed to frontend or DB coding
- Stop once backend specs are complete
```

## Response snapshot

Complete backend specifications for the Phase-II Full-Stack Todo Application have been created, covering all required areas:

1. **Feature Specification** (specs/001-backend-spec/spec.md): Comprehensive feature specification with user scenarios, functional requirements, and success criteria.

2. **Backend Specifications** (specs/backend/):
   - overview.md: Architecture overview and core components
   - auth.md: Authentication endpoints, JWT specification, and authorization rules
   - api.md: Complete API endpoint specifications with request/response formats
   - middleware.md: Middleware layer specification including auth, logging, and security
   - db.md: Database schema, entity definitions, and relationships
   - errors.md: Error handling specification with standardized formats
   - integration.md: Integration requirements and environment configuration

All specifications follow the requirements, are implementation-ready, and maintain compatibility with frontend expectations while adhering to the technology constraints (FastAPI, SQLModel, Neon PostgreSQL, JWT authentication).

## Outcome

- ✅ Impact: Complete backend specification suite created for Phase-II Todo Application
- 🧪 Tests: N/A (specification work)
- 📁 Files: 9 specification files created across feature and backend directories
- 🔁 Next prompts: Ready for planning phase (/sp.plan)
- 🧠 Reflection: Specifications comprehensively cover all required backend aspects with clear implementation guidance

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin implementation planning