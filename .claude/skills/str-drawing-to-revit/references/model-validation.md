# Model validation — programmatic checks of model vs drawings

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: checklist from KPwBI; scripts not preserved

## 1. Purpose and scope
The check catalogue used by `workflows/quality-control-workflow.md`. Prefer numbers over eyeballs.

## 2. Check catalogue
| # | Check | Method | Tolerance / pass | Status |
|---|---|---|---|---|
| 1 | Warnings | `document.GetWarnings()` grouped by `GetDescriptionText()` | 0 unexplained | [IMPORTED KPwBI] |
| 2 | Marks | none blank, none duplicated per category (`scripts/revit/find_duplicates.cs`) | 0 | [IMPORTED KPwBI]; script [THEORY] |
| 3 | Duplicates | same type, collinear, overlapping; placed twice (same type + bounding box ±10 mm, `find_duplicates.cs`, run after every retried batch) | 0 | [IMPORTED KPwBI]; script [THEORY] |
| 4 | Clashes | **bounding-box** overlap (floors, foundations, framing) | explained only | [IMPORTED KPwBI] |
| 5 | Column continuity | each stack continuous base→top (gap/overlap > 5 mm), stack shift > 20 mm, free tops (`scripts/revit/audit_columns.cs`); lands on cap/support (`check_connectivity.cs`) | no gaps | [IMPORTED KPwBI]; script [THEORY] |
| 6 | Beam top vs slab SFL | beam top = SFL above, or step wall; under metal deck SFL−t | per level | [IMPORTED KPwBI] |
| 7 | Free ends / unsupported edges | list; each is drawn cantilever / joint face / void edge | documented | [IMPORTED KPwBI] |
| 8 | Counts vs tables | piles, caps, members per mark/type | exact | [IMPORTED KPwBI] |
| 9 | Position vs calibrated vectors | compare faces/locations to PDF line pairs | ≤16 mm noise; investigate >30 mm | [IMPORTED KPwBI] (script not preserved) |
| 10 | Expansion joints | nothing crosses | 0 crossings | [IMPORTED KPwBI] |
| 11 | Existing/demolished/new | anything "attached to nothing" confirmed | resolved | [IMPORTED KPwBI] |
| 12 | LOW CONFIDENCE review | filter Comments contains text; list | all listed | [IMPORTED KPwBI] |
| 13 | Y-justification / solid vs location | bbox centre vs LocationCurve | <1 mm lateral | [IMPORTED KPwBI] |
| 14 | Family/type vs schedule | type dims vs schedule | exact | [THEORY] |
| 15 | Level/grid read-back | elevations & endpoints vs tables | ≤0.5 mm | [THEORY] |
| 17 | **Connectivity (nothing floats)** | `scripts/revit/check_connectivity.cs`: connected-end rule (column bbox ±20 mm, or on another beam within half-width + 30 mm and between its ends); column bases on foundation/column/beam/wall; same floor only (height overlap), column must reach the beam soffit; `CANTILEVER` excluded | 0 unexplained | rule [VERIFIED RSUD]; this script [THEORY] |
| 19 | **Slab audit per level** | the 12 checks in `slabs.md` B6 (warnings, overlap, corner steps, U-caps/slivers, empty holes, short edges, beams outside slab, beam faces past slab edge, free ends / OV tips, framed panels without slab, beam end offsets, edge beam vs outline) | 0 / user-accepted list | checks [VERIFIED RSUD]; thresholds [EXPERIMENTAL RSUD]; scripts RSUD-specific |
| 20 | **Beam end offsets** | read back STRUCTURAL_BEAM_END0/1_ELEVATION of every beam; ≠ the expected offset for the beam's SFL zone, except drawn steps/upstands | 0 | [VERIFIED RSUD] (per-zone rule [THEORY]) |
| 18 | **Beam audit per floor** | free ends (cantilever tips vs others, listed), collinear overlaps > 50 mm, duplicate marks, beams through a column interior, long unsupported spans, LOW CONFIDENCE count (`beams.md` B6) | 0 / user-accepted list | audit [VERIFIED RSUD]; thresholds [EXPERIMENTAL RSUD]; script not in repo yet |
| 21 | **Roof framing audit** | `scripts/revit/audit_roof.cs`: member ends on another member's line or a support, in 3D (arcs split into segments); short members; plus counts per truss and heel/ridge z vs sections (`roof-framing.md` B6) | 0 / user-accepted list | [THEORY] |
| 16 | Orphans | elements without Mark or on wrong level | 0 | [THEORY] |

## 3. Reusable checker
`scripts/pdf_calibrate.py` supports #9 on the drawing side (residuals). The Revit-side extraction script is a backlog item: write once Revit is available, verify, and store in `assets/examples/scripts/`.

## 4. Failure cases
| Symptom | Cause | Fix |
|---|---|---|
| Edge test flags 30–80 mm on hatched frames | Line-weight/drafting noise | Judge against drawing; not a model error `[IMPORTED KPwBI]` |

## 5. Related
`workflows/quality-control-workflow.md`, element files §Verification.
