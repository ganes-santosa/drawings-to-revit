# Beams — concrete and steel beams (Structural Framing, OST_StructuralFraming)

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: 2026 (KPwBI, imported); nothing re-tested in this setup
> Steel truss/brace/roof systems: `structural-framing.md`.

## 1. Purpose and scope
Identify, size, position, place and validate beams. Joins at columns; steps between slab zones.

## 2. Drawing conventions
Beam layout plans per level: beams as paired lines (faces) often dashed; tag = mark/size (e.g. `B1 300x600`) or only a mark with schedule; offsets from grids dimensioned; "TYP." notes; step/drop zones shown by level notes; secondary beams frame into girders. Beam schedule gives b×h, reinforcement, level. Sections show soffit/top relative to SFL. Check each sheet's existing/new status.

## 3. Required inputs
Mark → section size; plan centreline (from faces pair) and end points; top elevation (normally slab top/SFL) per zone; steel profile (name) and orientation; step locations; confirmation that nothing crosses expansion joints.

## 4. Interpretation method
1. Centreline = midpoint of face pair; width check against schedule `b`. Ends: at column face/centre as drawn, or at girder face.
2. Elevation: top = SFL of supported slab unless drawn otherwise. Under a **metal-deck slab**, steel top = SFL − slab thickness `[IMPORTED KPwBI]`.
3. Steps ≤ 400 mm → boundary beam takes higher SFL; large steps (1.7–2.1 m) → boundary beam at lower level + step walls `[IMPORTED KPwBI]` (confirm with user — it is a modelling convention, not drawn).
4. Eccentric beams modelled as drawn (KPwBI: treasury perimeter beams 120 mm inside column centres; roof G25 100 mm inside rows 1 and 3; secondaries at 1A − 1200 and 2A + 600, not on grids 1A/2A) `[IMPORTED KPwBI]`. Nothing crosses expansion joints.
5. Label provenance of each value (SKILL.md §3.3).

## 5. Revit procedure
1. Category Structural Framing. KPwBI names `[IMPORTED KPwBI]`: concrete family **`BALOK BETON PERSEGI`** (type parameters `b`, `h`), types `BALOK BETON bxhmm`; steel types named by profile (`WF350x175x7x11`), drawing tag codes BS1..BS6. Use the project's own names when its template differs. Check existence first (`revit-families.md`); duplicate type only if exact size missing, flag if substituting.
2. Create: `document.Create.NewFamilyInstance(Curve, FamilySymbol, Level, StructuralType.Beam)` `[THEORY]` (standard API); activate symbol first (`symbol.Activate()`).
3. **Set Z justification Top and apply vertical offset so top = SFL** via the end-offset parameters (`Z_OFFSET_VALUE`/start-end level offsets) `[IMPORTED KPwBI]`.
4. **Set Y_JUSTIFICATION = 1 (Center)** on every beam `[IMPORTED KPwBI]` — see failures.
5. **Joins:** `StructuralFramingUtils.DisallowJoinAtEnd(familyInstance, 0|1)` at every end **not** inside a column footprint; keep column joins `[IMPORTED KPwBI]`.
6. **Merge collinear same-type beams** meeting at a column into one continuous member (602 → 492 in KPwBI); keep secondaries split where they frame into girders `[IMPORTED KPwBI]`.
7. Sloped members (knee braces): place as `StructuralType.Beam` with sloped ends — the Brace type snapped its top to the beam centreline `[IMPORTED KPwBI]`.
8. Marks and comments (Section 3 rules). KPwBI mark patterns: concrete `BLn-W/E/T-nnn`, `BLA-*`, `BLD-*`; steel `BSL1/BSL2/BSM/BSA-nnn`. Comments: type tag, sheet, `LOW CONFIDENCE` where it applies. `ALL_MODEL_MARK`, `ALL_MODEL_INSTANCE_COMMENTS` `[IMPORTED KPwBI]`.

## 6. API / automation
### Imported `[IMPORTED KPwBI, Revit 2026, mcp-server-for-revit]`
- Parameters: `BuiltInParameter.ALL_MODEL_MARK`, `ALL_MODEL_INSTANCE_COMMENTS`; `Y_JUSTIFICATION` instance parameter (value 1 = Center).
- `StructuralFramingUtils.DisallowJoinAtEnd`.
- `ElementTransformUtils.MoveElement` for bulk moves (44 beams 950 mm down); append reason to Comments.
- Keep scripts ≈4k characters; split into several calls (see `revit-api-and-automation.md`).
### Untested
- Verbatim placement script: not preserved from KPwBI. Re-derive, test on one beam, and record here under *Verified*.

## 7. Verification
- Count by mark/type vs beam schedule.
- Each beam: `LocationCurve` endpoints vs calibrated drawing centreline (≤16 mm = line-weight noise; investigate >30 mm) `[IMPORTED KPwBI]`.
- Solid-vs-location check: bounding-box centre of one test beam vs its LocationCurve (detects Y-justification error).
- Top elevation = SFL of the slab above (or documented step/step wall).
- No duplicates (same type, collinear, overlapping); no beam crossing a joint; free ends listed (each must be a drawn cantilever, joint face or void edge).
- Warnings: `document.GetWarnings()` grouped by description.

## 8. Failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Beams offset sideways by (b−200)/2 (300 mm for 800 wide) | Default Y justification; family flexes one face only | Set Y_JUSTIFICATION = 1 on all beams; test one beam's solid vs location first | [IMPORTED KPwBI] |
| Beams notched/trimmed strangely | Auto-join to unrelated members | DisallowJoinAtEnd at non-column ends | [IMPORTED KPwBI] |
| Hundreds of fragments, hard to audit | One beam per bay | Merge collinear at columns | [IMPORTED KPwBI] |
| Beams crossing expansion joint | Modelled grid-to-grid | Stop at joint; add joint beams | [IMPORTED KPwBI] |
| Secondary beams on wrong lines | Assumed nearest grid | Use drawn offsets (e.g. 1A−1200) | [IMPORTED KPwBI] |
| Knee brace top snapped | Brace structural type | Use Beam type | [IMPORTED KPwBI] |
| Eave beams 950 mm high | Misread end-on section label | Trace leaders (drawing-interpretation §5) | [IMPORTED KPwBI] |
| Beam exists but not at drawn size | Nearest-size type substituted silently | Flag LOW CONFIDENCE or create exact type | [IMPORTED KPwBI] |

## 9. Related
`columns.md`, `slabs.md`, `structural-framing.md`, `connections.md`, `revit-families.md`, `model-validation.md`.
