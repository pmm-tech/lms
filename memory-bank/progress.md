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

## In Progress
- Frontend verification for the drag and drop refresh is still in progress because the containerized `yarn build` does not complete after entering the Vite transform/build phase.
- Workflow cleanup still needs live GitHub run verification to confirm every release-related job works with built-in token permissions.
- Workflow cleanup still needs live PR verification to confirm the semantic gate now comes only from PR title validation.

## Todo
- Keep the memory bank current as future feature work, fixes, and design decisions land.
- Add deeper historical notes when specific subsystems are modified or reviewed in detail.
- Diagnose why `docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench/apps/lms/frontend && yarn build'` hangs during `vite build`.
- Review whether the remaining PR semantic action should also be pinned or replaced with a more stable dependency reference.

## Risks
- The API and DocType surface area is large, so changes can have non-obvious cross-feature effects.
- Route, auth, and guest-access behavior can regress if server rules and SPA assumptions diverge.
- Existing memory bank content can go stale quickly unless updated after each substantial task.
- Host-only frontend tooling can mislead verification because the canonical runtime in this workspace is the Dockerized `frappe` container.
- Long-running or stuck container builds can leave background `vite build` processes behind if verification attempts are not cleaned up.
- Some release jobs may still reveal hidden permission gaps once they run against GitHub, especially where branch pushes, PR creation, or release mutation depend on repository settings beyond workflow YAML.
