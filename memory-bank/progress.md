# Progress

## Done
- 2026-03-18: Mapped the repo layout across backend, frontend, docs, Docker, Cypress, and GitHub workflows.
- 2026-03-18: Confirmed the project is a mature Frappe LMS with course delivery, batches, live classes, assessments, certificates, programs, jobs, and payments.
- 2026-03-18: Confirmed the frontend is a Vue 3 SPA with Pinia, Vue Router, Frappe UI, and PWA support.
- 2026-03-18: Confirmed the backend relies on Frappe hooks, DocTypes, whitelisted APIs, scheduled jobs, and an endpoint-allowlist auth gate.
- 2026-03-18: Initialized the memory bank in the required six-file layout with repo-specific content.
- 2026-03-20: Refreshed the learner-facing drag and drop answer bank with a colorful container, palette-based answer buttons, and clearer visual states for select, drag, and drop interactions in `frontend/src/components/DragDrop.vue`.
- 2026-03-20: Verified the active local runtime is the parent Docker Compose project, with frontend commands expected to run through `docker compose exec frappe ...` against `/home/frappe/frappe-bench/apps/lms`.
- 2026-03-20: Updated GitHub Actions workflows to use the built-in `github.token` for GHCR publishing and repo-local automation, added explicit permissions to more workflows, removed the hardcoded Cypress record key, removed the CI-time Cypress install step, and uploaded UI artifacts on every run.
- 2026-03-20: Removed duplicate commitlint enforcement from `.github/workflows/linters.yml` so semantic PR titles remain the single semantic convention gate.
- 2026-03-21: Added drag and drop item display modes with new `display_type` and `image` fields, backend validation for text vs image rows, authoring UI support for image prompts, learner-side image placeholder rendering, and result-schema support for image submissions.
- 2026-03-21: Added drag and drop navigation links under Quizzes, improved mobile interaction with tap-to-place UX, and changed the learner view to show one activity item at a time with Previous/Next navigation.
- 2026-03-29: Merged the latest `origin/develop` into `devel` and resolved the recurring Cypress workflow conflict in `.github/workflows/ui-tests.yml`.
- 2026-03-29: Hardened `.github/workflows/build.yml` by separating `FRAPPE_REF` from `PAYMENTS_REF`, validating upstream refs before build, and keeping LMS sourced from the executing repository/ref.
- 2026-03-29: Upgraded repo-controlled GitHub Action versions where available, including moving remaining `actions/checkout@v4` usages to `@v5` and `docker/login-action@v2` to `@v3`.
- 2026-03-29: Confirmed container image builds now succeed after correcting the invalid framework-ref assumption.
- 2026-04-04: Added a new course-level exam module with dedicated DocTypes for exams, questions, prerequisites, submissions, and results.
- 2026-04-04: Added standalone exam list/form/submission routes and learner-facing exam UI, plus course overview and outline integration for final exams.
- 2026-04-04: Added prerequisite evaluation for course progress, selected quizzes, and selected drag-and-drop activities, with configurable `Attempted` or `Passed` checks.
- 2026-04-04: Added certification gating so courses with a final exam require an exam pass before certificate issuance.
- 2026-04-04: Live-verified exam migrations, course detail/outline payloads, smoke submission, learner-specific prerequisite status, and final-exam certification blocking inside the running Dockerized Frappe site.
- 2026-04-04: Fixed stale exam status rendering by removing cached exam document reads from the live exam aggregation path.
- 2026-04-04: Simplified GitHub Actions around this fork's current needs by keeping PR lint/tests, tag-based builds, manual UI tests, and removing unused repo-local release automation workflows.
- 2026-04-04: Removed the unused Codecov upload job from `ci.yml`; coverage generation remains possible without a Codecov integration.
- 2026-04-04: Kept public course detail/outline endpoints guest-accessible while stripping final-exam enrichment for guests and documenting the reviewed exception with `nosemgrep` suppressions.
- 2026-04-04: Brought the local quality gates back to green: `python3 -m pre_commit run --all-files` passes inside the `frappe` container, and container-side `yarn build` now succeeds after fixing the exam import and lesson mobile action handlers.

## In Progress
- Manual browser verification for the exam module is still pending because only Docker + Bench runtime verification was completed in this session.
- Workflow observation is still in progress for the remaining Node 20 deprecation warning emitted by Docker-maintained GitHub Actions.
- Drag-and-drop learner UI/UX review is in progress to identify the next round of interaction improvements.

## Todo
- Keep the memory bank current as future feature work, fixes, and design decisions land.
- Add deeper historical notes when specific subsystems are modified or reviewed in detail.
- Run a browser-level exam QA pass covering authoring, learner lock states, unlocked attempts, course outline placement, and certificate button behavior.
- Review whether the remaining PR semantic action should also be pinned or replaced with a more stable dependency reference.
- Run targeted app-level tests or manual QA for drag and drop sidebar access, mobile/touch placement, and stepped item navigation once the local/container runtime is ready.
- Revisit Docker GitHub Actions versions when upstream publishes Node 24-ready runtime updates.

## Risks
- The API and DocType surface area is large, so changes can have non-obvious cross-feature effects.
- Route, auth, and guest-access behavior can regress if server rules and SPA assumptions diverge.
- Existing memory bank content can go stale quickly unless updated after each substantial task.
- Host-only frontend tooling can mislead verification because the canonical runtime in this workspace is the Dockerized `frappe` container.
- Some release jobs may still reveal hidden permission gaps once they run against GitHub, especially where branch pushes, PR creation, or release mutation depend on repository settings beyond workflow YAML.
- The remaining Docker-action Node 20 warnings can create alert fatigue even though the build currently succeeds, and they depend on upstream action runtime updates rather than repo-local YAML alone.
- The new exam feature crosses assessments, course aggregation, and certification logic, so regressions can appear in user flows that are not obviously “exam” screens.
