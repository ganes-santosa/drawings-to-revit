# Types and materials — system types, compound layers, materials, names, marks

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24 · Revit tested: none yet in this skill.

## 1. Scope
Shared Stage A mechanics for the system families (walls, floors, ceilings, roofs): duplicating a type, setting compound layers, materials, naming, Type Marks, Marks and Comments. Door/window (loadable) families: `openings-families.md`.

## 2. Duplicate a system type
- Find a base type of the right kind (`WallType` with `Kind == WallKind.Basic`, `FloorType`, `CeilingType`, `RoofType`) and `Duplicate("<name>")` `[IMPORTED KPwBI-ARS]`.
- **Create types in one call, set parameters/layers in the next, place in a third** when stability matters `[IMPORTED KPwBI-ARS]`.
- Revit can delete elements at commit ("Can't make type") although the script returned OK: read the type back in a **separate later call** `[IMPORTED KPwBI-ARS]`.

## 3. Compound structure (layers)
- `[IMPORTED KPwBI-ARS]` KPwBI used one-layer types: `cs = type.GetCompoundStructure(); cs.SetLayerWidth(0, mm/304.8); cs.SetMaterialId(0, matId); type.SetCompoundStructure(cs);` (walls, roofs).
- `[THEORY]` multi-layer build-ups (plaster 15 + brick 120 + plaster 15): build a `List<CompoundStructureLayer>` (function `Finish1/Finish2/Structure/Substrate/Membrane`), `CompoundStructure.CreateSimpleCompoundStructure(layers)`, mark the core boundary, `SetCompoundStructure`. Test on one type first.
- **Decision per project (ask once, record):** wall finishes as layers inside the wall type, or as separate thin finish walls. Default proposal: layers, when the wall-type legend gives the build-up `[OPEN]`.
- When a roof/floor type changes thickness, shift the base offset by the difference to keep the top surface where it was `[IMPORTED KPwBI-ARS]`.

## 4. Materials
- Find by name: `new FilteredElementCollector(doc).OfClass(typeof(Material))`. If missing, propose a name and create only after the user agrees `[IMPORTED STR]`.
- **Name materials with the project spec code** `[IMPORTED KPwBI-ARS]`: `LM01 - Limestone`, `GK01 - Genteng Keramik`, `W1 - Cat Exterior Water Based (Grey)`, `GR01 - Granit Grey (Graphite) 20mm`, `TG02 - Laminated Glass Clear`, `AL01 - Aluminium Solid Panel Grey`. Codes come from the elevation finish legend or finish schedule.
- Paint a finish on one face: `HostObjectUtils.GetSideFaces(wall, ShellLayerType.Exterior)` → `doc.Paint(id, face, matId)`; pick faces by normal `[IMPORTED KPwBI-ARS]`.

## 5. Names, marks, comments `[IMPORTED KPwBI-ARS]`
- **Type names:** code + description + size: `AW-04 1800x3500`, `D42 - Bulletproof double 1900x3000`, `PJ LM01 200mm`, `GK01 - Atap Genteng Keramik 120mm`. Keep Indonesian names where the project uses them. No "CLAUDE".
- **Type Mark:** every new type gets its own Type Mark (duplicate Type Marks raised warnings).
- **Marks** (`ALL_MODEL_MARK`) readable and unique: `W-<lvl>-nnn` (walls), `S-<lvl>-nn` (floors), `DR-<code>-<lvl>-nn` (doors), `W-AW-xx-<lvl>-nn` (windows), `R-AT-01` (roofs). Refer to marks in logs, not ids (ids change when elements are recreated).
- **Comments** (`ALL_MODEL_INSTANCE_COMMENTS`): category tag + source sheet + provenance/confidence, e.g. `WALL DN-01 A-4202 EXPLICIT` or `... LOW CONFIDENCE`.

## 6. Gate
Every catalogued type exists, reads back the catalogued thickness/layers/material (from parameters, not the name), has a unique Type Mark, and survives into a later call.

## Related
`walls.md`, `floors.md`, `ceilings.md`, `roofs.md`, `openings-families.md`, `assets/examples/type-catalog-template.csv`.
