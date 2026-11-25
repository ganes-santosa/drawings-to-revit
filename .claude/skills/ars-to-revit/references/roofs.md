# Roofs — roof types, footprint roofs, slopes, flat decks (OST_Roofs)

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24 · Revit tested: none yet in this skill.
> Order of work: `workflows/element-modeling-workflow.md`. Supports: `building-logic.md` §2.8. Types: `types-and-materials.md`.

## 1. Scope
Pitched (hip/gable) footprint roofs, flat roof decks, roof openings. Not here: roof steel/trusses (STR skill), canopies and skylights (parked, `assets/legacy/`).

---

## A. Types
### A1. Where
Roof plan (`RENCANA ATAP`, `DENAH ATAP`, `TOP ATAP`), sections (pitch per face, eave/ridge levels), roof details (covering + battens), elevation finish legend (GK01 tile …).
### A2. Extract
covering code · material · modelled thickness · pitch per face (degrees or rise/run) · eave level · ridge / top level · overhang · source.
### A3. Catalog
One type per covering build-up, named `GK01 - Atap Genteng Keramik 120mm` `[IMPORTED KPwBI-ARS]`.
### A4–A5. Make the types
Duplicate an existing `RoofType`; set layer width/material via `CompoundStructure` `[IMPORTED KPwBI-ARS]`.
### A6. Gate
Thickness/material read back.

---

## B. Placement
### B1. Where
Roof plan outline (eave line), section pitches **per direction** (they can differ: 34.9° vs 29.4° on KPwBI Penunjang), truss geometry from STR (eave tip, ridge, slope per face; purlin top = roof underside) `[IMPORTED KPwBI-ARS]`.
### B2. Instance table
mark · type · footprint loop(s) (outer + openings) · base level + offset · slope per edge (by coordinates) · cutoff level · supports · source · provenance.
### B4–B5. Revit procedure `[IMPORTED KPwBI-ARS]`
- `doc.Create.NewFootPrintRoof(CurveArray, level, roofType, out ModelCurveArray)`; an inner loop = opening.
- Per edge: `roof.set_DefinesSlope(mc, true)` and `roof.set_SlopeAngle(mc, rise/run)` (**rise/run, not radians**).
- **Assign slopes by curve coordinates, not by index** (the profile order differs from the input order).
- **The sketch plane is the roof underside; thickness is added upward** (vertical thickness = t / cos(pitch)). Offset the base so the top matches the section.
- `Regenerate` before reading bounding boxes; probe heights with a downward `ReferenceIntersector`.
- Flat top on a hip (KPwBI Penunjang): Cutoff Level at TOP ATAP minus the thickness/cos correction (356 mm there) leaves an opening exactly at the deck lines; fill with a 200 mm concrete deck at TOP ATAP, a coping ring and finials.
- Swapping to a type of another thickness: adjust the base offset by the difference to keep the top surface.
- The user wants roofs editable: build FootPrintRoofs, not DirectShapes.
- `[LIMIT]` `ROOF_CURVE_OVERHANG` BuiltInParameter absent in 2026: use object methods (`FootPrintRoof.get_Overhang`) `[IMPORTED STR]`.
### B6. Verification
Bounding-box z of eave and ridge vs section; slope per face read back; roof underside vs truss/purlin top (STR); 3D image vs elevation.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Wrong faces sloped | Slopes set by curve index; angle in radians | Match curves by coordinates; rise/run | [IMPORTED KPwBI-ARS] |
| Roof too high by its thickness | Sketched at the eave top | Sketch plane = underside; offset by t/cos | [IMPORTED KPwBI-ARS] |
| Roof top read as glazed skylight | Identity from hatch alone | Say it is an inference; ask | [IMPORTED KPwBI-ARS] |

## Related
`building-logic.md`, `project-setup.md` §6 (STR link), `types-and-materials.md`.
