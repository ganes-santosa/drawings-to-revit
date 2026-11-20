# Project setup — units, coordinates, conventions, project log

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: none in this file yet

## 1. Purpose and scope
Phase 2 framework decisions made *once* before modelling: units, coordinate conversion, naming/marking conventions, project log. Levels and grids: `grids-and-levels.md`.

## 2. Required inputs
Drawing units & scale (from Phase 1); whether the Revit file already exists, and its template; project base point / survey point state; the client/office naming convention (ask — do not invent); the Revit version and automation tool (run `api` probe).

## 3. Procedure
1. **Probe the environment** (`revit-api-and-automation.md` §3): Revit version, document title, units, existing levels/grids/families. Record in the project log.
2. **Units.** Revit stores length internally in feet. `[THEORY]` mm→ft = ÷304.8 (verified arithmetic; used throughout KPwBI). Check `Document.GetUnits()` display units; internal units are unaffected by display units. Never feed mm numbers into the API without converting.
3. **Single plan coordinate system for all logs:** state it explicitly, e.g. "x = mm east of grid A, y = mm south of first grid row". `[IMPORTED KPwBI]` Revit internal conversion in that job was `X = x − 217837`, `Y = 172339 − y` (axis flip), ft = mm/304.8. *Write your own conversion and its axis flip in the log; never reuse these numbers.*
4. **Decide the Revit origin strategy**: model near internal origin, or at shared coordinates; do not move project base/survey points without asking. `[THEORY]`
5. **Naming and marks.** Propose a scheme and get confirmation. Pattern that worked `[IMPORTED KPwBI]`: Mark `K-<grid>/<row>-S<n>` (columns), `BL<n>-W|E|T-nnn` (beams), `PC-<type>-<grid>` (pile caps), `TB-<type>-x/y` (bored piles). Comments: source sheet, drawing tag/type, provenance, `LOW CONFIDENCE` where applicable.
6. **Create the project log** from `assets/examples/project-log-template.md` (inputs, conversion, levels, conflicts, assumptions, not-modelled list, counts). Update after every step.
7. **Do not put the AI's name in view or element names** (user preference `[IMPORTED KPwBI]`). Use project-style names from the start.

## 4. Verification
Log contains: units, conversion with axis flip, level table, grid table, conventions, tool/version. A one-element round trip: place a marker at a known plan coordinate → read back → matches the drawing within tolerance.

## 5. Failure cases
| Symptom | Cause | Fix |
|---|---|---|
| Everything 304.8× off | mm passed as feet | convert; assert in a unit test element |
| Mirror-imaged model | Plan y (south) vs Revit Y (north) | Apply axis flip; verify with an asymmetric element |
| Ghost offset after shared-coordinate change | Base/survey point moved | Restore; ask before changing |

## 6. Related
`grids-and-levels.md`, `revit-api-and-automation.md`, `workflows/full-modeling-workflow.md`.
