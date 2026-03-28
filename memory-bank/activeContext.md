# Active Context

## Current Focus
- 2026-03-29: Keep the memory bank aligned with recent drag and drop UX changes and container-build workflow hardening.
- 2026-03-29: Validate the remaining drag and drop learner flow end-to-end inside the running LMS app, especially mixed text/image prompts and stepped navigation.
- 2026-03-29: Monitor GitHub Actions release builds after the `FRAPPE_REF` / `PAYMENTS_REF` split and action-version upgrades.

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

## Next Actions
- Continue frontend verification from the parent compose project using `docker compose exec frappe ...` instead of host-shell builds.
- Manually verify drag and drop activities end-to-end in the LMS UI, including authoring, mixed text/image items, mobile tap placement, sidebar access, stepped navigation, submission, and retry flows.
- Monitor GitHub Actions release runs to confirm the new `FRAPPE_REF` / `PAYMENTS_REF` validation produces clear failures when refs are wrong and that successful builds keep pushing to GHCR.
- Revisit the remaining Node 20 deprecation warning only when Docker publishes Node 24-ready action runtimes or when a test branch is ready to opt into forced Node 24 execution.
- Use the memory bank as the starting context for the next implementation or review task in this repo.
- Expand system notes when future work touches under-documented areas like payments, search indexing, or SCORM delivery.

## Blockers
- Host-shell frontend validation is misleading in this workspace because the app is meant to run inside Docker.
- Container-side frontend validation currently hangs in `vite build` when run as `docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench/apps/lms/frontend && yarn build'`.
- Remaining Node 20 deprecation warnings cannot be fully removed from the build workflow until Docker updates the affected GitHub Actions runtimes upstream.
