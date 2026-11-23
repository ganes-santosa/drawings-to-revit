# HANDOFF — where we left off

Last updated: 2026-11-23 · Repo state: last pushed commit `505d3dc` (local focus cleanup + AGENTS/CLAUDE/HANDOFF not yet committed), tag `v1.1.0` (points one commit earlier, left as is on purpose; the later commit only fixes the version number).

## What exists
- Skill `str-drawing-to-revit` v1.1.0: orchestrator `SKILL.md` (rules, routing, preferences), 15 reference files, 4 workflows, scripts, templates. Details: `DEVLOG.md`.
- Routes: `full, analyze, setup, grids, columns, beams, slabs, foundations, framing (roof), families, api, review, troubleshoot, learn, help`. Removed to stay focused (2026-11-23): walls, stairs, reinforcement, connections, views files and routes, and the old `drawing-extract` skill; all recoverable from tag `v1.1.0`.
- Core element procedure (`workflows/element-modeling-workflow.md`): Stage A types (find schedule → extract → catalog → map → create → verify gate) → Stage B placement (instance table + supports → pilot → batch → verify gate) → Stage C close-out.
- "Nothing floats" rule + `references/building-logic.md` + `scripts/revit/check_connectivity.cs`.
- `columns.md`, `beams.md`, `slabs.md` are rewritten in the types/placement layout.
- `scripts/find_schedules.py` (shortlists schedule pages in drawing PDFs); tuned on the real sets.
- `samples/` holds 6 real DED sets: Bandara Hang Nadim, DRC Kalimantan, Hunver OIKN 390B, KPWBI DIY, RSUD Cakung, Tower 4 ITS.
- `assets/legacy/` keeps the original single-file KPwBI skill verbatim.
- `assets/field-reports/` holds field reports from real modelling sessions. First one: RSUD Cakung beam clean-up (2026-11-23), now integrated. User decision: the clean-up rules run on the **planning table before placing** (`beams.md` B2b), then an **audit-and-repair pass** in the model (B5b, B6). The pre-placement version is untested: try it on one floor and compare audit numbers with RSUD.

## What is proven vs not
- **Verified here:** the skill syntax (official docs), `find_schedules.py` on real sets (columns found in 4 of 4 sets tested; beams/slabs missed where text is outlined), Revit 2026 + family templates exist on this machine.
- **Run in Revit on a real project (RSUD Cakung, by another agent):** beam placement mechanics, connected-end rule, free-end extension, merge, joint clean-up, flush snap, per-floor audit `[VERIFIED RSUD]` / `[EXPERIMENTAL RSUD]`.
- **Never run in Revit:** everything else (columns, slabs, foundations, roof, type creation, and the repo's own scripts, including the rewritten `check_connectivity.cs`). Tagged `[IMPORTED KPwBI]` or `[THEORY]`. Revit was not running; MCP calls failed with "connect to revit client failed".

## Open items / next steps (in order)
1. **Live tests in Revit** (needs the user to open Revit with a scratch project and start the MCP add-in): `assets/examples/live-test-plan.md` tests 1–6 first (connection, units, levels/grids, family inventory, type duplication, one beam with justification). Promote or fix tags with evidence.
2. Run `check_connectivity.cs` on a test model; add the missing check (column top below a framing beam).
3. Restructure `foundations.md` and `structural-framing.md` (roof) into the types/placement layout of `columns.md`.
4. Pick one real project (suggest DRC Kalimantan `3.DRC_STRUKTUR.pdf`, 84 pages; columns K1/K2 table on p23, beams p33, slabs p17) and run the full procedure end to end on columns first.
5. Ask the RSUD agent for its full clean-up and audit scripts (~4k chars each) and store them under `scripts/revit/` after a test run.
6. Not yet run: `find_schedules.py` on Tower 4 ITS and Bandara Hang Nadim (very large files, slow).
7. The installed plugin skill `structural-drawings-to-revit` overlaps and may trigger instead of the new skill: ask the user to disable it once the new one is trusted.

## Decisions the user made (keep)
- Local development; push only when told. Version tags v1.0.0, v1.1.0 pushed. Leave the v1.1.0 tag as is.
- Focus: setup, columns, beams, slabs, foundations, roof. "Essentials first, they have to work well."
- Core procedure is theirs: types first (find table, catalog, create by duplicating if possible, else family from scratch into a family folder, verify), then place.
- Building logic: no beam ever floats.
- Keep git identity `bimpc004` (repo-local).

## Gotchas learned this session
- The Revit tool names here are `mcp__mcp-server-for-revit__*` (the old skill used a `remote-devices` prefix).
- `sed`/Python writes to SKILL.md can fail when the file is briefly locked: re-run.
- Moving a published git tag is blocked by the auto-mode classifier; do not try.
