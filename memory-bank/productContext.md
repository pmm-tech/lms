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

## Acceptance Signals
- Public course browsing, enrollment, and lesson consumption are available from website routes under the LMS base path.
- Authenticated users receive role-aware UI and capabilities from boot/user API data.
- Scheduled reminders and operational jobs keep recurring workflows moving without manual intervention.
- The repo contains both Python tests around DocTypes and Cypress coverage for major UI flows.
