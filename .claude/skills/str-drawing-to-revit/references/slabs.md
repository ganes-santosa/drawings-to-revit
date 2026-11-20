# Slabs — structural floors (OST_Floors)

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: 2026 (KPwBI, imported); not re-tested here

## 1. Purpose and scope
Slab outlines, thickness types, openings, steps, expansion-joint splits. Metal-deck slabs affect steel levels (`beams.md`).

## 2. Drawing conventions
Slab plan: thick outline (line width heavy), slab tags (S1, SN1A…) with a slab schedule (thickness, reinforcement); X-marked cells = voids; stair/shaft outlines = openings; falls/slopes by arrows; metal-deck sections on detail sheets; double thin line = expansion joint. Tag text is often readable by `pdftotext -bbox`.

## 3. Required inputs
Outline polygon; tag → thickness (schedule **and** detail sheet); level and top elevation (SFL); openings; slopes/steps; joint locations.

## 4. Interpretation method
- Outline = the drawn thick line, **not** beam faces or grid-derived guesses `[VERIFIED KPwBI]` (grid guess 1825/24575 vs drawn 1944/24458 with jogs; beam-face-edge slabs left cantilever stubs).
- Compare schedule and detail thickness; on conflict ask (KPwBI: table 120 vs detail 150 metal deck → user chose 150) `[VERIFIED KPwBI]`.
- Split at expansion joints.

## 5. Revit procedure
1. Floor types per thickness/composition, named by thickness + tags, e.g. `PELAT BETON 120mm (S1/S2)`, `PELAT METAL DECK 150mm` `[VERIFIED KPwBI]`. Mark structural (`FLOOR_PARAM_IS_STRUCTURAL`) `[THEORY]`.
2. Create via `Floor.Create(document, List<CurveLoop>, floorTypeId, levelId)` (Revit 2022+) `[THEORY]`; older: `NewFloor`. Offset from level so top = SFL (`FLOOR_HEIGHTABOVELEVEL_PARAM`).
3. Openings as inner loops in the same CurveLoop list, or `NewOpening` `[THEORY]`.
4. **Overlapping floors:** rebuilding a floor that overlaps a neighbour raises a modal "Highlighted floors overlap" warning that blocks the API and looks like a timeout. Rebuild in an order that never overlaps, few per call `[VERIFIED KPwBI]`.
5. Mark and comment (tag, sheet, provenance).

## 6. Verification
Area per tag vs plan (±1%); no floor–floor bounding-box overlaps; every beam top at slab top above or documented step; no unsupported edges except drawn cantilevers/voids; openings match voids.

## 7. Failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| API call hangs | Modal overlap warning in Revit | Non-overlapping rebuild order; dismiss dialog | [VERIFIED KPwBI] |
| Stubs past slab | Edge at beam face | Redraw from thick outline | [VERIFIED KPwBI] |
| Slabs invisible in plan | Template view filters ("Floors - Concrete NOT") | Remove filters from working views | [VERIFIED KPwBI] |
| Wrong thickness | Used plan table, detail differs | Ask; log | [VERIFIED KPwBI] |

## 8. Related
`beams.md`, `structural-walls.md`, `stairs.md`, `model-validation.md`.
