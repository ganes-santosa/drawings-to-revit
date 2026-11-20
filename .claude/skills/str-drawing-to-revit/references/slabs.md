# Slabs — structural floors (OST_Floors)

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: none here. KPwBI items imported (Revit 2026); API items `[THEORY]` until run.
> Order of work: `workflows/element-modeling-workflow.md` (Stage A types → gate → Stage B placement → gate). This file supplies the slab-specific details for each step.
> Support and connectivity rules (nothing floats): `building-logic.md` — read it before placing.

## 1. Scope
Floor types (thickness, build-up, material), slab outlines, openings, levels and steps, splits at dilatation joints. Metal-deck slabs also set the steel level (`beams.md`). Not covered: rebar (parked), slab design.

---

## A. Types

### A1. Where the slab types are on the drawings
- **Slab schedule** (`TABEL PELAT`, `DAFTAR PELAT`, `SLAB SCHEDULE`): mark → thickness (+ rebar). Often a small table on the slab plan.
- **Slab details**: build-ups, metal-deck sections. The detail can disagree with the table (KPwBI: table 120, detail 150 metal deck; the user chose 150) `[IMPORTED KPwBI]`.
- Plan tags (S1, S2, SN1A …); tag text is often readable by `pdftotext -bbox` `[IMPORTED KPwBI]`.
- Find it: `scripts/find_schedules.py <folder> --element slabs`; confirm visually; ask if unclear.

### A2. What to extract per type
| Field | Notes |
|---|---|
| Mark | S1, S2, SN1A, PL1 … |
| Thickness (mm) | from schedule **and** detail; conflict → ask |
| Build-up | plain concrete, or metal deck (deck gauge, rib height, topping) |
| Material | concrete grade if given |
| Rebar | record only |
| Source | sheet, revision, page, provenance |

### A3. Catalog notes
- One floor type per thickness + build-up + material; the name lists the marks it serves (KPwBI: `PELAT BETON 120mm (S1/S2/S3/SN1A)`, `PELAT METAL DECK 150mm (SN1A/SN1B)`, each with a type mark) `[IMPORTED KPwBI]`.
- KPwBI metal deck: 0.75 mm deck, 50 mm ribs + 100 mm topping = 150 `[IMPORTED KPwBI]`.

### A4–A5. Make the types in Revit
Floors are a **system family**: no loadable family; duplicate an existing floor type and edit its compound structure.
```csharp
// [THEORY] call 1: duplicate a floor type
var src = (FloorType)document.GetElement(new ElementId(SRC_FLOOR_TYPE_ID));
var ft = (FloorType)src.Duplicate("PELAT BETON 120mm (S1/S2)");
return ft.Id.ToString();
```
```csharp
// [THEORY] call 2: single structural layer of the right thickness and material
var ft = (FloorType)document.GetElement(new ElementId(NEW_ID));
var cs = CompoundStructure.CreateSingleLayerCompoundStructure(MaterialFunctionAssignment.Structure, 120 / 304.8, new ElementId(MATERIAL_ID));
ft.SetCompoundStructure(cs);
ft.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK).Set("S1");
return "ok";
```
- Metal deck: a `StructuralDeck` layer with a deck profile (`CompoundStructure` deck settings) `[THEORY, OPEN]`; if unreliable, model the full thickness as concrete and note it.
- Floor type must be **structural** (`FLOOR_PARAM_IS_STRUCTURAL` on the instance) `[THEORY]`.

### A6. Gate
Read back total thickness (`ft.GetCompoundStructure().GetWidth()` × 304.8) and the material per type; every slab mark on the plans resolves to a type.

---

## B. Placement

### B1. Where the outlines and levels are
Slab plan per level: thick outline, tags, X-marked voids, stair/shaft openings, slope arrows, dilatation joints (double thin line). Sections and level notes for SFL per zone.

### B2. Instance table columns
`mark | type | level | top elevation (SFL) | outline polygon (mm) | openings | slope | supports (beams/walls along edges, or columns) | cantilever edges | source | provenance`

### B3. Interpretation rules
1. **Outline = the drawn thick line,** not beam faces or grid guesses (KPwBI: grid guess 1825/24575 vs drawn 1944/24458 with jogs; beam-face edges left stubs) `[IMPORTED KPwBI]`.
2. **Openings:** X-marked voids, stair and shaft outlines.
3. **Split at dilatation joints;** each side is its own slab.
4. **Top = SFL** of that zone; level offset = SFL − level elevation.
5. **Supports:** every edge sits on a beam or wall, or is a drawn cantilever / void edge / joint face (building-logic §2). Model the beams first.

### B4–B5. Revit procedure
```csharp
// [THEORY] one slab with one opening; points in mm
Func<double[], CurveLoop> loop = (pts) => {
    var cl = new CurveLoop();
    for (int i = 0; i < pts.Length; i += 2) {
        int j = (i + 2) % pts.Length;
        cl.Append(Line.CreateBound(new XYZ(pts[i]/304.8, pts[i+1]/304.8, 0), new XYZ(pts[j]/304.8, pts[j+1]/304.8, 0)));
    }
    return cl;
};
var outer = loop(new double[] { 0,0, 12000,0, 12000,8000, 0,8000 });
var hole  = loop(new double[] { 4000,3000, 4000,5000, 6000,5000, 6000,3000 }); // opposite direction
var loops = new List<CurveLoop> { outer, hole };
var f = Floor.Create(document, loops, new ElementId(FLOOR_TYPE_ID), new ElementId(LEVEL_ID));
f.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(OFFSET_MM / 304.8);
f.get_Parameter(BuiltInParameter.FLOOR_PARAM_IS_STRUCTURAL).Set(1);
f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("PL2-001");
f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set("S1 | S-501 p18 | EXPLICIT");
return f.Id.ToString();
```
- `double[]` arrays and `Func<>` instead of `int[]` and local functions (host compiler quirks) `[IMPORTED KPwBI]`.
- **Overlapping floors:** rebuilding a floor that overlaps a neighbour raises a modal "Highlighted floors overlap" warning that blocks the API and looks like a timeout. Build in an order that never overlaps, a few floors per call `[IMPORTED KPwBI]`.
- MCP alternative: `create_surface_based_element` (`OST_Floors`, outer loop only). It cannot make openings `[LIMITATION]`: use the script for slabs with voids.

### B6. Verification
- Area per mark vs the plan (±1%); outline vertices vs the instance table.
- Top elevation = SFL per zone; every beam top at the slab top above or a documented step.
- No floor–floor bounding-box overlaps; openings match the voids.
- Edges supported (beams/walls) except drawn cantilevers, voids, joint faces.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| API call hangs | Modal overlap warning in Revit | Non-overlapping order; dismiss the dialog | [IMPORTED KPwBI] |
| Slab stubs past the edge | Edge at beam face / grid | Redraw from the thick outline | [IMPORTED KPwBI] |
| Slabs invisible in plan | Template view filters ("Floors - Concrete NOT") | Remove the filters from working views | [IMPORTED KPwBI] |
| Wrong thickness | Plan table vs detail differ | Ask; log | [IMPORTED KPwBI] |

## Related
`building-logic.md`, `beams.md`, `views-and-documentation.md`, `model-validation.md`.
