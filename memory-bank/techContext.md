# Tech Context: Frappe LMS

## Technologies

| Layer | Stack |
|-------|--------|
| Backend | Python 3.10+, Frappe Framework (15–17) |
| Frontend | Vue 3, Vite 5, Frappe UI, Pinia, Vue Router, Tailwind CSS |
| DB | MariaDB (production); SQLite supported (search index) |
| Build | flit (Python); yarn (frontend); Vite build → `/assets/lms/frontend/` |
| Linting/Format | Ruff, isort (Python); ESLint, Prettier (frontend); pre-commit |
| E2E | Cypress |

## Development Setup

- **Prerequisites**: bench (Frappe), Node/yarn, Python 3.10+.
- **Local**: `bench get-app`, `install-app lms`; `bench start`; frontend: `yarn dev` (from repo root or `frontend/`).
- **Docker**: `docker/docker-compose.yml` + `docker/init.sh`; site at `http://lms.localhost:8000/lms`.
- **Production**: Easy-install script or Frappe Cloud; image `ghcr.io/frappe/lms`.

## Key Paths

- **App root**: `lms/` (Python package; `app_name = "frappe_lms"`).
- **Modules**: `LMS`, `Job` (in `lms/modules.txt`). LMS doctypes live under `lms/lms/doctype/`.
- **Frontend**: `frontend/` — Vue SPA; entry served via `lms/www/_lms.html`; base path configurable (`lms_path`).
- **Website routes**: All `/{lms_path}/<path:app_path>` → `_lms` (see `hooks.py` `website_route_rules`).
- **API**: Whitelisted methods in `lms/lms/api.py` and doctype modules; auth allowlist in `lms/auth.py`.

## Dependencies (Notable)

- **Backend**: websocket_client, markdown, beautifulsoup4, lxml, cairocffi, razorpay, fuzzywuzzy; Frappe 15–17.
- **Frontend**: frappe-ui, vue, vue-router, pinia, codemirror, editorjs, apexcharts, socket.io-client, etc.

## Constraints

- Frappe version bound: `>=15.0.0,<=17.0.0-dev` (pyproject.toml).
- Frontend is a SPA; server renders `_lms` with boot context (csrf, site, lms_path); rest is client-side routing.
- Custom auth hook restricts non-LMS API paths when `block_endpoints` is set (auth.authenticate).
