# Live test plan — run when Revit + MCP are available

Purpose: promote `[THEORY]` items to `[VERIFIED …]`. Use a **scratch project**, one element each, read back, then delete. Record Revit version/tool; update the referenced file + `lessons-learned.md` + `DEVLOG.md`. Do not promote without an inspected result.

| P | Test | Pass criterion | Updates |
|---|---|---|---|
| 1 | Tool discovery + probe script (api §3) | Version, counts returned | revit-api-and-automation (environment record) |
| 2 | Transaction semantics: create+delete a model line; error → rollback? | Behaviour documented | api §4 |
| 3 | Units: place line of 1000 mm, read back length | 1000 mm ±0.01 | project-setup |
| 4 | Levels/grids create + read back | exact | grids-and-levels |
| 5 | List structural families/types; duplicate a beam type + set b,h in separate call | type dims as set | revit-families |
| 6 | Beam: NewFamilyInstance, Z justification Top + offsets, Y_JUSTIFICATION=1; check bbox centre vs location | <1 mm | beams |
| 7 | DisallowJoinAtEnd; join behaviour at column | no notch | beams |
| 8 | Column: base/top level + offsets, rotation | positions as set | columns |
| 9 | Floor.Create with opening; thickness type; top offset | area, top elev | slabs |
| 11 | Foundation: native `Footing` vs DirectShape extrusion | both created | foundations |
| 12 | `document.GetWarnings()` extraction + bbox clash helper | works | model-validation |
| 13 | Selected-elements tool; view creation (plan, 3D with section box) | works | api / troubleshooting |
| 14 | End-to-end pilot on a real drawing sheet (user supplies PDF) | QC passes | all |
