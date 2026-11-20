# Development log

Newest first. Record: structure changes, verified workflows, unresolved issues, lessons. Tested results themselves go to `references/` (+ `lessons-learned.md`).

## 2026-11-20 — v1.0.0 release
- First tagged release: modular skill + full KPwBI legacy knowledge (v0.1–v0.3 below). Revit-side procedures remain `[IMPORTED]`/`[THEORY]` until live tests.

## 2026-11-20 — v0.3 legacy knowledge fully integrated
- Archived the original single-file skill verbatim: `assets/legacy/structural-drawings-to-revit-v1-KPwBI.md` + mapping README.
- Compared every legacy item with the modular skill. Added what had been lost or generalised away:
  - SKILL.md: "User working preferences" block; dependency-driven build order (height chain: slab → beam → column base → cap); "drawn-but-missing is worse than a flagged estimate".
  - New route `views` + `references/views-and-documentation.md` (inspection views, filters, naming, template-filter gotcha).
  - Real KPwBI names restored (BALOK BETON PERSEGI, KOLOM BAJA …, PELAT …, PONDASI …), mark patterns, eccentric-beam examples, profile-letter table example, metal-deck build-up.
  - Typical Indonesian DED sheet order and title words; pile glyph detail; inference examples.
  - Project log template: height chain, non-obvious coordinates, truss geometry record.
  - 7 missing troubleshooting rows.
- Open: the installed plugin `structural-drawings-to-revit` still exists and overlaps this skill; disable it once this skill is trusted.

## 2026-11-20 — v0.2 local sync and tag cleanup
- Project now developed locally (D:/Outpost/Coding/str-to-revit); GitHub is a backup, push/pull only on request.
- Environment record corrected: local Windows machine, Revit 2026 installed, MCP tools present, Revit not running -> connection failed.
- Retagged all `[VERIFIED KPwBI]` / `[VERIFIED container]` to `[IMPORTED ...]`; added `[IMPORTED]` to the tag table. `[VERIFIED]` now means run in this setup.
- Skill-syntax claim now cites the official docs instead of an unchecked binary version.
- Command hints use `python` (Windows) instead of `python3`.
- Next: live tests 1-6 (assets/examples/live-test-plan.md); fold `drawing-extract` into the `analyze` route; resolve overlap with the installed plugin skill.

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
