# System Patterns: Frappe LMS

## Architecture Overview

- **Monolith**: Single Frappe app; backend (Python/Frappe) + frontend (Vue SPA) in one repo.
- **Request flow**: Browser → Frappe site → `/{lms_path}` or `/{lms_path}/<path>` → `_lms` view → Jinja renders HTML with boot data → Vue app mounts; subsequent navigation is client-side; data via Frappe `call()` (whitelisted methods).
- **DocTypes**: Core entities (LMS Course, LMS Batch, Course Chapter, Course Lesson, LMS Enrollment, LMS Quiz, LMS Certificate, etc.) in `lms/lms/doctype/`. Job module: `lms/job/doctype/` (Job Opportunity, LMS Job Application, etc.).

## Key Design Decisions

1. **SPA under Frappe**: All LMS UI lives under a configurable base path (`lms_path`); one HTML shell, one Vue app; routes in `frontend/src/router.js`.
2. **Whitelisted API**: Backend exposes `@frappe.whitelist()` methods (e.g. in `lms/lms/api.py`); frontend uses `call("lms.lms.api.method_name", { ... })` or Frappe client APIs.
3. **DocType-centric**: All persistent data is Frappe DocTypes; no separate ORM. Business logic in doctype `.py` files and shared utils (`lms/lms/utils.py`).
4. **Hooks**: Install/roles in `install.py`; doc_events, scheduler_events, website_route_rules, page_renderer (SCORM), jinja methods, extend_bootinfo in `hooks.py`.
5. **Markdown macros**: Lesson content supports macros (Exercise, Quiz, YouTube, Video, Assignment, Embed, Audio, PDF) via `lms_markdown_macro_renderers`; implemented in `lms/plugins.py`.

## Component Relationships

- **Course** → Course Chapter → Course Lesson; Course Instructor; LMS Course Progress; LMS Enrollment (batch-level).
- **LMS Batch** → Batch Course; LMS Batch Enrollment; LMS Batch Timetable; LMS Live Class (Zoom).
- **LMS Certificate Request** → LMS Certificate Evaluation → LMS Certificate.
- **LMS Quiz** → LMS Question (with LMS Option); LMS Quiz Submission / LMS Quiz Result.
- **LMS Assignment** → LMS Assignment Submission.
- **LMS Program** → LMS Program Course; LMS Program Member.
- **Job** → Job Opportunity; LMS Job Application (separate module).

## Frontend Structure

- **Router**: `router.js` — routes for Home, Courses, CourseDetail, Lesson, Batches, Batch/BatchDetail, Profile (and children), Jobs, Quizzes, Assignments, Programs, Certifications, Statistics, etc.; base path from `getLmsBasePath()`.
- **Stores**: Pinia (e.g. session, user, settings); data often via `createResource` or `call` from frappe-ui.
- **Pages**: `frontend/src/pages/` — one (or more) Vue component per route; reusable components in `components/`.
- **Auth**: Login/guest handled by Frappe; frontend checks user/roles from boot or `get_user_info`.

## Backend Patterns

- **Permissions**: Role-based (Course Creator, Moderator, Batch Evaluator); `has_website_permission` for certificates; `can_modify_course` / `can_modify_batch` helpers.
- **Scheduled tasks**: Hourly (evals, course stats, live class attendance); daily (payment/batch/live class reminders, published course notifications); SQLite search index (all).
- **Document events**: e.g. badge processing on any doc change; discussion reply notifications; user validation; notification log publish.

## Security

- **Auth hook**: `lms.auth.authenticate` — when `block_endpoints` is set, only allowed paths and `/api/method/lms.*` (and server script/custom app) are permitted.
- **Guest access**: Controlled by LMS Settings; guest-only APIs use `@frappe.whitelist(allow_guest=True)` where appropriate.
