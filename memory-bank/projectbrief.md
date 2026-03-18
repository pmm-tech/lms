# Project Brief

## Goal
- Deliver an open-source LMS that is simpler to launch and operate than heavyweight alternatives.
- Support end-to-end learning workflows: authoring, enrollment, delivery, assessment, certification, and follow-on hiring.
- Fit naturally into the Frappe ecosystem so teams can self-host, extend, and administer it with standard Frappe patterns.

## Non-Goals
- Recreate the full breadth and configuration complexity of Moodle-class platforms.
- Split backend and frontend into separately deployed services.
- Store business data outside Frappe DocTypes as a primary persistence model.

## Success Criteria
- Instructors can publish structured courses with chapters and lessons.
- Learners can enroll, complete lessons, take quizzes, submit assignments, and earn certificates.
- Operators can run batches, live classes, reminders, payments, and evaluations from one app.
- Contributors can develop locally with Bench or Docker and validate changes with automated checks.

## Scope Notes
- In scope: courses, lessons, batches, quizzes, assignments, programming exercises, certificates, payments, profiles, badges, jobs, programs, search, and statistics.
- In scope: website delivery under a configurable LMS base path and a Vue SPA mounted inside Frappe.
- Out of scope: native mobile clients and multi-service deployment orchestration in this repo.
