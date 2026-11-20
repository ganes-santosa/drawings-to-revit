# Foundations — isolated, strip, raft, pile caps, piles (OST_StructuralFoundation)

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: 2026 (KPwBI, DirectShape convention); native foundation families untested

## 1. Purpose and scope
Foundation identification, levels, and modelling. Pile design/capacity is out of scope.

## 2. Drawing conventions
Foundation plan: footing/cap marks, pile symbols (type by glyph/letter), pile tables (type, diameter, Leff/length, count), strip footing widths, raft outlines; sections give depths and top levels; check "Eksisting/Existing" status and whether elements belong to demolished structures.

## 3. Required inputs
Type/mark, plan size and position, top and bottom levels (often missing), pile type, diameter, length (Leff from cap soffit), count per cap, concrete cover/blinding if modelled.

## 4. Interpretation method
- Cross-check pile counts by type against the sheet table (KPwBI matched exactly after glyph identification) `[VERIFIED KPwBI]`.
- Missing cap top: set to column base / beam soffit rule, flag `LOW CONFIDENCE`; confirm (columns.md §4.3).
- Existing vs demolished vs new per element; ask when a cap is "attached to nothing" `[VERIFIED KPwBI]` (4 caps of a demolished canopy).

## 5. Revit procedure
1. **Company convention: DirectShape in category Structural Foundations** `[VERIFIED KPwBI]`. Native option (Isolated/Wall Foundation, Foundation Slab families, `NewFamilyInstance` with `StructuralType.Footing`) `[THEORY]` — prefer native families where the project provides them; ask.
2. Two groups per foundation: `PONDASI <type> <grid> - PILE CAP` and `... - TIANG BOR`; marks `PC-<type>-<grid>`, `TB-<type>-x/y` `[VERIFIED KPwBI]`.
3. DirectShape: `DirectShape.CreateElement(document, new ElementId(BuiltInCategory.OST_StructuralFoundation))` + `SetShape` with solids from `GeometryCreationUtilities.CreateExtrusionGeometry` `[VERIFIED KPwBI for extrusion approach; exact code not preserved]`.
4. Pile length = Leff from cap soffit.
5. Delete a foundation by deleting its group: `document.Delete(group.Id)` `[VERIFIED KPwBI]`.

## 6. Verification
Counts per type vs table; plan positions vs calibrated drawing; cap top/bottom vs documented levels; no overlapping caps; every column lands on a cap.

## 7. Failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Orphan caps | Existing plan included demolished frame | Ask; model from the correct (new) sheets | [VERIFIED KPwBI] |
| Pile type miscount | Glyph confusion A/B/C | Cross-check table | [VERIFIED KPwBI] |

## 8. Related
`columns.md`, `revit-families.md`, `reinforcement.md`.
