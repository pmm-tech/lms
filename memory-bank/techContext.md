# Tech Context

## Stack
- Backend: Python 3.10+, Frappe Framework with declared compatibility from v15 through v17 dev.
- Frontend: Vue 3, Vue Router 4, Pinia, Vite 5, Frappe UI, Tailwind CSS, Chart.js/ApexCharts, CodeMirror, Editor.js.
- Integrations: Razorpay for payments, Zoom-related live class workflows, Crowdin translation pipeline, Cypress dashboard badge in README.
- Packaging and build: Flit for Python packaging, Yarn for frontend dependencies, Vite build output copied into Frappe-served assets and `_lms.html`.

## Setup
- Local Frappe workflow uses Bench: create a site, install the app, and run `bench start`.
- Docker workflow uses [`docker/docker-compose.yml`](/Users/purwaren/Projects/frappe/lms/docker/docker-compose.yml) and [`docker/init.sh`](/Users/purwaren/Projects/frappe/lms/docker/init.sh).
- 2026-03-20: In this workspace, the active runtime is driven from the parent compose project at `/Users/purwaren/Projects/frappe/frappe-learning/docker-compose.yml`, with the app mounted into the `frappe` service at `/home/frappe/frappe-bench/apps/lms`.
- Root `package.json` delegates frontend development and build commands into the `frontend/` workspace-like folder.
- Frontend dev server uses Vite with a local `frappe-ui` checkout when available, otherwise the npm package fallback.
- 2026-03-29: Container image builds are driven by `.github/workflows/build.yml` and now use `FRAPPE_REF` and `PAYMENTS_REF` repository variables, with backward compatibility for the older `FRAPPE_BRANCH` variable.

## Constraints
- The repo mixes Python, Frappe metadata, Vue, Cypress, and generated assets, so changes often need cross-layer validation.
- Route handling depends on a configurable `lms_path`; hardcoded `/lms` assumptions can regress custom deployments.
- Endpoint blocking in [`lms/auth.py`](/Users/purwaren/Projects/frappe/lms/lms/auth.py) can reject non-allowlisted API calls for non-system users.
- The backend surface is large, with many whitelisted methods in [`lms/lms/api.py`](/Users/purwaren/Projects/frappe/lms/lms/lms/api.py) and [`lms/lms/utils.py`](/Users/purwaren/Projects/frappe/lms/lms/lms/utils.py), so behavioral changes can have wide reach.
- Docker-backed verification may be more reliable than host-shell verification because node/yarn availability and dependency state differ between the host and the running `frappe` container.
- 2026-03-29: GitHub Actions build warnings about Node 20 deprecation still remain for the Docker-maintained actions (`docker/build-push-action`, `docker/login-action`, `docker/setup-buildx-action`, `docker/setup-qemu-action`) even after local workflow upgrades; this is currently an upstream action-runtime issue, not a repo-specific misconfiguration.

## Key Commands
- `bench start`
- `bench --site <site> install-app lms`
- `yarn dev`
- `yarn build`
- `yarn test-local`
- `ruff check .`
- `docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench/apps/lms/frontend && yarn build'`
- `git ls-remote --heads https://github.com/frappe/frappe <ref>`
- `git ls-remote --tags https://github.com/frappe/payments <ref>`
