# Docker & Production Deployment: Gap Analysis and Improvement Plan

## 1. Gap Analysis

### 1.1 Build workflow (`.github/workflows/build.yml`)

| Gap | Severity | Description |
|-----|----------|-------------|
| **Build does not use current repo/commit** | High | `APPS_JSON` is hardcoded to `https://github.com/frappe/lms` and branch `main`. The image is always built with LMS code from `frappe/lms` main, not from the commit being built. Forks or pushes to `develop` produce images that do not contain their code. |
| **Branch trigger only on `main`** | Medium | Workflow runs on push to `main` and on tags. If the default branch is `develop`, pushes to `develop` never build an image. |
| **Image tag logic** | Low | `IMAGE_TAG` is always set to `stable`. When building from a tag (e.g. `v1.2.3`), it would be better to also push with that version tag; currently only `github.ref_name` and `stable` are used. |
| **Duplicate checkout** | Low | Repository is checked out twice (lms repo then frappe_docker). The first checkout is unused for the build because APPS_JSON points to GitHub; after fixing APPS_JSON, the first checkout is still not used by the Containerfile (which uses APPS_JSON_BASE64). So the build context is frappe_docker only; the image installs apps from JSON. To build “this repo’s code” we must pass the current repo URL and ref in APPS_JSON. |

### 1.2 Production Docker Compose

| Gap | Severity | Description |
|-----|----------|-------------|
| **No production compose in repo** | High | Only development compose exists (`docker/docker-compose.yml`). It uses `frappe/bench:latest`, mounts the repo, and runs `init.sh` (bench init + get-app + new-site). Production deployment is documented only via `easy-install.py` and pre-built image `ghcr.io/frappe/lms`. There is no docker-compose YAML in the repo for self-hosted production (single-server with MariaDB + Redis + app). |
| **No production env example** | Medium | No `.env.example` or similar for production (e.g. `DB_PASSWORD`, `CUSTOM_IMAGE`, `CUSTOM_TAG`, site name). Teams must infer from frappe_docker docs. |
| **Dev compose not suitable for prod** | High | Dev compose is for local try-out: fixed DB password, developer_mode, no gunicorn/workers/scheduler/nginx, single process. Production needs multiple services (backend, frontend, websocket, queue, scheduler) and external DB/Redis or included MariaDB/Redis. |

### 1.3 Development Docker

| Gap | Severity | Description |
|-----|----------|-------------|
| **init.sh shebang** | Low | Shebang is `#!bin/bash`; should be `#!/bin/bash` for correct interpreter. |
| **get-app source** | Low | `init.sh` runs `bench get-app lms` with no path; in the current setup the app is cloned from Git (default). When the repo is mounted at `/workspace`, the script does not install from `/workspace`; so the dev compose as documented (wget compose + init.sh) does not use local code. Fix is optional if the goal is “run from Git”; otherwise document or add logic to use mounted app. |

### 1.4 Documentation

| Gap | Severity | Description |
|-----|----------|-------------|
| **No “Production with Docker Compose”** | Medium | README and docker-installation.md describe easy-install and dev Docker only. No step-by-step for: pull/build image, run production compose, create site, install LMS. |
| **LMS-specific env vars** | Low | No central place documenting production-related LMS or Frappe env vars (e.g. `block_endpoints`, `lms_path`) when using Docker. |

---

## 2. Improvement Plan

### 2.1 Build workflow (recommended)

- **Use current repository and ref for APPS_JSON**
  - Set `APPS_JSON` to the repo and ref being built, e.g. `${{ github.server_url }}/${{ github.repository }}` and branch/tag from `github.ref` (e.g. `refs/heads/main` → `main`, `refs/tags/v1.0.0` → `v1.0.0`).
  - This way the built image contains the LMS code from the commit that triggered the workflow (important for forks and for `develop` if we add it).
- **Optional: trigger on `develop`**
  - Add `develop` to `push.branches` if you want to build and push images from `develop` (e.g. tag `develop` or `latest-dev`). Otherwise keep build only for `main` and tags.
- **Smarter image tags**
  - On tag push: set `IMAGE_TAG` to the tag name (e.g. `v1.2.3`) and push that; optionally also push `stable` from `main`.
  - On branch push: keep `IMAGE_TAG=stable` for `main`; for `develop` use e.g. `IMAGE_TAG=develop`.
- **Keep using frappe_docker’s Containerfile**
  - No need for an in-repo Dockerfile unless you want to maintain a custom build; the layered Containerfile with build-args is sufficient once APPS_JSON and tags are fixed.

### 2.2 Production Docker Compose (recommended)

- **Add a production compose file** (e.g. `docker/docker-compose.production.yml`) that:
  - Uses the same service layout as frappe_docker’s production pattern: **configurator**, **backend**, **frontend** (nginx), **websocket**, **queue-short**, **queue-long**, **scheduler**.
  - Uses **CUSTOM_IMAGE** / **CUSTOM_TAG** (e.g. `ghcr.io/frappe/lms:stable`) so deployers can override with their own image.
  - Adds **Redis** (redis-cache, redis-queue) and **MariaDB** (database) in the same file so one `docker compose up` brings up the full stack.
  - Sets **DB_HOST**, **DB_PORT**, **REDIS_CACHE**, **REDIS_QUEUE** (and **DB_PASSWORD** via env) so the configurator and backend use the included DB and Redis.
  - Uses **volumes** for sites, DB data, and Redis queue data; **restart** policy `unless-stopped`; **healthcheck** on MariaDB where useful.
- **Add an example env file** (e.g. `docker/env.production.example`) with:
  - `DB_PASSWORD`, `CUSTOM_IMAGE`, `CUSTOM_TAG`, and any LMS/Frappe vars (e.g. site name / `FRAPPE_SITE_NAME_HEADER` if needed).
  - Comments so deployers know what to change. (Copy to `.env` in the same directory; `.env` is gitignored.)

### 2.3 Development Docker (optional)

- Fix **init.sh** shebang to `#!/bin/bash`.
- Optionally: document that current dev compose installs LMS from Git; if “run from local source” is required, add a variant or env to install from mounted path instead of `bench get-app lms`.

### 2.4 Documentation (recommended)

- Add a short **“Production deployment with Docker Compose”** section (in README or docker-installation.md or both) that:
  - References the new production compose and env example.
  - Steps: copy `docker/env.production.example` to `docker/.env`, set `DB_PASSWORD`, `CUSTOM_IMAGE`/`CUSTOM_TAG`, run `docker compose -f docker-compose.production.yml up -d` from the `docker` directory, then create site and install app (e.g. `docker compose exec backend bench new-site ...` and `bench --site <site> install-app lms`).
- Optionally add a line about LMS-specific config (e.g. `block_endpoints`, `lms_path`) in the same section.

---

## 3. Summary Table

| Item | Action |
|------|--------|
| Build uses current repo/ref | Change APPS_JSON to `${{ github.repository }}` and ref (branch or tag). |
| Image tags | Derive IMAGE_TAG from ref (tag name or `stable`/`develop`). |
| Production compose | Add `docker/docker-compose.production.yml` (app + MariaDB + Redis). |
| Production env | Add `docker/env.production.example`. |
| Dev init.sh | Fix shebang to `#!/bin/bash`. |
| Docs | Add “Production with Docker Compose” and reference new files. |

---

## 4. What You Will Get After Implementation

1. **GitHub workflow**  
   - Builds an image that contains the LMS code from the commit being built (branch or tag).  
   - Pushes to GHCR with ref-based tags (e.g. `main`, `develop`, `v1.2.3`) and optional `stable`/`develop`.

2. **Production deploy with Docker**  
   - Single `docker compose -f docker/docker-compose.production.yml --env-file .env up -d` (after configuring `.env`) to run MariaDB, Redis, and all Frappe/LMS services.  
   - Clear steps to create site and install LMS after first bring-up.

3. **Docs**  
   - One place that describes production Docker Compose and points to the new files.

---

## 5. Implementation Status (for review)

The following have been added or changed for your review:

| Item | Status | Location |
|------|--------|----------|
| Gap analysis & plan | Done | This document |
| Production compose | Done | `docker/docker-compose.production.yml` |
| Production env example | Done | `docker/env.production.example` |
| Build workflow (repo/ref + tags) | Done | `.github/workflows/build.yml` |
| init.sh shebang | Done | `docker/init.sh` |
| README / docker-installation.md | Pending | Add "Production with Docker Compose" section |

After you approve, the only remaining step is adding the "Production with Docker Compose" section to README or docker-installation.md.
