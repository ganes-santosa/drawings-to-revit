# Model validation — programmatic checks of model vs drawings

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: checklist from KPwBI; scripts not preserved

## 1. Purpose and scope
The check catalogue used by `workflows/quality-control-workflow.md`. Prefer numbers over eyeballs.

## 2. Check catalogue
| # | Check | Method | Tolerance / pass | Status |
|---|---|---|---|---|
| 1 | Warnings | `document.GetWarnings()` grouped by `GetDescriptionText()` | 0 unexplained | [VERIFIED KPwBI] |
| 2 | Marks | none blank, none duplicated per category | 0 | [VERIFIED KPwBI] |
| 3 | Duplicates | same type, collinear, overlapping | 0 | [VERIFIED KPwBI] |
| 4 | Clashes | **bounding-box** overlap (floors, foundations, framing) | explained only | [VERIFIED KPwBI] |
| 5 | Column continuity | each stack continuous base→top; lands on cap/support | no gaps | [VERIFIED KPwBI] |
| 6 | Beam top vs slab SFL | beam top = SFL above, or step wall; under metal deck SFL−t | per level | [VERIFIED KPwBI] |
| 7 | Free ends / unsupported edges | list; each is drawn cantilever / joint face / void edge | documented | [VERIFIED KPwBI] |
| 8 | Counts vs tables | piles, caps, members per mark/type | exact | [VERIFIED KPwBI] |
| 9 | Position vs calibrated vectors | compare faces/locations to PDF line pairs | ≤16 mm noise; investigate >30 mm | [VERIFIED KPwBI] (script not preserved) |
| 10 | Expansion joints | nothing crosses | 0 crossings | [VERIFIED KPwBI] |
| 11 | Existing/demolished/new | anything "attached to nothing" confirmed | resolved | [VERIFIED KPwBI] |
| 12 | LOW CONFIDENCE review | filter Comments contains text; list | all listed | [VERIFIED KPwBI] |
| 13 | Y-justification / solid vs location | bbox centre vs LocationCurve | <1 mm lateral | [VERIFIED KPwBI] |
| 14 | Family/type vs schedule | type dims vs schedule | exact | [THEORY] |
| 15 | Level/grid read-back | elevations & endpoints vs tables | ≤0.5 mm | [THEORY] |
| 16 | Orphans | elements without Mark or on wrong level | 0 | [THEORY] |

## 3. Reusable checker
`scripts/pdf_calibrate.py` supports #9 on the drawing side (residuals). The Revit-side extraction script is a backlog item: write once Revit is available, verify, and store in `assets/examples/scripts/`.

## 4. Failure cases
| Symptom | Cause | Fix |
|---|---|---|
| Edge test flags 30–80 mm on hatched frames | Line-weight/drafting noise | Judge against drawing; not a model error `[VERIFIED KPwBI]` |

## 5. Related
`workflows/quality-control-workflow.md`, element files §Verification.
