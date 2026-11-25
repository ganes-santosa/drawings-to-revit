# Development log

Newest first. Record: structure changes, verified workflows, unresolved issues, lessons. Tested results themselves go to `references/` (+ `lessons-learned.md`).

## 2026-11-25 — one repo, two skills, shared scripts (unreleased)
- `ars-to-revit` moved into this repo (copied from `D:\Outpost\Coding\ars-to-revit`, commit 6dc17fe, byte-identical). Shared originals live in `shared/` at the repo root; `tools/sync_shared.py` copies them into both skills with a "SHARED COPY" header; `--check` fails on drift and runs both checkers.
- Shared now: `scripts/find_schedules.py` (one engine, `--discipline str|ars`, default from the skill folder; both rankings unchanged, regression-tested on DRC and KPwBI), `check_skill.py` (the ars version: also checks argument-hint routes and the 500-line limit), `pdf_calibrate.py`, `scripts/revit/find_duplicates.cs` (now also walls, ceilings, roofs, doors, windows), `rfi-log-template.md`, one project log template for both disciplines.
- `say_hello` dropped as a connection test (architecture skill found it blocks the API): workflow Stage 0, api environment note.

## 2026-11-25 — roof framing starting point (unreleased)
- Read the roof sheets of the sample sets (DRC, Hunver, KPwBI GKU/GPNJ, RSUD; Bandara and Tower 4 have no searchable roof text).
- `structural-framing.md` → `references/roof-framing.md`, rewritten in the A/B layout: roof systems seen in the samples, what-to-model decision (§2), profile notation (dots, decimal comma, 2L, LC), type creation incl. parameter probe and DirectShape fallback, 3D geometry record and instance table, arch radius worked example (RSUD), interpretation rules (slope spacing for purlins, panel points, stub columns), B3b clean table (nodes), sloped/curved member snippet, B5b audit, B6 checks.
- New `scripts/revit/audit_roof.cs` (3D free ends incl. arcs, short members) `[THEORY]`.
- Route renamed `framing` → `roof` (old words kept as aliases); `find_schedules.py` roof phrases and steel profile counting; building-logic supports for truss webs and stub columns; setup asks the roof scope; model-validation #21; troubleshooting rows.

## 2026-11-25 — review fixes: two bugs, five gaps (unreleased)
- `check_connectivity.cs`: height tests (beam-to-beam same floor only; column must reach the beam soffit; a column above does not count); free ends report why (`column top below beam soffit` closes the old [OPEN] item).
- New read-only scripts `[THEORY]`: `find_duplicates.cs` (placed twice, duplicate/blank marks), `audit_columns.cs` (stack gaps/overlaps, stack shifts, free tops).
- Re-runnable batches: skip existing Marks (api §5 snippet; beams, columns, workflow B5); SKILL.md §4.
- SKILL.md rule 5 now allows only the rule-based snaps within their tolerances (it contradicted the beam/slab snaps).
- `building-logic.md` §7 "Changes ripple": dependency table; workflow B5b points to it.
- Offsets audited per SFL zone, not one value per floor (beams B6, slabs #11, model-validation #20, level table with zone extents).
- `columns.md` B3b clean table and B5b audit; workflow B2b/B5b include columns.
- Project log folder defined: `<drawing set folder>\_log\` (project-setup §3 step 6, template, SKILL.md §4).

## 2026-11-24 — beam segmentation becomes a project decision (unreleased)
- User requirement: decide per project whether beams are continuous or split (4D / Navisworks TimeLiner zones need pieces that do not cross zones).
- `project-setup.md` §3 step 5b: ask once at setup (A continuous, B split at supports, C continuous within zones); recommend B when 4D is possible or unknown (merge later = scripted, split later = rework); slab segmentation and column stacks asked in the same round. Recorded in the project log (template updated).
- `beams.md` B2a.8 and B2b step 5: merge into runs always, then apply the mode (cut at supports / zone lines); audit checks segmentation; RSUD continuity rule kept as mode A. Workflow Stage 0 reads the decisions; SKILL.md preference added.

## 2026-11-24 — RSUD Cakung slab field report integrated (unreleased)
- Archived `assets/field-reports/2026-11-24-rsud-cakung-slab-cleanliness.md` and its scripts (`2026-11-24-rsud-slab-cleanup-scripts/`, verbatim, RSUD-specific, notes appended to its README).
- `slabs.md` rewritten in the beam layout: big lesson (internal consistency), A3 piece kinds B/S/D, A4–A5 copy-and-SetLayers, B2 vector outline file + beam CSV, B2a rules (**extent = outline polygon; edge line = edge-beam outer face**, replacing the old B3 rule 1), B2b clean before building (cell grid from real lines, artifact table + guards, snap, clean again, pre-build audit), B4–B5 (file hand-off, arcs, shaft openings, one level per call, hand-built pieces, Regenerate), B5b audit and repair (four causes of protruding beams, ripple to dak, fix the class), B6 12-check slab audit.
- `beams.md`: curve edit resets end offsets (write back), curved beams, off-axis warning fix, audit adds end offsets and OV tips without edge beam.
- `building-logic.md`: slab edge = edge-beam outer face; cantilever row needs an edge beam.
- `drawing-interpretation.md`: Bézier arc detection and centre rule; "none found" is not an answer.
- `revit-api-and-automation.md`, `troubleshooting.md` (8 rows), `model-validation.md` (#19 slab audit, #20 end offsets), workflow B2b/B5b for slabs, SKILL.md "fix the class, not the instance".

## 2026-11-23 — RSUD Cakung beam field report integrated (unreleased)
- Archived the structure agent's handover as `assets/field-reports/2026-11-23-rsud-cakung-beam-cleanliness.md`; new evidence tags `[VERIFIED RSUD]` / `[EXPERIMENTAL RSUD]` in SKILL.md §8.
- `beams.md` rewritten: B3 continuity (one instance per run; secondaries no longer split), edge beams, flush intent; B4–B5 verified mechanics (justification, offsets, move via LocationCurve, allow/disallow joins, arrays for speed); new **B5b clean-up pipeline** (fixed order) with the joint table; B6 per-floor audit; failure table extended.
- `building-logic.md`: connected-end definition, extension method, re-scan rule, overshoot bug; joins at column ends allowed.
- `check_connectivity.cs` rewritten to the RSUD definition (within the other beam's length; ±20 mm column; half-width + 30 mm); not yet run.
- `drawing-interpretation.md` §5: one-sided / outline-only edge beams + detection, "model it, then tag it", flush intent, column outline vs schedule, de-duplication, user wording vs selection. `grids-and-levels.md`: sheets shift against each other. `revit-api-and-automation.md`: modal dialogs generalised, stale replies, speed, InvalidObject, `out`, LINQ works. `troubleshooting.md`: 8 rows. `model-validation.md`: check #18 beam audit.
- SKILL.md: "clean up and audit every floor", "model it, then tag it" extended to graphic conventions, user wording vs selection.
- Open: the RSUD audit/clean-up scripts themselves are not in the repo (only the core snippet); ask for them.
- Restructured (user decision): the clean-up now runs on the **planning table before placing** (`beams.md` B2b, steps 1–7 incl. a table gate), and B5b became an **audit-and-repair pass** in the model for what only shows there. Workflow, building-logic §6 and SKILL.md aligned. Pre-placement version `[THEORY]` until tested on a floor.

## 2026-11-23 — focus cleanup (unreleased)
- Removed everything outside the focus: references `structural-walls`, `stairs`, `reinforcement`, `connections`, `views-and-documentation`; their routing rows; the old `drawing-extract` skill; live-test rows for them. Recoverable from git tag `v1.1.0`.
- README rewritten for the single-skill layout. Added AGENTS.md, CLAUDE.md, HANDOFF.md.

## 2026-11-20 — v1.1.0 focus, building logic, core procedure
- Focus narrowed to setup, columns, beams, slabs, foundations, roof (`framing`). Walls, stairs, reinforcement, connections, views moved to "Parked routes" in SKILL.md.
- New global rule 11 "Nothing floats" + `references/building-logic.md` (load path, valid supports per element, support table, end-point rules, join notes). Loaded by every focus element route and by `review`.
- New `scripts/revit/check_connectivity.cs` (read-only floating-end and column-base check) and validation check #17. Not yet run in Revit.
- Element workflow rewritten as the **core procedure** (user-defined): Stage 0 scope → Stage A types (A1 find tables, A2 extract, A3 reconcile + catalog, A4 map to Revit, A5 create: exists → duplicate → load → new family → DirectShape, A6 gate) → Stage B placement (B1 layouts, B2 instance table + supports, B3 cross-check, B4 pilot, B5 batch supports-first, B6 gate) → Stage C close-out.
- `columns.md`, `beams.md`, `slabs.md` rewritten in the A/B layout with from-scratch guidance and `[THEORY]` code; all KPwBI notes kept. `_template.md` updated to the same layout. Foundations and roof framing: restructure pending.
- New `scripts/find_schedules.py` (PyMuPDF/pdftotext keyword scoring, English + Indonesian) and `assets/examples/type-catalog-template.csv`.
- `samples/` folder created for the user's real drawing sets (git-ignored); user added 6 real DED sets (386 files, 6.1 GB).
- `find_schedules.py` tuned on the real sets (phrases over sizes, PEMBESIAN/TABULASI/PERKUATAN, stair and example penalties, drawing-index flag). Real-set schedule vocabulary recorded in drawing-interpretation.md.

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
