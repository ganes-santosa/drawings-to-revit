# Beams — concrete and steel beams (Structural Framing, OST_StructuralFraming)

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: none here. KPwBI items imported (Revit 2026); API items `[THEORY]` until run.
> Order of work: `workflows/element-modeling-workflow.md` (Stage A types → gate → Stage B placement → gate). This file supplies the beam-specific details for each step.
> Support and connectivity rules (nothing floats): `building-logic.md` — read it before placing. Roof steel, trusses, purlins: `structural-framing.md`.

## 1. Scope
Floor and roof beams, concrete and steel: types, plan lines, end points, elevations, justification, joins. Not covered: beam design, rebar (parked).

---

## A. Types

### A1. Where the beam types are on the drawings
- **Beam schedule** (`TABEL BALOK`, `DAFTAR BALOK`, `BEAM SCHEDULE`, `DETAIL PENULANGAN BALOK`): rows per mark with b × h and rebar at support/midspan, often with cross-section sketches. May be split per level.
- **Plan tags** that carry the size directly: `B1 300x600`, `G1 (400x800)`.
- **Steel:** profile name in the tag or a **profile-letter table** on the framing plan (A = WF250x175 …) `[IMPORTED KPwBI]`; codes like BS1..BS6.
- Strengthening sheets (retrofit) may change the final size.
- Find it: `scripts/find_schedules.py <folder> --element beams`; confirm visually; ask the user if unclear.

### A2. What to extract per type
| Field | Notes |
|---|---|
| Mark | B1, B2, G1, BA, BL, sloof/tie beam (TB, S) … |
| Level range | The same mark can differ per level: one catalog row per mark per level |
| b × h (mm) | concrete; or steel profile with h, b, tw, tf (r if given) |
| Material | concrete grade / steel grade if given |
| Rebar | record only |
| Source | sheet, revision, page, provenance |

### A3. Catalog notes
- Cross-check the schedule against sections (a section showing a different depth = conflict, ask).
- Every mark on the beam plans is in the schedule; every schedule mark is used.
- One Revit type per unique size + material (default).

### A4–A5. Make the types in Revit
1. **Find a family:** inventory `OST_StructuralFraming`. Typical: concrete rectangular beam family with type parameters `b`, `h`; steel WF/H/I families with a type catalog. KPwBI: concrete family **`BALOK BETON PERSEGI`** (`b`, `h`), types `BALOK BETON bxhmm`; steel types named by profile `WF350x175x7x11` `[IMPORTED KPwBI]`.
2. **Duplicate** for a missing size, dimensions in a separate call (same pattern as `columns.md` A4–A5: `Duplicate`, then `LookupParameter("b"/"h").Set(mm/304.8)`, material via `STRUCTURAL_MATERIAL_PARAM`, Type Mark) `[THEORY]`.
3. **Steel from a type catalog:** `document.LoadFamilySymbol(path, "WF350x175x7x11")` `[THEORY]`, or duplicate + set h, b, tw, tf, r `[IMPORTED KPwBI]`.
4. **No family:** build from `Metric Structural Framing - Beams and Braces.rft` (workflow A5). For angles/channels with no family, KPwBI used DirectShape extrusions (`structural-framing.md`) `[IMPORTED KPwBI]`.
5. **Know the family's quirk before placing:** the KPwBI concrete family flexed only one face with `b`, so instances must use Y justification Center (B5) `[IMPORTED KPwBI]`. Test one instance's solid against its location line for every new family.

### A6. Gate
Read back b, h / profile dimensions in mm; material; every beam mark on the plans resolves to a type.

---

## B. Placement

### B1. Where the positions and heights are
Beam layout plan per level (beam faces as paired, often dashed lines; tags; offsets from grids); sections for top/soffit relative to the slab; slab plan for SFL zones and steps; joint locations.

### B2. Instance table columns
`mark | type | level | start (x,y) | end (x,y) | start support | end support | top elevation (SFL zone) | Y offset/eccentricity | CANTILEVER? | source | provenance`

### B3. Interpretation rules
1. **Line:** centreline = midpoint of the face pair; check its width against `b`. Eccentric beams stay eccentric (KPwBI: perimeter beams 120 mm inside column centres; roof G25 100 mm inside rows 1 and 3; secondaries at 1A − 1200 and 2A + 600) `[IMPORTED KPwBI]`.
2. **Ends: resolved to the support,** along the beam's own axis: column centre, girder centreline, wall line. Not where the drawn line stops (drafted lines stop at faces or leave gaps). Drawn cantilevers end where dimensioned and get `CANTILEVER` in Comments (`building-logic.md` §4).
3. **Elevation:** top = SFL of the slab it supports, unless drawn otherwise. Steel under a metal-deck slab: top = SFL − slab thickness `[IMPORTED KPwBI]`.
4. **Steps:** ≤ 400 mm → boundary beam takes the higher SFL; large steps (1.7–2.1 m) → boundary beam at the lower level + step walls `[IMPORTED KPwBI]` (a convention: confirm with the user).
5. **Joints:** nothing crosses a dilatation joint; beams stop at it `[IMPORTED KPwBI]`.
6. **Continuity:** a run of the same type through several columns is one member (KPwBI merged 602 → 492); secondaries stay split where they frame into girders `[IMPORTED KPwBI]`.

### B4–B5. Revit procedure
```csharp
// [THEORY] one beam; points in mm from the instance table, top elevation handled by justification + offsets
var sym = (FamilySymbol)document.GetElement(new ElementId(TYPE_ID));
if (!sym.IsActive) sym.Activate();
var lvl = (Level)document.GetElement(new ElementId(LEVEL_ID));
double z = lvl.Elevation;
var crv = Line.CreateBound(new XYZ(X0/304.8, Y0/304.8, z), new XYZ(X1/304.8, Y1/304.8, z));
var b = document.Create.NewFamilyInstance(crv, sym, lvl, Autodesk.Revit.DB.Structure.StructuralType.Beam);
b.get_Parameter(BuiltInParameter.Y_JUSTIFICATION).Set(1);                 // Center  [IMPORTED KPwBI]
b.get_Parameter(BuiltInParameter.Z_JUSTIFICATION).Set(0);                 // Top: check the enum value on the live model
b.get_Parameter(BuiltInParameter.STRUCTURAL_BEAM_END0_ELEVATION).Set(OFF_MM/304.8); // start level offset
b.get_Parameter(BuiltInParameter.STRUCTURAL_BEAM_END1_ELEVATION).Set(OFF_MM/304.8); // end level offset
b.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("BL2-W-001");
b.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set("B1 | S-401 p15 | EXPLICIT");
return b.Id.ToString();
```
- **Z justification Top, top = SFL** through the start/end offsets `[IMPORTED KPwBI]`.
- **Y justification = 1 (Center)** on every beam `[IMPORTED KPwBI]`.
- **Joins:** keep joins at column ends; `StructuralFramingUtils.DisallowJoinAtEnd(b, 0|1)` at ends not inside a column footprint to avoid odd notching `[IMPORTED KPwBI]`. The end point still sits on the girder centreline (building-logic §4).
- Sloped members (knee braces): `StructuralType.Beam` with sloped ends, not Brace (Brace snapped its top to the beam centreline) `[IMPORTED KPwBI]`.
- Marks `[IMPORTED KPwBI]`: concrete `BLn-W/E/T-nnn`, `BLA-*`, `BLD-*`; steel `BSL1/BSL2/BSM/BSA-nnn`. Comments: drawing mark, sheet/page, provenance, `LOW CONFIDENCE`, `CANTILEVER`.
- Order: columns first, then primary beams, then secondaries.
- MCP alternative: `create_line_based_element` (category `OST_StructuralFraming`, type id, p0/p1 in mm). It sets no justification, offsets, joins or marks: follow up with a script, or use the script above `[THEORY]`.
- Bulk corrections: `ElementTransformUtils.MoveElement`; append the reason to Comments `[IMPORTED KPwBI]`.

### B6. Verification
- Connectivity check: 0 unexplained floating ends.
- Count per mark/type vs the schedule/plan.
- `LocationCurve` end points vs the instance table / calibrated centreline (≤ 16 mm line-weight noise; investigate > 30 mm) `[IMPORTED KPwBI]`.
- Solid vs location: bounding-box centre of a test beam vs its location line, < 1 mm sideways (catches the justification problem).
- Top elevation = SFL of the slab above, or a documented step / step wall.
- No duplicates (same type, collinear, overlapping); nothing crosses a joint; warnings grouped.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Beams offset sideways by (b−200)/2 (300 mm for 800 wide) | Default Y justification; family flexes one face only | Y_JUSTIFICATION = 1 on all beams; test one beam's solid first | [IMPORTED KPwBI] |
| Beams don't touch columns / each other | Ends taken from where the drawn line stops; support not modelled yet | Ends resolved to supports; supports first; connectivity check | [THEORY] (user-reported) |
| Beams notched/trimmed strangely | Auto-join to unrelated members | DisallowJoinAtEnd at non-column ends | [IMPORTED KPwBI] |
| Hundreds of fragments | One beam per bay | Merge collinear at columns | [IMPORTED KPwBI] |
| Beams crossing a dilatation joint | Modelled grid-to-grid | Stop at the joint; add joint beams | [IMPORTED KPwBI] |
| Secondary beams on the wrong lines | Assumed nearest grid | Drawn offsets (1A − 1200) | [IMPORTED KPwBI] |
| Knee-brace top snapped | Brace structural type | Beam type | [IMPORTED KPwBI] |
| Eave beams 950 mm high | Misread end-on section label | Trace leaders | [IMPORTED KPwBI] |
| Beam not at drawn size | Nearest size substituted silently | Exact type (A5) or LOW CONFIDENCE + user OK | [IMPORTED KPwBI] |

## Related
`building-logic.md`, `columns.md`, `slabs.md`, `structural-framing.md`, `revit-families.md`, `model-validation.md`.
