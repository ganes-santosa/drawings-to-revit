# Full drawing → Revit workflow (route: `full`)

Load each linked file **when its phase starts**, not before. Keep a running project log (`assets/examples/project-log-template.md`).

## Phase 1 — Input analysis
Follow `workflows/drawing-analysis-workflow.md` (+ `references/drawing-interpretation.md`). Exit: sheet inventory, scale/units, cross-reference map, RFI/conflict list. **Present the RFI list to the user; resolve critical items before Phase 3.**

## Phase 2 — Project framework
`references/project-setup.md`, `references/grids-and-levels.md`, `references/revit-api-and-automation.md` (probe). Exit: tool probe recorded, units & conversion logged, levels and grids created/verified, calibration residuals logged.

## Phase 3 — Structural modelling (dependency order, adapt to the structure)
1 foundations → 2 columns → 3 walls → 4 beams/framing → 5 slabs → 6 stairs → 7 reinforcement/connections (only if supported and requested).
For each group run `workflows/element-modeling-workflow.md` with the matching reference. Strategy statement first: which groups apply, which sheets feed each, and the planned order — show it to the user.

## Phase 4 — Quality control
`workflows/quality-control-workflow.md` after each group; full audit at the end.

## Phase 5 — Reporting
SKILL.md §7 format. Update the project log, `references/lessons-learned.md` (tested lessons), and the relevant reference files (SKILL.md §8).

## Stop conditions
Missing critical information (ask), a failing approach repeated (change method), unexpected destructive impact (confirm).
