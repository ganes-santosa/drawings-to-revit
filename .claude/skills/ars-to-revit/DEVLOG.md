# Development log

Newest first. Record structure changes, verified workflows, unresolved issues. Tested results themselves go to `references/` (+ `lessons-learned.md`).


## 2026-11-25 — moved into the drawings-to-revit repo (then named str-to-revit) (unreleased)
- This skill now lives in `D:\Outpost\Coding\drawings-to-revit` next to `str-drawing-to-revit` (copied from the `ars-to-revit` repo, commit 6dc17fe). Shared scripts and templates are edited in `shared/` and copied in by `tools/sync_shared.py` (files carry a "SHARED COPY" header).
- Shared: `find_schedules.py` (one engine for both disciplines; ars ranking unchanged, regression-tested on KPwBI Part2/Part4), `check_skill.py`, `pdf_calibrate.py`, `scripts/revit/find_duplicates.cs` (new here: elements placed twice, duplicate/blank marks), `rfi-log-template.md`, one project log template shared with the structural skill (`project-setup.md` §2 step 1).

## 2026-11-24 — v0.1.0 base skill (uncommitted)
- Repo cloned (was empty). Architecture copied from `str-drawing-to-revit`: SKILL.md orchestrator + routing, references/, workflows/, scripts/, assets/ (examples, field-reports, legacy).
- **Focus (user decision):** setup, walls, floors, ceilings, roofs, door/window families, door/window placement. Doors and windows are **one module split by stage** (user idea): `openings-families.md` (Stage A, schedule → families/types) and `openings-placement.md` (Stage B, hosting/placement), with routes `openings` (both), `openings-create`, `openings-place`. Rooms/finishes parked.
- Legacy skill `architectural-drawings-to-revit` (KPwBI) archived byte-identical in `assets/legacy/` with an item-by-item map; content distributed and tagged `[IMPORTED KPwBI-ARS]`. Three deliberate changes (user brief): `say_hello` banned as a connection test (confirmed today); ARS vs STR differences are asked, not resolved by following STR; "exterior first" is a per-project choice.
- New `building-logic.md` (architectural "nothing floats": hosted inside wall length, inserts cut, walls whole, joins/enclosure, floors/ceilings inside walls, height chain, ARS vs STR consistency) and `types-and-materials.md` (system types, compound layers, materials, names/marks).
- `scripts/check_skill.py` adapted (also checks argument-hint routes and the 500-line limit); negative test: all four planted faults caught. `scripts/find_schedules.py` rewritten for architecture (`--element openings|walls|finishes|ceilings|floors|roofs`, `--sheets` sheet map from the title block) and tuned on KPwBI Part1–4, RSUD, Hunver (results in drawing-interpretation.md §3). `scripts/pdf_calibrate.py` copied from STR, not yet run (pdfplumber missing).
- `samples/` = junction to `str-to-revit/samples` (no 6 GB copy).
- Revit: read-only probe ran once on the open model before the user said it belongs to other agents; `say_hello` timed out (modal). No further Revit calls; everything Revit-side is `[IMPORTED]`/`[THEORY]`.
- Open: read the KPwBI wall-type legend and door/window schedules visually and build real catalogs (first real task); find `Metric Window.rft`/`Metric Door.rft` on this machine; a scratch Revit model for pilots; tune find_schedules on Tower 4 ITS, Bandara 02 ARC, DRC.
