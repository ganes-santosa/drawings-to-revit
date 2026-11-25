# Ceilings — ceiling types and ceilings at drawn heights (OST_Ceilings)

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24 · Revit tested: none. **No earlier project experience:** KPwBI did not model ceilings; everything here is `[THEORY]` until tested.
> Order of work: `workflows/element-modeling-workflow.md`. Room boundaries and structure above: `building-logic.md`. Types: `types-and-materials.md`.

## 1. Scope
Flat ceilings per room/zone at the drawn height (gypsum, acoustic tile, ACP, exposed). Not here: bulkheads/drop details beyond a simple height step, light fittings, MEP.

---

## A. Types
### A1. Where
**Ceiling plans** (`RENCANA PLAFOND`, `FINISHING PLAFOND`, `DENAH PLAFON`; KPwBI A-4301..4305, Part2 p18–20, `find_schedules.py --element ceilings` `[VERIFIED 2026-11-24]`); ceiling legend codes; standard details (KPwBI Part3: `PEKERJAAN - PLAFOND GYPSUM`, `PLAFOND AKUSTIK` p68–69) for board thickness and suspension depth; sections for heights.
### A2. Extract
code · material/board · thickness · suspension/frame depth (record, usually not modelled) · height(s) above FFL · rooms · source.
### A3. Catalog
One type per board build-up; heights belong to instances, not types.
### A4–A5. Make the types `[THEORY]`
Duplicate a compound `CeilingType`, set layer width/material (`types-and-materials.md` §3).
### A6. Gate
Thickness and material read back; every ceiling code on the plan resolves to a type.

---

## B. Placement
### B1. Where
Ceiling plan zones (often follow rooms, sometimes span several), height tags (`+2.800`, `H = 3000 dari FFL`), sections.
### B2. Instance table
mark · type · outline (room loop / drawn zone) · level · height offset · structure-above clearance · source · provenance.
### B4–B5. Revit procedure `[THEORY]`
- `Ceiling.Create(doc, List<CurveLoop>, typeId, levelId)` (Revit 2022+), then `CEILING_HEIGHTABOVELEVEL_PARAM`.
- MCP `create_surface_based_element` supports `OST_Ceilings` (not yet tried).
- Check the ceiling sits below the beam soffit/slab underside above: a ceiling higher than the structure is a conflict to report, not to fix.
### B6. Verification
Area per zone; height per zone vs plan/section; inside room boundaries; below structure.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| — | — | — | — |

## Related
`floors.md`, `walls.md`, `building-logic.md` §2.7.
