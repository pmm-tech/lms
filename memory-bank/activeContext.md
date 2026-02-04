# Active Context: Frappe LMS

## Current Focus

- **Initial memory bank setup**: All core Memory Bank files have been created and populated from a first-pass analysis of the repository. No specific feature or bug is in progress unless stated by the user.

## Recent Changes

- Created `memory-bank/` with:
  - `projectbrief.md` — scope, goals, requirements
  - `productContext.md` — why the product exists, problems, UX goals
  - `techContext.md` — stack, setup, paths, dependencies
  - `systemPatterns.md` — architecture, DocTypes, frontend/backend patterns
  - `activeContext.md` — this file
  - `progress.md` — what works, what’s left, status

## Next Steps

- Use the Memory Bank at the start of each task (read relevant files).
- When starting a concrete task: update **Current Focus** and **Next Steps** here; when finishing, update **progress.md** and optionally **Recent Changes**.
- If the user requests **update memory bank**: review all memory bank files and refresh them to current state.

## Active Decisions & Considerations

- **Base path**: LMS app is served under a configurable path (`lms_path` in site config or default `"lms"`); redirects and frontend base path must respect this.
- **Frappe version**: App targets Frappe 15–17; avoid relying on APIs outside that range.
- **Contributions**: Semantic commit messages; run tests and lint before PR (see Contribution.md and GitHub workflows).
