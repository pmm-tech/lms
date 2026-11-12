# Active Context

## Current Focus
- 2026-04-04: Keep the memory bank aligned with the new final-exam architecture, simplified CI workflow set, and Docker-based verification workflow.
- 2026-04-04: Preserve the remaining manual browser QA gap for the exam UI and course integration views.
- 2026-04-04: Review drag-and-drop learner interaction for remaining UI/UX friction after the one-at-a-time and touch-friendly changes.

## Recent Changes
- 2026-03-18: Reviewed repository docs, packaging files, hooks, auth layer, SPA router, frontend bootstrap, and test/CI surface.
- 2026-03-18: Rewrote all six memory-bank files into concise bullet-based records aligned with the memory-bank skill contract.
- 2026-03-18: Preserved the existing `memory-bank/` directory and treated this task as a refresh rather than creating empty starter files.
- 2026-03-20: Updated `frontend/src/components/DragDrop.vue` to use a tinted answer bank container, palette-based answer buttons, and clearer selected/drag/drop target states without changing submission payloads.
- 2026-03-20: Confirmed this app runs inside the parent Docker Compose project at `/Users/purwaren/Projects/frappe/frappe-learning/docker-compose.yml` and frontend verification should target the `frappe` container path `/home/frappe/frappe-bench/apps/lms`.
- 2026-03-20: Updated GitHub workflows to prefer `github.token` over a custom release token for repo-local release, note regeneration, PR automation, translation PRs, and GHCR publishing; also standardized several checkout actions and improved UI test artifact capture.
- 2026-03-20: Removed the duplicate `Semantic Commits` job from `.github/workflows/linters.yml` after confirming workflow failures were caused by commitlint, not the separate PR-title validation workflow. Repo rule is now to enforce semantic PR titles, not every commit message.
- 2026-03-21: Extended drag and drop activities to support mixed item rendering modes. Each row can now render as either text (`prompt_before`/`prompt_after`) or image (`image` + drop target), while keeping the same answer-bank and scoring flow.
- 2026-03-21: Added instructor navigation for drag and drop activities under the Quizzes area and updated the learner view to favor touch-friendly tap placement on mobile.
- 2026-03-21: Reworked the learner drag and drop flow to show one item at a time with Previous/Next navigation while keeping placements persistent across the whole activity.
- 2026-03-29: Merged `origin/develop` into `devel`, resolved the recurring `ui-tests.yml` conflict by keeping the secret-based Cypress key plus the newer parallel screenshot behavior, and pushed the merge to `origin/devel`.
- 2026-03-29: Hardened `.github/workflows/build.yml` by separating `FRAPPE_REF` and `PAYMENTS_REF`, validating upstream refs before Docker build, and upgrading workflow action versions where repo-controlled updates were available.
- 2026-03-29: Confirmed release builds now succeed after fixing the invalid `version-16` framework ref assumption; the remaining Node 20 deprecation warning comes from Docker-maintained actions still on their current major lines.
- 2026-04-04: Added a dedicated exam module with new DocTypes for exams, exam questions, prerequisites, submissions, and results, plus standalone exam routes and authoring/learner pages under `frontend/src/pages/Exam`.
- 2026-04-04: Integrated final exams into course detail payloads, course outline rendering, certification checks, and LMS navigation. Exams are course-level, can display under a selected chapter, and are required for certification when present.
- 2026-04-04: Added prerequisite evaluation for course progress, selected quizzes, and selected drag-and-drop activities with AND-only semantics and `Attempted` / `Passed` requirement modes.
- 2026-04-04: Live-verified the exam module inside the running `frappe` container with `bench migrate`, course detail/outline payload checks, a successful smoke exam submission path, member-specific prerequisite status checks, and certification gating checks.
- 2026-04-04: Fixed stale exam output during live verification by replacing cached exam loads with uncached `frappe.get_doc` calls in exam status helpers.
- 2026-04-04: Simplified the GitHub Actions footprint so PR validation centers on `ci.yml` and `linters.yml`, release images build from tags in `build.yml`, and UI tests are manual-only for now.
- 2026-04-04: Removed the local-repo Codecov upload path from `ci.yml`; coverage can still be generated without relying on a Codecov integration.
- 2026-04-04: Fixed the remaining local quality gates for the exam branch: Semgrep-reviewed guest endpoint suppressions are formatted cleanly, `pre_commit --all-files` passes in the `frappe` container, and container `yarn build` succeeds after moving problematic mobile lesson actions into named handlers.

## Next Actions
- Run a manual browser pass for the new exam UI on `/lms/exams`, `/lms/exams/:examID`, `/lms/exam/:examID`, and the course overview/outline exam surfaces.
- Decide whether to add editor-side chapter actions for attaching exams or keep chapter placement solely on the exam form for now.
- Continue frontend verification from the parent compose project using `docker compose exec frappe ...` instead of host-shell builds.
- Review drag-and-drop learner interaction for remaining friction in answer-bank focus, mobile paging, and step-by-step progression.
- Revisit the remaining Node 20 deprecation warning only when Docker publishes Node 24-ready action runtimes or when a test branch is ready to opt into forced Node 24 execution.

## Blockers
- Host-shell frontend validation is misleading in this workspace because the app is meant to run inside Docker.
- Remaining Node 20 deprecation warnings cannot be fully removed from the build workflow until Docker updates the affected GitHub Actions runtimes upstream.
- Playwright/browser automation is not available in this session, so exam verification is currently limited to Docker + Bench runtime checks plus any manual browser QA the user performs.
