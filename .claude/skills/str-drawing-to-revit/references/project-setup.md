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
5b. **Ask the project modelling decisions once, before any element is modelled,** and record the answers in the project log. Re-ask only if the user changes their mind.
   - **Beam segmentation** (user requirement 2026-11-24). Ask with AskUserQuestion:

     | Mode | What it means | Good for |
     |---|---|---|
     | **B. Split at supports** *(recommend when 4D/phasing or per-bay quantities are likely, or unknown)* | one instance per span: primary beams break at every column, secondaries at the girder or column they frame into | 4D scheduling (Navisworks TimeLiner), construction zones decided later, per-bay quantities |
     | **A. Continuous** | one instance per continuous run of the same type | clean coordination / visualisation models with no phasing |
     | **C. Continuous within zones** | continuous inside each construction zone, split at zone boundaries the team supplies (gridlines, pour breaks) | 4D where the zones are already known |

     Why B is the default when unsure: merging split beams into runs later is a scripted, proven step (`beams.md` B2b step 5, RSUD); splitting continuous beams later means re-creating beams and redoing joins and offsets. Split is the reversible choice.
     In every mode: always split at dilatation joints and where the type changes.
   - **Roof framing scope** if the set has a steel roof (`roof-framing.md` §2): purlins modelled (default yes when drawn), sag rods and wind rods (default not modelled), light-gauge (baja ringan) roofs (skip / ring beam only / placeholder).
   - Ask in the same question round if the project may need it: **slab segmentation** (one slab per bay or zone vs one per level piece) and **column stacks** (per storey is the default, `columns.md` B3.1). Same reasoning: 4D zones need pieces that do not cross zone lines.
6. **Create the project log** from `assets/examples/project-log-template.md` (inputs, conversion, levels, conflicts, assumptions, not-modelled list, counts). Update after every step.
   **Where:** a `_log` folder next to the drawing set: `<drawing set folder>\_log\` (for the sample sets `samples\<project>\_log\`). It holds `project-log.md`, the type catalog, instance tables, outline files, the RFI log and script outputs. Never inside the skill folder: project facts are not skill knowledge (SKILL.md §8). If the drawing folder is read-only or shared, ask the user for another place and write it at the top of the log. Note: `samples\` is git-ignored, so these logs are not backed up to GitHub.
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
