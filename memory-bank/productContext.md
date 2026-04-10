# Product Context

## Users
- Learners consuming courses, batches, live classes, assessments, and certificates.
- Instructors and course creators authoring lessons, quizzes, assignments, and programs.
- Moderators and evaluators reviewing content, assessments, and certificate requests.
- Operators managing payments, reminders, branding, jobs, and site-level LMS settings.

## Problems To Solve
- Reduce friction in launching and maintaining an online learning experience.
- Give course content clear structure with course -> chapter -> lesson progression.
- Keep instructor workflows lightweight while still supporting assessments, cohorts, and certifications.
- Let organizations pair learning with adjacent workflows like hiring and paid enrollments.

## UX Expectations
- The app should feel simpler and faster than traditional LMS products.
- Learner navigation should stay coherent across courses, batches, lessons, quizzes, assignments, and profile views.
- Instructor workflows should avoid overly long forms and expose role-specific actions clearly.
- The product should work well as a browser-based experience and remain mobile-friendly through the SPA and PWA setup.
- 2026-03-29: Drag and drop activities should feel usable on touch devices by supporting tap-to-select and tap-to-place, not only desktop drag gestures.
- 2026-03-29: Drag and drop assessment flows should avoid overwhelming learners; the current UX direction is one prompt at a time with Previous/Next navigation.
- 2026-04-04: Final exams should feel like a first-class assessment type with a standalone authoring/library flow, a learner-facing locked/unlocked state, and prerequisite explanations that tell learners exactly what is missing.
- 2026-04-04: If a course has a final exam, learners should still be able to reach normal 100% course progress while clearly seeing that certification remains blocked until the final exam is passed.
- 2026-04-04: Public course browsing should remain guest-accessible, but final-exam metadata and placement should only be enriched for authenticated learners so public discovery stays lightweight and safer.

## Acceptance Signals
- Public course browsing, enrollment, and lesson consumption are available from website routes under the LMS base path.
- Authenticated users receive role-aware UI and capabilities from boot/user API data.
- Scheduled reminders and operational jobs keep recurring workflows moving without manual intervention.
- The repo contains both Python tests around DocTypes and Cypress coverage for major UI flows.
- 2026-03-29: Drag and drop activities are accessible from LMS navigation under Quizzes for instructor-facing flows.
- 2026-04-04: Exams are accessible from LMS navigation like other assessment libraries, can be attached to courses, appear in the course outline and overview, and show locked prerequisite messaging for enrolled learners.
