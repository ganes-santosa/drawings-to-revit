# Columns — structural columns (OST_StructuralColumns)

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: 2026 (KPwBI, imported); not re-tested here

## 1. Purpose and scope
Concrete and steel columns: sizes, stacking per storey, base/top levels, orientation, joins with beams and foundations.

## 2. Drawing conventions
Column layout plan (marks at grid intersections, offsets from grid dimensioned); column schedule (mark × level → size, reinforcement, stack changes); jacketing/strengthening detail sheets in retrofit work (final = jacketed size, `JK` types); steel columns by profile name; sections show base plate/cap and top level.

## 3. Required inputs
Mark; size (b×h / profile); plan position incl. offset; base level; top level; orientation of b vs h; whether a stack exists on each storey.

## 4. Interpretation method
1. Take final sizes (jacketed where `JK` applies; existing size where no JK type applies) `[VERIFIED KPwBI]`.
2. Split each column into **stacks per storey** (S1 base→L1 slab, S2, …). No stack where drawings show none above `[VERIFIED KPwBI]`.
3. **Base level:** if the drawings give no pile-cap/footing top, base = soffit of the deepest beam framing in at the lowest floor, flagged `LOW CONFIDENCE`; and the cap top is set to column base `[VERIFIED KPwBI]` (a modelling convention — confirm with the user).
4. Orientation: assume b along X, h along Y only if undrawn; log the assumption (`[VERIFIED KPwBI]` was assumed and logged) and check against column schedule sketches.

## 5. Revit procedure
1. Family/type: concrete rectangular column types `COLUMN bxh`; steel via UC/H-column families; duplicate types for missing profiles (`revit-families.md`).
2. `document.Create.NewFamilyInstance(XYZ, symbol, baseLevel, StructuralType.Column)` `[THEORY]`; set top level and offsets via `FAMILY_TOP_LEVEL_PARAM`, `FAMILY_BASE_LEVEL_OFFSET_PARAM`, `FAMILY_TOP_LEVEL_OFFSET_PARAM` `[THEORY]`. Verify names on the live model.
3. Rotation for orientation: `ElementTransformUtils.RotateElement` about the vertical axis through the location point `[THEORY]`.
4. Mark `K-<grid>/<row>-S<n>`; Comments with sheet/tag/provenance.
5. Joins: beams end at columns; keep the join at column ends (beams.md §5.5).
6. Slanted/tapered columns: `[OPEN]` not yet encountered.

## 6. Verification
Count vs schedule per mark×level; each stack continuous base→top with no gaps or overlaps; positions vs calibrated plan; every column lands on a cap/support or a drawn support; sizes vs schedule.

## 7. Failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Columns floating above foundation | Base level undefined | Use documented base rule; flag LOW CONFIDENCE | [VERIFIED KPwBI] |
| Wrong orientation | b/h assumed | Check schedule sketch / ask | [VERIFIED KPwBI] (assumption logged) |
| Extra posts beside columns | Misread end-on label | Trace leaders | [VERIFIED KPwBI] |

## 8. Related
`foundations.md`, `beams.md`, `revit-families.md`, `model-validation.md`.
