# HANDOFF — where we left off

Last updated: 2026-11-25 · Repo state: this repo, now named **drawings-to-revit**, holds **two skills** (STR and ARS) plus `shared/` and `tools/`. The move-in of `ars-to-revit` and the shared folder are committed and pushed. Tag `v1.1.0` (STR, points one commit before its version fix, left as is on purpose).
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
- `assets/field-reports/`: RSUD Cakung beam (2026-11-23) and slab (2026-11-24) reports, integrated. Clean-up rules run on the planning table before placing, then an audit-and-repair pass (untested pre-placement version: compare with RSUD numbers on one floor).

### What is proven vs not
- **Verified here:** skill syntax, `find_schedules.py` on real sets (columns 4/4 sets, roof sheets 5/5), Revit 2026 + family templates exist.
- **Run in Revit by another agent (RSUD Cakung):** beam placement mechanics, connected ends, extension, merge, joints, flush snap, beam audit; slab outlines, clean-up, edge snapping, arcs, shafts, slab audit.
- **Never run in Revit:** columns, foundations, roof, type creation, and all repo scripts.

### Next steps (in order)
1. **Live tests in Revit** on a scratch model the user prepares: `assets/examples/live-test-plan.md` tests 1–6. Use the read-only probe, not `say_hello`.
2. Run `check_connectivity.cs`, `find_duplicates.cs`, `audit_columns.cs` on a test model with planted faults.
3. Restructure `foundations.md` into the types/placement layout. First roof test: one KPwBI GPNJ truss (p50–51), then `audit_roof.cs`.
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

### What is proven vs not
- **Verified:** skill syntax; `check_skill.py` (negative test catches all planted faults); `find_schedules.py` on KPwBI (all 26 door/window schedule pages ranked first; titles from title blocks; wall-type, finish and ceiling plans found); RSUD and Hunver architecture have outlined text; no door/window family templates on this machine; `say_hello` times out on its modal dialog.
- **Never run:** every Revit procedure (`[IMPORTED KPwBI-ARS]` or `[THEORY]`), `pdf_calibrate.py` (pdfplumber missing).

### Next steps (in order)
1. **First real task (no Revit needed):** read the KPwBI wall-type legend (Part2 A-4201..4207) and door/window schedules (Part4 A-8101..8126) visually; build the wall and opening type catalogs; refine `walls.md` A1–A3 and `openings-families.md` A1–A3.
2. Same on a second set (Tower 4 ITS architecture or Bandara 02 ARC); tune `find_schedules.py` (edit in `shared/`).
3. **Revit pilots** on a scratch model the user opens for this work (not a shared model): probe, one wall type + wall, one door + window (cut check), one floor, one ceiling, one roof.
4. Ask the user for `Metric Window.rft` / `Metric Door.rft` (or their template folder) and a family folder.
5. Decisions still open (ask when the first task needs them): finishes as wall layers vs separate walls; finish floors vs combined floors vs STR copy; width/height basis in schedules.
6. Install pdfplumber (ask) or port `pdf_calibrate.py` to PyMuPDF (in `shared/`, benefits both skills).
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
