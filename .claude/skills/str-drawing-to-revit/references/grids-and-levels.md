# Grids and levels — the project coordinate framework

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: KPwBI (2026) items imported; nothing re-tested here

## 1. Purpose and scope
Extract grids and levels from drawings, create/verify them in Revit, calibrate PDF coordinates to them. Everything else is positioned relative to this.

## 2. Drawing conventions
Grids: bubbles with letters/numbers; irregular spacings; sub-grids (1A, 1'); dimension strings between bubbles; skewed or curved grids. Levels: FFL (finished floor), SFL/structural slab top (usually FFL − 50 to −150, varies by zone), top of footing, T.O.C./T.O.S., ±0.000 datum definition. Sections and elevations carry level markers; schedules may carry "level" columns.

## 3. Required inputs
Grid names & spacings (explicit dimensions, not scaled), level names & elevations with datum, SFL offsets per zone, any sheet-group datum shift.

## 4. Interpretation method
- Build a grid table: name, direction, position (mm, from dimension string), source sheet. Cross-check cumulative dimensions against overall dimensions.
- Build a level table: name, FFL, SFL per zone, source. Record datum shifts between sheet groups (verify one known level per group).
- Elements derive elevation from **level + offset**; keep SFL per zone in the log `[IMPORTED KPwBI]`.

## 5. PDF-to-model calibration `[IMPORTED KPwBI]` method · script `[IMPORTED container 2026-11-20]`
- Find the **vector grid lines** on the sheet (pdfplumber), record their pt coordinates; map pt→mm **piecewise, grid-to-grid, per axis**. Never one global scale.
- Failure that justified this: assuming row 1' at 310.0 pt (vs true 308.93 pt) and 105.88 mm/pt (vs ~105.84) shifted a roof ~112 mm and an east wing 30–43 mm and went unnoticed through several checks.
- **Sheets shift against each other** `[VERIFIED RSUD]`: one plan page sat 45.3 pt lower than its sister sheets, and an automatic grid alignment locked onto the wrong grid spacing (off by a whole multiple of ~28 pt), placing a whole floor wrong. Align each sheet to **its own** grids with a *constrained* shift search, and check one known column per sheet.
- After calibrating, confirm known on-grid members land on grid (error check on every grid line) before measuring anything.
- Tool: `python ${CLAUDE_SKILL_DIR}/scripts/pdf_calibrate.py --help` (piecewise calibrator + residual report; self-test included).

## 6. Revit procedure
1. List existing levels/grids first (`FilteredElementCollector(document).OfClass(typeof(Level))`, `.OfClass(typeof(Grid))`) `[THEORY]`. Verify against the tables; do not duplicate.
2. Create/adjust levels: `Level.Create(document, elevationFt)`; name via `level.Name`; set elevations in feet. `[THEORY]`
3. Create grids: `Grid.Create(document, Line.CreateBound(p0, p1))`; `grid.Name = "A"`. `[THEORY]` Arcs: `Grid.Create(document, Arc)`.
4. Pin grids/levels after verification (`element.Pinned = true`) to prevent accidental moves. `[THEORY]`
5. Reference-level strategy: elements hosted on the **level that corresponds to their FFL/SFL**, with offset to the real top/bottom; do not use arbitrary new levels per element.
6. Set level types/annotation per project standard — ask; no tested standard yet `[OPEN]`.

## 7. Verification
Programmatic: read back every level elevation (mm) and every grid line endpoints → diff against tables (tolerance 0.5 mm). Count levels/grids vs table.

## 8. Failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| All measured positions shifted uniformly | Global scale / wrong datum | Piecewise calibration; check datum shift of sheet group | [IMPORTED KPwBI] |
| Inset positions wrong | Inset scale ≠ title scale | Calibrate on inset ticks | [IMPORTED KPwBI] |
| Level mismatch between sheet groups | Different zero datums | Compare one known level on each group | [IMPORTED KPwBI] |

## 9. Related
`project-setup.md`, `drawing-interpretation.md` §4, `model-validation.md`.
