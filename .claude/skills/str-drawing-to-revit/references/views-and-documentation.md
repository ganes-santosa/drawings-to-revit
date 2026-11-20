# Views and documentation — inspection views, filters, naming, sheets

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: 2026 (KPwBI, imported); nothing re-tested here
> Source: legacy skill Part 4 (`assets/legacy/structural-drawings-to-revit-v1-KPwBI.md`).

## 1. Purpose and scope
Working views that let the user and Claude inspect the model per level, view filters that make problems visible, and naming. Sheets, dimensions, tags, schedules and annotation standards: **no tested standard yet** `[OPEN]` — follow the project's own template and ask.

## 2. Inspection views (what was actually done) `[IMPORTED KPwBI]`
| View | Name pattern | Settings |
|---|---|---|
| Structural plan per level | `0n <LEVEL> - Denah struktur` | Discipline Coordination; view range from slab top −1.7 m to about +1.2 m; crop around the building |
| 3D per level | `0n <LEVEL> - 3D` | Section box limited to that level |
| Overall 3D | `00 STRUKTUR - 3D semua level` | All levels |

All of them: show only structural categories; floors 45–55% transparent.

## 3. View filters `[IMPORTED KPwBI]`
- `LOW CONFIDENCE`: Comments contains "LOW CONFIDENCE" → red, **highest priority**.
- Steel beams blue, concrete beams grey.
- Slabs coloured by thickness: 150 blue, 120 yellow, 300/500 grey.

## 4. Naming rules
- Project-style names from the start; **no AI name** ("CLAUDE - …") in view names. Views first named that way had to be renamed `[IMPORTED KPwBI]`.
- Rename with `v.Name = newName` inside try/catch **per view** (names must be unique); report OK/FAIL per view `[IMPORTED KPwBI]`.

## 5. Revit procedure `[THEORY]` until re-run
- Plan: `ViewPlan.Create(document, viewFamilyTypeId, levelId)`; pick the ViewFamilyType with `ViewFamily.StructuralPlan`.
- 3D: `View3D.CreateIsometric(document, viewFamilyTypeId)`; `view.SetSectionBox(BoundingBoxXYZ)`.
- View range: `PlanViewRange` via `viewPlan.GetViewRange()` / `SetViewRange()`.
- Filters: `ParameterFilterElement.Create` with a rule on `ALL_MODEL_INSTANCE_COMMENTS` contains "LOW CONFIDENCE"; `view.AddFilter`, `view.SetFilterOverrides`.

## 6. Verification
Each level has its plan + 3D; LOW CONFIDENCE elements show red; no structural element is hidden unexpectedly (compare category counts in the view vs the model).

## 7. Failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| All slabs invisible in a structural plan | The Structural Plan view type's template injected 6 filters, incl. a hidden "Floors - Concrete NOT" | Remove the template's filters from working views | [IMPORTED KPwBI] |
| View rename fails | Name already used | try/catch per view, unique names | [IMPORTED KPwBI] |

## 8. Related
`model-validation.md`, `troubleshooting.md`, `revit-api-and-automation.md`.
