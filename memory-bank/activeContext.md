# Active Context

## Current Focus
- 2026-03-18: Complete a comprehensive repo analysis and refresh the project memory bank to match the current codebase.
- 2026-03-18: Establish a reliable baseline for future feature work by documenting architecture, stack, constraints, and risks.
- 2026-03-20: Refresh the learner-facing drag and drop activity so the answer bank feels more colorful, interactive, and mobile-friendly.

## Recent Changes
- 2026-03-18: Reviewed repository docs, packaging files, hooks, auth layer, SPA router, frontend bootstrap, and test/CI surface.
- 2026-03-18: Rewrote all six memory-bank files into concise bullet-based records aligned with the memory-bank skill contract.
- 2026-03-18: Preserved the existing `memory-bank/` directory and treated this task as a refresh rather than creating empty starter files.
- 2026-03-20: Updated `frontend/src/components/DragDrop.vue` to use a tinted answer bank container, palette-based answer buttons, and clearer selected/drag/drop target states without changing submission payloads.
- 2026-03-20: Confirmed this app runs inside the parent Docker Compose project at `/Users/purwaren/Projects/frappe/frappe-learning/docker-compose.yml` and frontend verification should target the `frappe` container path `/home/frappe/frappe-bench/apps/lms`.

## Next Actions
- Continue frontend verification from the parent compose project using `docker compose exec frappe ...` instead of host-shell builds.
- Investigate why `yarn build` in the `frappe` container remains inside the Vite build phase for several minutes without completing.
- Use the memory bank as the starting context for the next implementation or review task in this repo.
- Expand system notes when future work touches under-documented areas like payments, search indexing, or SCORM delivery.

## Blockers
- No immediate blocker for initialization work.
- Deeper product or operational history still depends on external issues, PRs, and deployment context not stored in this repo.
- Host-shell frontend validation is misleading in this workspace because the app is meant to run inside Docker.
- Container-side frontend validation currently hangs in `vite build` when run as `docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench/apps/lms/frontend && yarn build'`.
