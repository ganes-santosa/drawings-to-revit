# Development log

Newest first. Record: structure changes, verified workflows, unresolved issues, lessons. Tested results themselves go to `references/` (+ `lessons-learned.md`).

## 2026-11-20 — v0.1 architecture established
- Replaced the single-file legacy skill `structural-drawings-to-revit` with a modular skill: `SKILL.md` orchestrator, 17 references, 4 workflows, `scripts/`, `assets/examples/`.
- Argument routing in SKILL.md §1–2 (keywords + aliases; leading keywords select route, remaining text = task; empty → full; unknown → keyword list + closest match). Mechanics verified against Claude Code 2.1.329 (`$ARGUMENTS`, `${CLAUDE_SKILL_DIR}`, `argument-hint`).
- Migrated legacy KPwBI knowledge into element/tool references, tagged `[VERIFIED KPwBI]`; standard-API content tagged `[THEORY]`.
- Added status-tag system, provenance labels (EXPLICIT/DERIVED/MEASURED/ASSUMED), conflict log format.
- Added `scripts/check_skill.py` (route/link integrity) and `scripts/pdf_calibrate.py` (piecewise calibration, tested on synthetic PDF).
- Environment: cloud container has no Revit. Live-test backlog created (`assets/examples/live-test-plan.md`); user can start Revit + MCP on request.

### Open issues
- All Revit-side API snippets untested in this setup (`[THEORY]`).
- Reinforcement, connections, stairs, walls have no field evidence.
- No tested standard for sheets/tags/dimensions/schedules.
- KPwBI placement/edge-test scripts were not preserved; rebuild and store verified versions.
