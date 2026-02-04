# Product Context: Frappe LMS

## Why This Project Exists

Born from the need to launch [Mon.School](https://mon.school) for FOSS United (2021). Existing options (e.g. Moodle) felt heavy—lengthy forms, confusing UI. The goal: a simple platform for anyone to launch a course and share knowledge.

## Problems It Solves

- **Content structure**: Clear course → chapter → lesson hierarchy so lessons have context.
- **Instructor workflow**: Create courses, chapters, lessons; add quizzes/assignments; run batches and live classes; issue certificates—without overwhelming forms.
- **Learner experience**: Discover courses, enroll in batches, follow lessons, take quizzes, submit assignments, attend live classes, earn certificates—all in a single coherent app.
- **Monetization & operations**: Payments (Razorpay), coupons, payment reminders; batch reminders; certificate evaluations; job board for opportunities.

## How It Should Work

- **Instructors/Moderators**: Create and publish courses; create batches and timetables; schedule Zoom live classes; evaluate certificate requests; manage job openings.
- **Learners**: Browse courses/batches; enroll (free or paid); progress through lessons; attempt quizzes and assignments; join live classes; request certificates; view profile, badges, certificates.
- **Evaluators**: Fulfill certificate evaluation slots; mark evaluations complete.
- **Guests**: Limited access when `allow_guest_access` is enabled (e.g. browse, limited reads).

## User Experience Goals

- Simple, fast forms; minimal cognitive load.
- Modern UI (Vue 3, Frappe UI, Tailwind).
- Mobile-friendly and PWA-capable.
- Clear roles: Course Creator, Moderator, Batch Evaluator, LMS Student.

## Key Product Areas

| Area | Description |
|------|-------------|
| Courses | Title, description, image, category, instructors, chapters, lessons, reviews, ratings |
| Batches | Linked to course(s), duration, timetable, enrollments, live classes |
| Lessons | Rich content (markdown), macros (Exercise, Quiz, Video, Assignment, etc.), progress tracking |
| Quizzes / Assignments | Standalone and embeddable; submissions and grading |
| Live Classes | Zoom integration; schedule per batch; reminders and attendance |
| Certificates | Request → evaluation → certificate; templates and print format |
| Programs | Multi-course programs; program members and progress |
| Jobs | Job opportunities and applications (Job module) |
| Profile | About, certificates, roles, evaluator slots, schedule |
