# Legacy source (do not edit)

`architectural-drawings-to-revit-v1-KPwBI.md` is a byte-identical copy of the user's earlier single-file skill (`architectural-drawings-to-revit.skill`, also installed as a plugin with the same description; plugin files not found on disk, assumed identical). It records the KPwBI DIY tender model (Gedung Utama, Gedung Penunjang, skybridge, site), Revit 2026, Nov 2026.

Its knowledge is distributed into the skill, tagged `[IMPORTED KPwBI-ARS]`. Item-by-item map (legacy → current home). "Parked" = not routed now; this file is the only copy, by design.

| Legacy item | Now in |
|---|---|
| Purpose/scope, consult table | SKILL.md header, §2 focus/parked list |
| Principle 1 drawings = truth; 2 drawn-undimensioned | SKILL.md §3.4, §4 preferences |
| 3 interpretations not facts | SKILL.md §3.5, drawing-interpretation.md §5 |
| 4 ask before conflicts/deleting/batches | SKILL.md §3.2, §3.10 |
| 5 native families over DirectShape | SKILL.md §4 |
| 6 final renovated state | SKILL.md §3.9 |
| 7 exterior first | full-modeling-workflow.md Phase 3 (per-project choice, **changed** from rule) |
| 8 don't clean up the user's content | SKILL.md §3.10, walls.md B3 |
| 9 follow STR where it differs | SKILL.md §5, project-setup.md §6 (**changed**: ask, not rank; user brief 2026-11-24) |
| 10 walls whole, inserts cut | building-logic.md §2.3, walls.md B2b, openings-placement.md B2b |
| 11 quota-minimal, report + "save the model" | SKILL.md §4 preferences, §7 |
| 12 no CLAUDE in names | SKILL.md §4, types-and-materials.md §5 |
| 13 keep deferred things deferred; 14 match sibling system | SKILL.md §4 preferences |
| End-to-end workflow 1–8 | full-modeling-workflow.md, project-setup.md §2 (orient) |
| QC requirements (minimum per package) | model-validation.md §2 (#1–3, 12, 14) |
| Known limitations | revit-api-and-automation.md §1, openings-placement.md B4 (100 mm doors), SKILL.md §2 parked |
| A.1 finding sheets, sheet types | drawing-interpretation.md §2–3 |
| A.1 calibration, raster measuring, nested transforms, vector fills | drawing-interpretation.md §4 |
| A.1 datums and levels | project-setup.md §4 |
| A.1 elevation overlay | drawing-interpretation.md §5, openings-placement.md B6 |
| A.2 wall-type/finish/ceiling plans, demolition, standard details | walls.md A1, floors.md A1, ceilings.md A1, drawing-interpretation.md §2 |
| B.0 sequence | building-logic.md §6, full-modeling-workflow.md (facade/canopy/site steps parked) |
| B.1 linked structure | project-setup.md §6 |
| B.2 walls | walls.md A4–A5, B3–B5 |
| B.3 cladding, niches, cornices, DirectShape categories | **Parked** (legacy only); paint faces → types-and-materials.md §4; exterior-wall raycast → walls.md B3; slab edge in niches → floors.md B4–B5 |
| B.4 windows | openings-families.md A5, openings-placement.md B5 |
| B.5 doors | openings-families.md A3/A5, openings-placement.md B2b–B5, open problem B4 |
| B.6 floors/slabs, ramp | floors.md B4–B5 |
| B.7 roofs | roofs.md A4–A5, B1, B4–B5 |
| B.8 canopies, column covers, bridge, site/toposolid | **Parked** (legacy only); distinct Type Marks → types-and-materials.md §5; STR alignment → project-setup.md §6 |
| C.1 marks, comments, material names, type names | types-and-materials.md §4–5 |
| C.1 check views | revit-api-and-automation.md §5 |
| C.1 project docs (master + area docs) | full-modeling-workflow.md (project log outside the skill) |
| C.2 gaps (sheets, tags, schedules, rooms) | SKILL.md §2 parked |
| D.1 automation (scripts, errors, transactions, quirks, AppDomain cache, families, active doc, say_hello) | revit-api-and-automation.md §1–4 |
| D.1 PC bridge (container staging) | revit-api-and-automation.md §6 (not used locally) |
| D.1 visual check | revit-api-and-automation.md §5 |
| E.1 QC checks, look behind, duplicate Type Marks, final audit | model-validation.md §2 |
| E.2 common mistakes | model-validation.md §3 |
| F trial-and-error rows 1–36 | troubleshooting.md (rows cite `F#`); parked rows F1, F13, F14, F20, F21, F30, F34 stay here; F17 (beam Y-justification) belongs to the STR skill |
| G KPwBI project facts (paths, coordinates, levels, sheet map, materials) | Project facts, not skill: stay here. Example values quoted in project-setup.md §3 and types-and-materials.md §4 |

Keep this file as the evidence trail. If a reference contradicts it, check here first, then re-test.
