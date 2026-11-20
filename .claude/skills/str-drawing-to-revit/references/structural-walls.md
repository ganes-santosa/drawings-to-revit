# Structural walls — shear/retaining/core walls (OST_Walls, structural usage)

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: none. Content is `[THEORY]` pending live tests.

## 1. Purpose and scope
Concrete/masonry structural walls, step walls, retaining walls. Architectural partitions excluded.

## 2. Drawing conventions
Walls as thick hatched/filled pairs on plans; wall marks and schedules (thickness, height, reinforcement); sections give top/base levels; openings dimensioned; boundary elements/column strips at ends.

## 3. Required inputs
Centreline or face position, thickness, base/top levels (+offsets), openings, location line intent, mark.

## 4. Interpretation method
Determine whether drawn lines are faces or centreline; pick location line accordingly; base/top from sections.

## 5. Revit procedure `[THEORY]`
1. `Wall.Create(document, Curve, wallTypeId, levelId, heightFt, offsetFt, flip, structural=true)`.
2. Set `WALL_KEY_REF_PARAM` (location line), `WALL_STRUCTURAL_USAGE_PARAM`, top constraint (`WALL_HEIGHT_TYPE`) and offsets.
3. Openings: place via wall-hosted families or `document.Create.NewOpening(wall, p1, p2)`.
4. Step walls beside slab level changes (see `beams.md` §4.3, `[IMPORTED KPwBI]` convention).
5. Join with columns/beams/slabs; check joins visually and by geometry.

## 6. Verification
Length/thickness/height vs drawing; base/top levels; openings count; structural usage flagged; no overlaps with columns.

## 7. Failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Wall off by half thickness | Location line mismatch | Set location line to match drawn reference | [THEORY] |

## 8. Related
`slabs.md`, `columns.md`, `reinforcement.md`.
