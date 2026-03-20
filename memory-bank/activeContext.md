# Active Context

## Current Focus
- 2026-03-18: Complete a comprehensive repo analysis and refresh the project memory bank to match the current codebase.
- 2026-03-18: Establish a reliable baseline for future feature work by documenting architecture, stack, constraints, and risks.
- 2026-03-20: Refresh the learner-facing drag and drop activity so the answer bank feels more colorful, interactive, and mobile-friendly.
- 2026-03-20: Simplify GitHub Actions token usage by preferring the built-in `github.token` for repo-local automation and GHCR publishing.

## Recent Changes
- 2026-03-18: Reviewed repository docs, packaging files, hooks, auth layer, SPA router, frontend bootstrap, and test/CI surface.
- 2026-03-18: Rewrote all six memory-bank files into concise bullet-based records aligned with the memory-bank skill contract.
- 2026-03-18: Preserved the existing `memory-bank/` directory and treated this task as a refresh rather than creating empty starter files.
- 2026-03-20: Updated `frontend/src/components/DragDrop.vue` to use a tinted answer bank container, palette-based answer buttons, and clearer selected/drag/drop target states without changing submission payloads.
- 2026-03-20: Confirmed this app runs inside the parent Docker Compose project at `/Users/purwaren/Projects/frappe/frappe-learning/docker-compose.yml` and frontend verification should target the `frappe` container path `/home/frappe/frappe-bench/apps/lms`.
- 2026-03-20: Updated GitHub workflows to prefer `github.token` over a custom release token for repo-local release, note regeneration, PR automation, translation PRs, and GHCR publishing; also standardized several checkout actions and improved UI test artifact capture.
- 2026-03-20: Removed the duplicate `Semantic Commits` job from `.github/workflows/linters.yml` after confirming workflow failures were caused by commitlint, not the separate PR-title validation workflow. Repo rule is now to enforce semantic PR titles, not every commit message.

## Next Actions
- Continue frontend verification from the parent compose project using `docker compose exec frappe ...` instead of host-shell builds.
- Investigate why `yarn build` in the `frappe` container remains inside the Vite build phase for several minutes without completing.
- Watch the next GitHub Actions runs to confirm built-in token permissions are sufficient for release notes, weekly release PR creation, semantic release, and POT-file PR automation.
- Watch the next PR run to confirm `Validate PR title` remains the only semantic gate and that the removed commitlint check no longer blocks non-conventional commit messages.
- Use the memory bank as the starting context for the next implementation or review task in this repo.
- Expand system notes when future work touches under-documented areas like payments, search indexing, or SCORM delivery.

## Blockers
- No immediate blocker for initialization work.
- Deeper product or operational history still depends on external issues, PRs, and deployment context not stored in this repo.
- Host-shell frontend validation is misleading in this workspace because the app is meant to run inside Docker.
- Container-side frontend validation currently hangs in `vite build` when run as `docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench/apps/lms/frontend && yarn build'`.
- Built-in GitHub token behavior still needs live workflow confirmation for jobs that mutate releases or open PRs, even though the YAML permissions now match those intents.
