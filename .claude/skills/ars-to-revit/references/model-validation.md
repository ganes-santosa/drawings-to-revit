# Model validation — checks per element group and the final audit

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24

## 1. Scope
What to check, how, and the pass condition. The order of use: `workflows/quality-control-workflow.md`.

## 2. Checks
| # | Check | How | Pass | Status |
|---|---|---|---|---|
| 1 | Persistence | Re-collect new elements in a **separate, later call** | All still exist | [IMPORTED KPwBI-ARS] |
| 2 | Warnings delta | `document.GetWarnings()` grouped by description, before vs after (separate read-only call) | Not higher, or each new one explained | [IMPORTED KPwBI-ARS] |
| 3 | Inserts hosted and cutting | `host.FindInserts(true,true,true,true)` contains each door/window; host volume dropped | 100 % | [IMPORTED KPwBI-ARS] |
| 4 | Inserts within wall length, no overlaps | Location along wall ± half width vs wall ends; bbox overlap per wall | 0 failures | [IMPORTED KPwBI-ARS] |
| 5 | Counts vs schedule | Instances per code per level vs schedule/keyplan; walls/floors per type vs plan | Equal, or listed | [THEORY] |
| 6 | Wall joins and enclosure | End gaps/overlaps; unjoined ends; rooms close (room placement test) | 0 or accepted list | [THEORY] |
| 7 | Floors/ceilings inside walls, at the right height | Outline vs wall faces; top z vs FFL; ceiling z vs plan and below structure | 0 failures | [THEORY] |
| 8 | Roof heights | Bbox z of eave/ridge vs section; slopes read back | ± 5 mm | [IMPORTED KPwBI-ARS] |
| 9 | Positions vs drawing | Elevation overlay for openings; calibrated plan overlay for walls | Within tolerance | [IMPORTED KPwBI-ARS] |
| 10 | Duplicates | Same type + same location (walls, floors, inserts); copied STR slabs in the ARS model | 0 | [IMPORTED KPwBI-ARS] |
| 11 | STR consistency | ARS vs STR link bbox clashes; column covers on real columns | Listed and asked | [IMPORTED KPwBI-ARS] |
| 12 | Marks and comments | Every element: unique Mark, Comments with source + provenance; unique Type Marks | 100 % | [IMPORTED KPwBI-ARS] |
| 13 | LOW CONFIDENCE list | Collect Comments containing LOW | Listed in the report | [IMPORTED KPwBI-ARS] |
| 14 | 3D image vs elevation/render | Exported view image | Matches | [IMPORTED KPwBI-ARS] |

- Bounding-box overlap checks were reliable; intersect filters threw `[IMPORTED STR]`.
- **Look behind what you model:** piers stopped short exposed a column; extend to the slab underside `[IMPORTED KPwBI-ARS]`.

## 3. Common mistakes seen `[IMPORTED KPwBI-ARS]`
Modelling from a hatch/outline without a label; placing on grids instead of real positions; flipping before Regenerate; loading and placing in one call; trusting a returned "OK" without re-checking; editing the wrong open document; naming views with CLAUDE.

## Related
`building-logic.md`, `workflows/quality-control-workflow.md`, `troubleshooting.md`.
