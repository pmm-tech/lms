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
- Assessment rendering pattern: drag and drop activities now support multiple item presentation modes while keeping one scoring payload shape (`submitted_answer` per row).
- Assessment specialization pattern: final exams reuse quiz-style question/submission mechanics where practical but live in dedicated DocTypes and routes so they can evolve separate metadata, prerequisite rules, and certification behavior.
- Container release pattern: the image build sources LMS from the executing repository/ref, while framework dependencies are controlled by explicit upstream refs validated before Docker build.

## Decisions
- 2026-03-18: Keep LMS delivery inside a single Frappe app. Rationale: the repo couples routing, DocTypes, permissions, scheduled jobs, and frontend bootstrapping tightly. Impact: changes usually span hooks, DocTypes, and SPA routes instead of service boundaries.
- 2026-03-18: Use a Vue SPA mounted at a configurable `lms_path`. Rationale: one routed client app gives a modern UX while preserving Frappe website entry points. Impact: server routes and frontend base-path logic must stay aligned.
- 2026-03-18: Treat DocTypes as the primary domain boundary. Rationale: Frappe permissions, schema, forms, and tests all center on DocTypes. Impact: new features should usually start with schema and permission design, not standalone tables.
- 2026-03-18: Allow selective public access through whitelisted methods and route rules. Rationale: browsing courses and other public LMS surfaces must coexist with protected authoring and learner actions. Impact: API additions need explicit guest/auth decisions.
- 2026-03-21: Keep drag and drop scoring uniform across text and image prompt types. Rationale: the backend already grades per item using submitted answer strings. Impact: new prompt types should reuse the same result and submission model instead of introducing a second grading path.
- 2026-03-21: Treat tap-to-place as the primary mobile interaction model for drag and drop. Rationale: native HTML drag events are unreliable on touch browsers. Impact: mobile UX should emphasize selection state and tappable drop targets rather than relying on drag-only affordances.
- 2026-03-21: Present drag and drop items one at a time with Previous/Next navigation. Rationale: the stepped flow is easier to use on mobile and less visually overwhelming than rendering every item at once. Impact: placement state must persist independently of the currently visible item.
- 2026-03-29: Separate LMS release refs from framework dependency refs in the container build pipeline. Rationale: assuming one shared branch name caused failed builds when `version-16` did not exist upstream. Impact: Frappe and Payments refs are now independently configurable and validated before build.
- 2026-04-04: Model the final exam as a course-level DocType instead of overloading lesson resources or quizzes. Rationale: the exam needs independent prerequisite logic, certification gating, attempt handling, and future exam-only metadata. Impact: exam state now spans dedicated DocTypes, course detail/outline aggregation, and certificate eligibility rules.
- 2026-04-04: Keep final exams outside normal course progress while making them mandatory for certification when present. Rationale: product wants progress to reach 100% before the exam while still treating the exam as a final gate. Impact: prerequisite checks use normal course progress, and certificate validation now performs an additional exam-pass check.
- 2026-04-04: Use `frappe.get_doc` instead of `frappe.get_cached_doc` when assembling live exam status for course payloads. Rationale: cached exam docs caused stale `display_chapter` and status output during live verification. Impact: course outline/detail responses now reflect exam edits immediately.
- 2026-04-04: Keep guest-whitelisted course endpoints for public browsing, but strip final-exam enrichment for guests and document the intentional exception with reviewed `nosemgrep` comments. Rationale: the product needs public course pages while Semgrep requires explicit review of guest-exposed methods. Impact: guest course detail/outline payloads stay public, but exam metadata is only added for authenticated users.
- 2026-04-04: Refactor template actions into named handlers when inline Vue expressions fight Prettier or the Vite parser. Rationale: the mobile lesson action buttons were stuck in a formatter/build conflict. Impact: local `pre_commit --all-files` and container `yarn build` are now both reliable gates.
