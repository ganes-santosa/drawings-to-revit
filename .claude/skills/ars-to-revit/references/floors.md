# Floors — architectural / finish floors inside wall boundaries (OST_Floors)

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24 · Revit tested: none yet in this skill.
> Order of work: `workflows/element-modeling-workflow.md`. Boundaries and heights: `building-logic.md`. Types: `types-and-materials.md`.

## 1. Scope
Architectural floors: finish build-ups (SFL → FFL) per room/zone, and slabs when the project has no STR model and the user asks for them. Structural slabs normally come from the STR skill/link; the STR slab lessons (outline cleaning, edge = edge-beam face) live there.

**Decide once per project (ask, record):** (a) finish floors only on top of the STR slabs, (b) one combined floor per level, or (c) floors from STR copied in. `[OPEN]`

---

## A. Types
### A1. Where
**Finish floor plans** (`FINISHING LANTAI`, KPwBI A-4001..4007, `find_schedules.py --element finishes` `[VERIFIED 2026-11-24]`), finish schedule/legend codes (GR01, HT…), details for build-up (screed + tile thickness), sections for SFL/FFL.
### A2. Extract
finish code · material · finish thickness · screed thickness · total (= FFL − SFL) · rooms/zones · source.
### A3. Catalog
One type per finish build-up; name `<code> - <material> <total>mm`. Total thickness must equal FFL − SFL for that zone, else conflict.
### A4–A5. Make the types
Duplicate a FloorType, set compound layers (`types-and-materials.md` §3) `[THEORY]`.
### A6. Gate
Thickness and material read back; every finish code on the plans resolves to a type.

---

## B. Placement
### B1. Where
Finish plan zone outlines; walls already modelled (room loops); FFL per zone from sections/level marks.
### B2. Instance table
mark · type · outline source (room loop from walls / drawn zone) · level · top offset (FFL − level) · openings (shafts, stairs) · source · provenance.
### B2b. Clean the outline before placing `[IMPORTED STR]` (slab lessons)
Outline = drawn polygon from vector lines, never raster tracing; no slivers or notches; close every loop; edges on wall faces (decide finish face vs core per project, `building-logic.md` §2.6).
### B4–B5. Revit procedure
- `Floor.Create(doc, List<CurveLoop>, typeId, levelId)`, then `FLOOR_HEIGHTABOVELEVEL_PARAM` for the offset `[IMPORTED KPwBI-ARS]`.
- To change an outline: delete and recreate (no hosted elements) `[IMPORTED KPwBI-ARS]`.
- **Never create temporary overlaps:** the modal "floors overlap" freezes the API `[IMPORTED KPwBI-ARS]`.
- Structural slab tops at SFL (FFL − 50) on KPwBI `[IMPORTED KPwBI-ARS]`.
- Sloped floor / ramp: KPwBI made a 15.3 % ramp and a bridge ramp +7800 → +6900 `[IMPORTED KPwBI-ARS]` (method not recorded: `SlabShapeEditor` or slope arrow `[THEORY]`).
- At facades, the floor edge stops at the wall face; a slab edge beyond it showed as a grey band in niches `[IMPORTED KPwBI-ARS]`.
- One level per call `[IMPORTED STR]`. Area reads 0 until `doc.Regenerate()` `[IMPORTED STR]`.
### B6. Verification
Area per zone vs drawing; top z = FFL; no floor outside its walls; no overlaps between floors of the same level.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| API "hangs" while rebuilding floors | Modal "floors overlap" | Order operations to avoid overlap | [IMPORTED KPwBI-ARS] |
| Grey band visible in facade niches | Slab edge beyond wall face | Recreate floor to the wall face | [IMPORTED KPwBI-ARS] |
| Copied STR slabs duplicated in ARS model | Copied, not linked | Audit duplicates; ask before deleting | [IMPORTED KPwBI-ARS] |

## Related
`walls.md`, `ceilings.md`, `building-logic.md`, `project-setup.md` §4 (FFL/SFL).
