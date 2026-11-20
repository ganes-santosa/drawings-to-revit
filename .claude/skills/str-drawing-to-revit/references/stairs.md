# Stairs — structural stair flights and landings

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: none. Content is `[THEORY]`.

## 1. Purpose and scope
Concrete/steel stair geometry as documented (flight, landing, waist thickness). No stair design.

## 2. Drawing conventions
Stair plans with arrows (UP/DN), riser/tread counts, landing levels; sections give riser height, waist thickness, landing beams; shaft outlines also form slab openings.

## 3. Required inputs
Start/end levels, flight run and width, riser count & height, tread depth, landing sizes, waist thickness, supporting beams/walls.

## 4. Interpretation method
Verify `risers × riser height = floor-to-floor`; reconcile plan and section counts; flag mismatches.

## 5. Revit procedure `[THEORY]`
- Option A: native stair by component (`StairsRun.CreateStraightRun`, Revit 2020+ with `StairsEditScope`).
- Option B: modelled as floors/beams/DirectShape when native stairs cannot represent the structure (document why).
- Cut the slab opening to the shaft outline.

## 6. Verification
Total rise; riser/tread count; landing levels; openings coincide with slab voids.

## 7. Failure cases
`[OPEN]` none recorded yet.

## 8. Related
`slabs.md`, `structural-walls.md`.
