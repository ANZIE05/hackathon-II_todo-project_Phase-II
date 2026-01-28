---
id: 2
title: Create Frontend UI Specifications
stage: spec
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5-20250929
feature: frontend-todo-ui
branch: 001-frontend-todo-ui
user: claude
command: /sp.specify
labels: [ui, frontend, todo-application, nextjs, authentication, jwt]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-frontend-todo-ui/spec.md
 - specs/ui/pages.md
 - specs/ui/flows.md
 - specs/ui/components.md
 - specs/ui/states.md
 - specs/ui/navigation.md
 - specs/001-frontend-todo-ui/checklists/requirements.md
tests:
 - none
---

## Prompt

```text
You are executing /sp.specify for the FRONTEND of Phase-II Full-Stack Todo Application.

You must produce complete, professional-grade frontend specifications.

You are bound by /sp.constitution.
Violating the constitution is forbidden.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I. SCOPE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This specification applies ONLY to the frontend.

You must NOT:
- Write React or Next.js code
- Define backend behavior
- Invent APIs or authentication logic
- Bypass API contracts

You must:
- Specify UI behavior, structure, and flows
- Reference API contracts via @specs/contracts/...
- Reference auth specs via @specs/auth/...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
II. TECH CONSTRAINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Framework: Next.js (App Router)
- Architecture: App Router only
- Auth: JWT-based (Better Auth compatible)
- Communication: REST APIs only
- State: Client-side auth + server-safe routing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
III. UI QUALITY REQUIREMENTS (CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The UI must be:

✔ Professional
✔ Clean & minimal
✔ Accessible
✔ Mobile-first responsive
✔ Suitable for production SaaS apps

Design expectations:
- Clear visual hierarchy
- Consistent spacing & typography
- Logical grouping of actions
- Friendly empty states
- Explicit loading & error states

No:
- Cluttered layouts
- Over-styled visuals
- Experimental UX
- Hidden functionality

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IV. REQUIRED PAGES & ROUTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST define specs for:

1. Public Routes
- Login page
- Signup page

2. Protected Routes (JWT required)
- Dashboard (task overview)
- Create task
- Edit task
- Task list (active / completed)
- User session handling

3. System States
- Loading
- Unauthorized
- Session expired
- API failure

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
V. UI BEHAVIOR SPECIFICATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For EACH page, define:

- Page purpose
- Route path
- Required auth state
- UI components (logical, not code)
- User interactions
- API calls (referenced, not defined)
- Success & failure flows

You must include:

- Form validation rules (UX-level)
- Button states (idle, loading, disabled)
- Error feedback placement
- Navigation behavior

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VI. AUTH & SECURITY BEHAVIOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- JWT stored securely (spec-level, no implementation)
- Protected routes must reject unauthenticated users
- Redirect rules must be explicit
- Logout must fully clear session state

Reference:
- @specs/auth/jwt.md
- @specs/contracts/auth-api.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VII. API INTEGRATION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Frontend MUST rely solely on API contracts
- No assumptions about backend behavior
- All requests must include JWT
- Error handling must follow contract specs

Reference:
- @specs/contracts/task-api.md
- @specs/contracts/error-format.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VIII. DELIVERABLE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You must output specs under:

/specs/ui/
  ├─ pages.md
  ├─ flows.md
  ├─ components.md
  ├─ states.md
  └─ navigation.md

Each file must be complete and unambiguous.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IX. STOP CONDITIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Do NOT generate implementation code
- Do NOT proceed to backend specs
- Stop once frontend specs are complete
```

## Response snapshot

Created comprehensive frontend specifications for the Phase-II Todo Application following the constitution requirements. Generated 5 specification files under /specs/ui/: pages.md, flows.md, components.md, states.md, and navigation.md. Also created the main feature spec file and a quality checklist. All specifications focus on UI behavior, structure, and flows while referencing API contracts and maintaining clean, professional design standards as required.

## Outcome

- ✅ Impact: Complete frontend UI specifications created for Todo Application
- 🧪 Tests: none
- 📁 Files: specs/001-frontend-todo-ui/spec.md, specs/ui/pages.md, specs/ui/flows.md, specs/ui/components.md, specs/ui/states.md, specs/ui/navigation.md, specs/001-frontend-todo-ui/checklists/requirements.md
- 🔁 Next prompts: Proceed to planning phase with /sp.plan
- 🧠 Reflection: Specifications are complete and follow all constitution requirements for frontend development

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): All specifications meet quality standards
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin planning implementation based on these specs