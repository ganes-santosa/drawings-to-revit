# Full drawings → Revit workflow (route: `full`)

Load each linked file **when its phase starts**. Keep a running project log (`assets/examples/project-log-template.md`) outside the skill (project facts never go into the skill).

## Phase 1 — Orient and analyse
`workflows/drawing-analysis-workflow.md` + `references/drawing-interpretation.md`. Read the project log first if one exists. Exit: sheet map, schedule pages per element, level/height sources, RFI/conflict list. **Present the RFI list; resolve critical items before Phase 3.**

## Phase 2 — Project framework
`references/project-setup.md` (+ `references/revit-api-and-automation.md` for the read-only probe). Exit: right document confirmed, units and conversion logged, levels (FFL/SFL) and grids verified, STR status known.

## Phase 3 — Modelling (dependency order, `references/building-logic.md` §6)
1. Walls — `references/walls.md` (+ `types-and-materials.md`)
2. Floors — `references/floors.md`
3. Door/window families — `references/openings-families.md`
4. Door/window placement — `references/openings-placement.md`
5. Ceilings — `references/ceilings.md`
6. Roofs — `references/roofs.md`

Each group runs `workflows/element-modeling-workflow.md`. Strategy statement first: which groups apply, which sheets feed each, the order, and the priority (exterior first was the KPwBI choice; ask per project) — show it to the user and agree the package order.

## Phase 4 — Quality control
`workflows/quality-control-workflow.md` after each group; full audit at the end.

## Phase 5 — Report
SKILL.md §7. Update the project log and `references/lessons-learned.md` (tested lessons only).

## Stop conditions
Missing critical information (ask) · a failing approach repeated (change method) · unexpected destructive impact (confirm) · wrong or shared Revit model (stop).
