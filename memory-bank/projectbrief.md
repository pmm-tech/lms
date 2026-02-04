# Project Brief: Frappe LMS

## Overview

**Frappe Learning** (LMS) is an easy-to-use, open-source Learning Management System built on the Frappe Framework. It helps organizations bring structure to educational content and run courses with live classes, quizzes, assignments, and certifications.

## Core Requirements & Goals

- **Structured learning**: 3-level hierarchy — Courses → Chapters → Lessons. Context is set by chapter.
- **Live classes**: Batches group learners by course and duration; Zoom live classes can be created from the app; learners see their live class list per batch.
- **Assessments**: Quizzes (single/multiple choice, open-ended), assignments (PDF/document submission), programming exercises with test cases.
- **Certification**: Grant certificates on course/batch completion; built-in certificate template or custom templates.
- **Jobs module**: Job opportunities and applications (separate Job module under `lms/job/`).
- **Programs**: Multi-course programs with membership and progress.
- **Modern UX**: Vue 3 + Frappe UI frontend; simple forms and clear navigation (inspired by Mon.School / FOSS United needs).

## Scope

- **In scope**: Course authoring, batch management, enrollments, lessons (markdown + macros), quizzes, assignments, live classes (Zoom), certificates, evaluations, payments (Razorpay), profiles, badges, discussions, job openings, programs, statistics, PWA.
- **Out of scope**: Full Moodle-level complexity; the aim is simplicity over feature breadth.

## Source of Truth

- This document defines project scope. Product context, tech context, system patterns, active context, and progress build on it.
