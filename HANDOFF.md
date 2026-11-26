# HANDOFF — where we left off

Last updated: 2026-11-25 (ARS: KPwBI catalogs, core door/window families) · Repo state: this repo, now named **drawings-to-revit**, holds **two skills** (STR and ARS) plus `shared/` and `tools/`. The move-in of `ars-to-revit` and the shared folder are committed and pushed. Tag `v1.1.0` (STR, points one commit before its version fix, left as is on purpose).
- Git remote `origin` = `https://github.com/ganes-santosa/drawings-to-revit.git` (GitHub repo renamed from `str-to-revit` on 2026-11-25; the old address redirects).
- Local folder: rename `D:\Outpost\Coding\str-to-revit` → `D:\Outpost\Coding\drawings-to-revit` is pending; it was blocked while a session had it open. The old `ars-to-revit` folder's `samples` junction points at the old path.

## Repo setup (2026-11-25)
- `ars-to-revit` copied in byte-identical from `D:\Outpost\Coding\ars-to-revit` (commit 6dc17fe; its GitHub repo `ganes-santosa/ars-to-revit` and the local folder were left untouched). Whether to archive that repo is the user's call.
- `shared/` holds the one original of: `find_schedules.py` (one engine, `--discipline str|ars`; both rankings regression-tested unchanged on DRC and KPwBI), `check_skill.py`, `pdf_calibrate.py`, `scripts/revit/find_duplicates.cs`, the RFI template and **one project log template for both disciplines**. `tools/sync_shared.py` copies them into both skills; `--check` verifies and runs both checkers.
- Candidates to share next (need a careful content merge, not a copy): the Revit bridge behaviour in both `revit-api-and-automation.md`, units/coordinates/levels in both `project-setup.md`, modal-dialog rows in both `troubleshooting.md`.

---

## STR skill (`str-drawing-to-revit`)

### What exists
- v1.1.0 + unreleased work: orchestrator `SKILL.md`, 15 reference files, 4 workflows, scripts, templates. Details: its `DEVLOG.md`.
- Routes: `full, analyze, setup, grids, columns, beams, slabs, foundations, roof (alias framing), families, api, review, troubleshoot, learn, help`. Removed to stay focused (2026-11-23): walls, stairs, reinforcement, connections, views; recoverable from tag `v1.1.0`.
- Core element procedure (`workflows/element-modeling-workflow.md`): Stage A types → Stage B placement → Stage C close-out.
- "Nothing floats" rule + `references/building-logic.md` (incl. §7 changes ripple) + read-only Revit scripts `check_connectivity.cs` (height-aware), `find_duplicates.cs` (shared), `audit_columns.cs`, `audit_roof.cs`.
- Review fixes 2026-11-25: re-runnable batches, rule 5 allows only rule-based snaps, offsets per SFL zone, columns clean table (B3b) + audit (B5b), project log folder.
- `columns.md`, `beams.md`, `slabs.md`, `roof-framing.md` in the types/placement layout. `roof-framing.md` (2026-11-25) is built from the roof sheets of five sample sets.
- `assets/field-reports/`: RSUD Cakung beam (2026-11-23), slab (2026-11-24) and roof / roof-support / continuous-void (2026-11-25) reports, all integrated (roof report: all steel as Beam, arch circle method, groups, roof sections govern columns, columns carrying nothing → hidden group, one shaft per vertical void, dak + MISSING SUPPORT rule, lift pits, discipline precedence asked at setup). Clean-up rules run on the planning table before placing, then an audit-and-repair pass (untested pre-placement version: compare with RSUD numbers on one floor).

### What is proven vs not
- **Verified here:** skill syntax, `find_schedules.py` on real sets (columns 4/4 sets, roof sheets 5/5), Revit 2026 + family templates exist.
- **Run in Revit by another agent (RSUD Cakung):** beam placement mechanics, connected ends, extension, merge, joints, flush snap, beam audit; slab outlines, clean-up, edge snapping, arcs, shafts, slab audit; steel roof frames (arch and mono-pitch, families from templates, groups), roof-support checks, continuous shafts.
- **Never run in Revit:** columns, foundations, roof, type creation, and all repo scripts.

### Next steps (in order)
1. **Live tests in Revit** on a scratch model the user prepares: `assets/examples/live-test-plan.md` tests 1–6. Use the read-only probe, not `say_hello`.
2. Run `check_connectivity.cs`, `find_duplicates.cs`, `audit_columns.cs` on a test model with planted faults.
3. Restructure `foundations.md` into the types/placement layout. First roof test: one KPwBI GPNJ truss (p50–51) as a **Revit Structural Truss** (new default, user rule 2026-11-25: method asked at setup, trusses recommended; types first, `roof-framing.md` A4b/B4a, all `[THEORY]`): build the truss family from `Metric Structural Trusses.rft` (API for chord/web lines is `[OPEN]`), place, compare members with the panel points, then `audit_roof.cs`.
4. End-to-end pilot on DRC Kalimantan `3.DRC_STRUKTUR.pdf` (columns p23, beams p33, slabs p17), columns first.
5. Get the RSUD agent's full clean-up and audit scripts; generalise the RSUD slab scripts into `scripts/`.
6. `find_schedules.py` on Tower 4 ITS and Bandara (large, slow; roof text not searchable there).
7. The installed plugin skill `structural-drawings-to-revit` overlaps: ask the user to disable it once this one is trusted.

---

## ARS skill (`ars-to-revit`)

### What exists
- v0.1.0: `SKILL.md` (rules, 15 routes, preferences), 14 references + template, 4 workflows, scripts (shared ones), assets (project log / RFI / type catalog templates, empty `field-reports/`, `legacy/`). Details: its `DEVLOG.md`.
- **Focus:** setup, walls, floors, ceilings, roofs, `openings-create` (door/window families from the schedule), `openings-place` (placement), `openings` = both in order.
- Legacy KPwBI architectural skill archived byte-identical + item map (`assets/legacy/README.md`); content tagged `[IMPORTED KPwBI-ARS]`.

### KPwBI catalogs (2026-11-25, no Revit)
- Outputs in `samples\DED KPWBI DIY\_log\` (git-ignored): `project-log.md` (common + architecture sections; levels/grids/coordinates not set up), `kpwbi-wall-types.csv` (A, B-130, B-150, C blocked, 2 detail-only partitions, 19 finish codes), `kpwbi-door-window-types.csv` (24 doors D42–D65, 42 window-sheet codes, schedule qty next to keyplan count), `rfi-log.md` (19 items).
- Skill: `walls.md` and `openings-families.md` A1–A3 rewritten from the real sheets; `drawing-interpretation.md` §2–3.

### Door/window families (2026-11-25, Revit 2026 scratch project)
- **Supported set (user decision: fewer, reliable):** `families\Windows\KPW_Window.rfa` (1–6 equal columns, optional top/bottom light) and `families\Doors\KPW_Door.rfa` (1/2 leaves, optional transom, vision panel, louvre). One type per drawing code. Scripts `scripts/revit/family_window_core.cs`, `family_door_core.cs`; rules in `openings-families.md` A5d.
- Verified: window 40 locks / flex 8/8; door 47 locks / flex 8/8 / committed sweep 101 of 120 (rest not run, bridge timeouts); 7 KPwBI types (AW04, AW18, AW21, D46, D47, D52, D55) placed in a test wall: sizes, sills, cuts, bounding boxes exact, 0 warnings.
- **Edge cases are improvised at run time** (right opening/sill/host/cut, marked `IMPROVISED` + LOW, logged); 14 known edge cases from DRC / Tower 4 / Bandara / Hunver in A5c, to be supported later.
- Superseded: pilot `KPW_Window-Fixed-2Pane.rfa` and its script (kept for the record). The scratch project in Revit is unsaved.

### What is proven vs not
- **Verified:** skill syntax; `check_skill.py`; `find_schedules.py` on KPwBI; family creation from templates, type creation and door/window placement with cut checks (above); `say_hello` blocks on its modal dialog.
- **Never run:** walls, floors, ceilings, roofs in Revit; `pdf_calibrate.py` (pdfplumber missing).

### Next steps (in order)
1. Decisions waiting on the user: finishes as wall layers vs separate walls; B-150 / C thickness (RFI-W01/W02); lobby glazing (D57/D58/D60), GP partitions, AW29 as curtain walls?; screens K01/J01/J02 parked?
2. Support the next edge cases one at a time (A5c), each with the same build → flex → place → check cycle; run the remaining door sweep cases in short calls.
3. Add an "Improvised door/window types" line to `shared/assets/examples/project-log-template.md` once the other session's edits there are committed.
4. KPwBI: read sills/heights from elevations and sections (RFI-W10, RFI-D05) and the floor/ceiling finish plans; then a second set (Tower 4 ITS or Bandara).
5. **Revit pilots** for walls, floors, ceilings, roofs on a scratch model the user opens for this work.
6. Install pdfplumber (ask) or port `pdf_calibrate.py` to PyMuPDF (in `shared/`).
7. Write and test `scripts/revit/check_building_logic.cs` (inserts hosted/cutting/within length, wall gaps, floors outside walls).
8. The installed plugin skill `architectural-drawings-to-revit` overlaps: ask the user to disable it once `ars-to-revit` is trusted.

---

## Decisions the user made (keep)
- Local development; push only when told; commit only when told. STR version tags v1.0.0, v1.1.0 pushed; leave v1.1.0 as is.
- **Two skills, one repo, shared scripts in `shared/`** (2026-11-25).
- **Do not work in Revit on a model other agents use; it is not a reference** (2026-11-24). Never `say_hello`.
- Core procedure is theirs: types first (find table, catalog, create by duplicating if possible, else family from scratch into a family folder, verify), then place.
- STR: focus setup, columns, beams, slabs, foundations, roof ("essentials first, they have to work well"); no beam ever floats; beam segmentation per project at setup (recommend split at supports when unsure).
- ARS: doors and windows = one module split into family creation and placement; ARS vs STR differences asked, not ranked; exterior-first is per project.
- One project log per project for both skills: `<drawing set folder>\_log\` (samples: `samples\<project>\_log\`, git-ignored).
- Keep git identity `bimpc004` (repo-local).

## Gotchas
- Revit tool names here are `mcp__mcp-server-for-revit__*`.
- Writes to SKILL.md can fail when the file is briefly locked: re-run.
- Moving a published git tag is blocked by the auto-mode classifier; do not try.
- The working directory sometimes jumps into a skill folder: use absolute paths.
- Python/bash edits with backslashes can mangle Windows paths (`\a` became a bell character): build backslashes with `chr(92)` or use the Edit tool, then grep.
- `mklink` via Git Bash fails; create junctions with PowerShell `New-Item -ItemType Junction`.
