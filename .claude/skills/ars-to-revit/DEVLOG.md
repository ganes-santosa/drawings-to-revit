# Development log

Newest first. Record structure changes, verified workflows, unresolved issues. Tested results themselves go to `references/` (+ `lessons-learned.md`).


## 2026-11-25 — core door/window families KPW_Window + KPW_Door (user decision: fewer, reliable)
- `openings-families.md` A5d: the two supported families, mapping rules, the run-time "improvise and flag" rule for edge cases, and the rules learnt (valid hidden parts, park hidden parts, set order, commit-based tests, short bridge calls, separate type/place calls). Scripts `family_window_core.cs`, `family_door_core.cs` (with guard formulas).
- Verified in a Revit 2026 scratch project: KPW_Window (40 locks, flex 8/8) and KPW_Door (47 locks, flex 8/8, committed sweep 101/120); 7 KPwBI types (AW04, AW18, AW21, D46, D47, D52, D55) placed in a 22 m test wall: sizes, sills, cuts (wall volume exact), bounding boxes, visible parts all right, 0 warnings.
- Problems met and fixed on the way: D55 froze Revit (hidden vision plane negative) → caps; window bounding box too wide (hidden mullions outside) → parked; windows uncut when typed and placed in one call → separate calls; long sweeps timed out → short calls. Revit was restarted once by the user (scratch project lost and rebuilt).
- `openings-placement.md` B5 and `revit-api-and-automation.md` §4 updated (failure handler, timeouts).

## 2026-11-25 — door/window edge cases from the other sample sets
- Read the door/window schedules of DRC Kalimantan (AR-709..728), Tower 4 ITS (p98–110), Bandara (utility-building schedules) and checked Hunver/RSUD (no schedules). Added `openings-families.md` A5c: 14 edge cases with a proposed way to support each (`[THEORY]` until piloted) and reading notes (scanned sets, layouts, false friends, no-schedule sets).

## 2026-11-25 — parametric door/window families (user decision) + pilot
- `openings-families.md` A5: default is now one parametric family per shape, one type per code (66 KPwBI codes ≈ 10–12 families); stock duplicate and static family kept as fallbacks. Template path corrected (D: drive).
- Pilot in Revit 2026 scratch model "Project1" (user-opened): fixed 2-pane window, 16/16 locks, flex 5/5, 4 KPwBI types placed and cut exactly, 0 warnings (A5b). New `scripts/revit/family_window_fixed_2pane.cs`. Placement trap (sill 0) in `openings-placement.md` B4; family-document API confirmed in `revit-api-and-automation.md` §4.

## 2026-11-25 — first real task: KPwBI type catalogs (no Revit)
- Read the KPwBI architecture set (Part1–4): wall-type legends A-4201..4207, wall-finish legends A-4101..4107, standard details A-7009/A-7010, partial plans A-5004/A-5201, all 26 door/window schedules A-8101..8126 and the 12 keyplans. Outputs in `samples/DED KPWBI DIY/_log/` (git-ignored): `project-log.md` (common + architecture), `kpwbi-wall-types.csv`, `kpwbi-door-window-types.csv` (24 doors, 42 window-sheet codes), `rfi-log.md` (19 items).
- `walls.md` A1–A3 and `openings-families.md` A1–A3 rewritten from what the sheets really show (where values sit, table layout, traps); `drawing-interpretation.md` §2–3: finish legends are text, keyplan tag pairing rule, rotated pages. Tags `[VERIFIED 2026-11-25, samples]`.
- Not changed: `find_schedules.py` (it found every sheet needed; the standard details and partial plans that hold wall thicknesses are not "schedules" and are found through `--sheets`).

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
