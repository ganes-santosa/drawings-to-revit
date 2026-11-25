# Walls — wall types (layers) and walls, joins, closing into rooms (OST_Walls)

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24 · Revit tested: none yet in this skill.
> Order of work: `workflows/element-modeling-workflow.md`. Hosting, joins, enclosure, heights: `building-logic.md`. Layers, materials, names: `types-and-materials.md`.

## 1. Scope
Basic (layered) walls: interior and exterior, partitions, parapets. Not here: curtain walls, facade cladding/niches (parked, `assets/legacy/`), structural walls (STR skill).

---

## A. Types
### A1. Where the types are
- **Wall-type plan / legend** (`TIPE DINDING`, `wall type`, `legenda dinding`): KPwBI A-4201..4207, found by `find_schedules.py --element walls` `[VERIFIED 2026-11-24]`. Contents not yet read `[OPEN]`.
- **Sections and 1:20/1:50 details** for build-ups (plaster, brick/hebel, gypsum on studs); **finish plans** (`FINISHING DINDING`, KPwBI A-41xx) and the finish schedule for faces.
- Specs (RKS) only to name a material, never for a dimension the drawings omit.
- No legend: thickness from the plan's line pair (calibrated) → `MEASURED`, LOW.

### A2. Extract per type
code (DN-01, W1 …) · description · total thickness · layers in order (material, mm, function) · exterior/interior finish codes · fire rating/notes · source sheet/page · provenance.

### A3. Catalog notes
- One Revit type per unique build-up (+ finishes if finishes are layers). The drawing code goes in Type Mark and the type name.
- Plan line pairs that do not match any legend thickness → conflict row, ask.

### A4–A5. Make the types
- Duplicate a Basic wall type, then set layers/material in the next call (`types-and-materials.md` §2–3) `[IMPORTED KPwBI-ARS]`.
- KPwBI created one-layer types named by material and thickness (`PJ LM01 200mm`, `KPW - Jembatan Dinding Limestone 250` with its own Type Mark) `[IMPORTED KPwBI-ARS]`.
- Multi-layer build-ups `[THEORY]`: test on one type, read back each layer width and material.

### A6. Gate
Every code in the legend and every wall-type tag on the plans resolves to a type; total and layer widths read back exactly.

---

## B. Placement
### B1. Positions and heights
Plan line pairs (centre and thickness from the pair, calibrated per sheet `[IMPORTED KPwBI-ARS]`); dimension chains; wall-type plan for the type; sections for base and top.

### B2. Instance table
mark · type · start/end (mm, plan system) · location line (centre / finish face ext / core) · base level + offset · top (level / unconnected height / attach to slab/beam) · joins at each end (L/T/X/free) · room(s) it bounds · source · provenance.

### B2b. Clean the table before placing `[THEORY]` (STR lesson: clean first, then audit)
1. De-duplicate (double-traced lines, same wall on two sheets).
2. **Merge collinear runs** of the same type/level/height that touch (walls whole) `[IMPORTED KPwBI-ARS]`.
3. **Snap ends**: each end lands on another wall's location line or face (T) or meets it at a corner (L); close gaps < tolerance; no overshoot past the target wall.
4. Check each drawn room is a closed loop.
5. Check every door/window code on the plan has a wall under it with enough length.

### B3. Interpretation rules
- Off-grid walls keep their drawn offset. Base level = highest level at or below the wall bottom; base offset + height carry exact z `[IMPORTED KPwBI-ARS]`.
- Location line: read which face is dimensioned; KPwBI user walls mixed Finish Face Exterior and Centerline `[IMPORTED KPwBI-ARS]`.
- **Exterior side:** `Wall.Orientation` points to the exterior side; check `Flipped` `[IMPORTED KPwBI-ARS]`. Raycasting from both sides (`ReferenceIntersector` in a 3D view, hit within 400 mm = blocked) worked except where the plan is open `[IMPORTED KPwBI-ARS]`.
- The user's own walls stay unless they ask; modifying them is allowed when it makes the model cleaner, and say so `[IMPORTED KPwBI-ARS]`.

### B4–B5. Revit procedure
- `[THEORY]` `Wall.Create(doc, Line, wallTypeId, levelId, heightFt, offsetFt, flip, structural:false)`; MCP `create_line_based_element` (category `OST_Walls`) exists, not yet tried.
- Set `WALL_HEIGHT_TYPE` (top constraint) only **after Regenerate** on a new wall `[IMPORTED KPwBI-ARS]`.
- Joins: rings and room walls keep default joins; boxes/claddings disallow joins (`WallUtils.DisallowWallJoinAtEnd`) `[IMPORTED KPwBI-ARS]`.
- **Before deleting joined walls:** disallow joins and `JoinGeometryUtils.UnjoinGeometry`, else the modal "Can't keep elements joined" blocks the API `[IMPORTED KPwBI-ARS]`.
- New walls sit exactly on the face of existing walls; 1–4 mm overlaps raised dialogs `[IMPORTED KPwBI-ARS]`.
- One level per call; Mark + Comments on every wall.

### B5b. Audit and repair `[THEORY]`
Per level: wall end gaps/overlaps, unjoined ends, duplicates (same line, same type), walls not reaching their top, rooms that do not close (`create_room` test points or a room-boundary check), warnings delta.

### B6. Verification
Counts and lengths per type vs plan; thickness per type; base/top z vs section; join and enclosure audit at zero or an accepted list.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| API "hangs" while deleting walls | Modal "Can't keep elements joined" | Disallow joins + unjoin first | [IMPORTED KPwBI-ARS] |
| Modal overlap dialog | New wall 1–4 mm into an existing one | Snap to the exact face | [IMPORTED KPwBI-ARS] |
| Inserts disappear | Host wall deleted | Capture insert data, re-place after | [IMPORTED KPwBI-ARS] |

## Related
`building-logic.md`, `types-and-materials.md`, `openings-placement.md`, `floors.md`.
