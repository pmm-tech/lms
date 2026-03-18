# System Patterns

## Architecture Snapshot
- Monolithic Frappe app with Python backend under `lms/` and a Vue 3 SPA under `frontend/`.
- Website requests under `/{lms_path}` route to `_lms`, then the Vue router takes over client-side navigation.
- Persistent business entities are modeled as Frappe DocTypes under `lms/lms/doctype/` and `lms/job/doctype/`.
- Shared runtime behavior is centralized through Frappe hooks for install, routing, schedulers, doc events, Jinja helpers, and boot augmentation.

## Boundaries
- `lms/hooks.py` defines app wiring, website routing, scheduled jobs, doc events, and rendering extensions.
- `lms/lms/api.py` and `lms/lms/utils.py` hold a large portion of whitelisted LMS-facing server methods.
- `frontend/src/router.js` is the route map for the SPA and mirrors the product surface area.
- `lms/auth.py` adds request gating when `block_endpoints` is enabled for non-system users.
- `lms/plugins.py` and related renderers extend lesson content with markdown macros and specialized page rendering.

## Shared Patterns
- DocType-first design: business logic typically lives alongside the owning DocType in `.py`, `.js`, `.json`, and tests.
- SPA-in-shell pattern: Frappe serves bootstrapped HTML while Vue handles route transitions and most interaction state.
- Role-aware behavior: user capabilities are inferred from Frappe roles and surfaced to the frontend via boot data and `get_user_info`.
- Scheduled automation pattern: reminders, attendance updates, statistics refresh, and evaluation scheduling run through Frappe scheduler hooks.
- Content extensibility pattern: lessons support embedded exercises, quizzes, videos, assignments, audio, PDF, and SCORM-related flows.

## Decisions
- 2026-03-18: Keep LMS delivery inside a single Frappe app. Rationale: the repo couples routing, DocTypes, permissions, scheduled jobs, and frontend bootstrapping tightly. Impact: changes usually span hooks, DocTypes, and SPA routes instead of service boundaries.
- 2026-03-18: Use a Vue SPA mounted at a configurable `lms_path`. Rationale: one routed client app gives a modern UX while preserving Frappe website entry points. Impact: server routes and frontend base-path logic must stay aligned.
- 2026-03-18: Treat DocTypes as the primary domain boundary. Rationale: Frappe permissions, schema, forms, and tests all center on DocTypes. Impact: new features should usually start with schema and permission design, not standalone tables.
- 2026-03-18: Allow selective public access through whitelisted methods and route rules. Rationale: browsing courses and other public LMS surfaces must coexist with protected authoring and learner actions. Impact: API additions need explicit guest/auth decisions.
