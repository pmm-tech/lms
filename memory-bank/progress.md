# Progress: Frappe LMS

## What Works

- **Core learning flow**: Courses (chapters, lessons), batches, enrollments, lesson progress, markdown lessons with macros (Exercise, Quiz, Video, Assignment, etc.).
- **Assessments**: Quizzes (single/multiple choice, open-ended), quiz submissions and results; assignments and assignment submissions; programming exercises with test cases.
- **Live classes**: Zoom integration; live class creation per batch; reminders and attendance updates.
- **Certification**: Certificate requests, evaluations (with evaluator slots and schedule), certificate generation and templates.
- **Payments**: Razorpay; coupons; payment reminders (daily job).
- **Programs**: Program definition, program courses, program members.
- **Jobs**: Job opportunities and job applications (Job module).
- **Profile & roles**: User profile (about, certificates, roles, evaluator slots); Course Creator, Moderator, Batch Evaluator, LMS Student.
- **Frontend**: Vue 3 SPA with full route set (courses, batches, lessons, quizzes, assignments, programs, statistics, job-openings, profile, etc.); Frappe UI components; PWA option.
- **Backend**: DocTypes, API whitelist, auth hook, scheduled tasks, doc events, SCORM page renderer, SQLite search index (background).
- **DevOps**: Docker setup; CI (GitHub Actions: build, linters, Cypress); semantic release; Crowdin for translations.

## What’s Left / Optional

- No single “in progress” feature list; the codebase is mature. New work is typically feature requests or bug fixes tracked in issues/PRs.
- Potential areas (from structure): more lesson macro types, additional payment gateways, richer analytics, mobile app (if ever desired).

## Current Status

- **Memory Bank**: Initialized. All six core files present and filled from repo analysis.
- **Codebase**: Develop branch; no uncommitted feature context beyond this initialization.
- **Known issues**: None specified here; see GitHub Issues and SECURITY.md for reporting.

## Summary

Frappe LMS is a feature-complete open-source LMS. The Memory Bank is ready for use: read it at the start of each task and update **activeContext.md** and **progress.md** as work progresses.
