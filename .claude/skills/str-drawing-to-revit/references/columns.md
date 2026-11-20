# Columns — structural columns (OST_StructuralColumns)

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: none here. KPwBI items imported (Revit 2026); API items `[THEORY]` until run.
> Order of work: `workflows/element-modeling-workflow.md` (Stage A types → gate → Stage B placement → gate). This file supplies the column-specific details for each step.
> Support and connectivity rules (nothing floats): `building-logic.md` — read it before placing.

## 1. Scope
Concrete and steel columns: types (sizes, materials), stacks per storey, base/top levels, orientation, connection to foundations and beams. Not covered: column design, rebar (parked), slanted/tapered columns `[OPEN]`.

---

## A. Types

### A1. Where the column types are on the drawings
- **Column schedule** (`TABEL KOLOM`, `DAFTAR KOLOM`, `COLUMN SCHEDULE`): usually a grid of marks × levels, each cell with a cross-section sketch, size and rebar. Often on the same sheet as the column layout plan.
- Retrofit work: **jacketing / strengthening details** give the final size (types `JK…`) `[IMPORTED KPwBI]`.
- Steel columns: profile name on the plan or in a profile table (WF, H, HB, UC, box/pipe).
- No schedule → sizes from plan tags or sections; note that the source is not a schedule.
- Find it: `scripts/find_schedules.py <folder> --element columns`; confirm visually; ask the user if unclear.

### A2. What to extract per type
| Field | Notes |
|---|---|
| Mark | K1, K2, KC1, KB … |
| Level range | A mark can change size up the building (K1 = 600×600 to L2, 500×500 above): one catalog row per mark per level range |
| b × h (mm) | or diameter for round; or steel profile name with all dimensions (h, b, tw, tf) |
| Orientation | from the schedule sketch: which side is b, relative to which grid direction |
| Material | concrete grade (fc', K-) or steel grade (BJ 37, BJ 41) if given |
| Rebar | record only (main bars, ties); not modelled unless asked |
| Source | sheet, revision, page, provenance |

### A3. Catalog notes
- Final state: jacketed size where a JK type applies; existing size where none applies `[IMPORTED KPwBI]`.
- One Revit type per unique size + material (default; SKILL.md / workflow A3.4). Type Mark = drawing mark only if one mark ↔ one type.
- Check: every mark on the column plans is in the schedule; every schedule mark is used.

### A4–A5. Make the types in Revit
1. **Find a family:** inventory `OST_StructuralColumns` (`get_available_family_types`). Typical: a concrete rectangular column family with type parameters `b`, `h`; round concrete with diameter; steel H/WF/UC families with a type catalog. KPwBI steel columns were duplicated from the UC family `[IMPORTED KPwBI]`.
2. **Duplicate** for a missing size (`revit-families.md` §3), dimensions set in a separate call:
   ```csharp
   // [THEORY] call 1: duplicate
   var src = (FamilySymbol)document.GetElement(new ElementId(SRC_ID));
   var t = (FamilySymbol)src.Duplicate("KOLOM BETON 600x600");
   return t.Id.ToString();
   ```
   ```csharp
   // [THEORY] call 2: set dimensions + material + type mark (parameter names: check on the family first)
   var t = (FamilySymbol)document.GetElement(new ElementId(NEW_ID));
   t.LookupParameter("b").Set(600 / 304.8);
   t.LookupParameter("h").Set(600 / 304.8);
   var mat = t.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM);
   if (mat != null && !mat.IsReadOnly) mat.Set(new ElementId(MATERIAL_ID));
   t.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK).Set("K1");
   return "ok";
   ```
   The structural material may be an instance parameter on some families: then set it on each instance in Stage B.
3. **Steel from a type catalog:** load only the needed sizes, `document.LoadFamilySymbol(path, "WF300x150x6.5x9")` `[THEORY]`, or duplicate + set h, b, tw, tf, r `[IMPORTED KPwBI]`.
4. **No family:** build from `Metric Structural Column.rft` (workflow A5). Needs parameters b, h, structural material; save to the family folder; load.
5. Naming: project's style first (KPwBI: `KOLOM BAJA WF300x150x6.5x9`, `KOLOM BAJA HB300x300x10x15` `[IMPORTED KPwBI]`; concrete e.g. `KOLOM BETON bxh`).

### A6. Gate
Read back b, h (or profile dimensions) from each type in mm; material; every column mark on the plans resolves to a type.

---

## B. Placement

### B1. Where the positions and heights are
Column layout plan per level (marks at grid intersections; dimensioned offsets for off-grid columns); sections and elevations for base and top levels; foundation plan for the column base support.

### B2. Instance table columns
`mark | type | grid / position (x,y mm) | rotation | stack (S1, S2…) | base level + offset | top level + offset | base support (cap/footing/column below/beam) | source | provenance`

### B3. Interpretation rules
1. **Stacks per storey** (S1 base → L1 slab, S2, …), so each storey can carry its own type; no stack where the drawings show no column above `[IMPORTED KPwBI]`.
2. **Position:** grid intersection plus drawn offsets, exactly. Never snap an off-grid column to the grid.
3. **Base:** top of the cap/footing from the foundation section. If no foundation level is drawn: base = soffit of the deepest beam framing in at the lowest floor, `LOW CONFIDENCE`, and the cap top is set to the column base `[IMPORTED KPwBI]` (convention: confirm with the user).
4. **Top:** the top of the slab/beam at the top of the stack (column must reach the beam soffit at least: building-logic §4.3).
5. **Orientation:** from the schedule sketch. If undrawn, assume b along X and log it `[IMPORTED KPwBI]`.

### B4–B5. Revit procedure
```csharp
// [THEORY] one column; ids and values from the instance table
var sym = (FamilySymbol)document.GetElement(new ElementId(TYPE_ID));
if (!sym.IsActive) sym.Activate();
var lvlB = (Level)document.GetElement(new ElementId(BASE_LEVEL_ID));
var lvlT = (Level)document.GetElement(new ElementId(TOP_LEVEL_ID));
var p = new XYZ(X_MM / 304.8, Y_MM / 304.8, lvlB.Elevation);
var c = document.Create.NewFamilyInstance(p, sym, lvlB, Autodesk.Revit.DB.Structure.StructuralType.Column);
c.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).Set(lvlT.Id);
c.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM).Set(BASE_OFF_MM / 304.8);
c.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).Set(TOP_OFF_MM / 304.8);
c.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("K-A/1-S1");
c.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set("K1 | S-301 p12 | EXPLICIT");
return c.Id.ToString();
```
- Rotation: `ElementTransformUtils.RotateElement(document, c.Id, Line.CreateBound(p, p + XYZ.BasisZ), angleRad)` `[THEORY]`.
- Mark pattern `K-<grid>/<row>-S<n>` `[IMPORTED KPwBI]`; Comments: drawing mark, sheet/page, provenance, `LOW CONFIDENCE`.
- Place columns **before** the beams that frame into them.
- MCP alternative: `create_point_based_element` with the type id; check that it creates a *structural* column with the right base/top before using it for a batch `[OPEN]`.

### B6. Verification
- Count per mark × level vs the schedule/plan.
- Position (x, y) vs the instance table (≤ 1 mm for dimensioned positions; ≤ 16 mm noise for measured ones, investigate > 30 mm).
- Base and top elevations; each stack continuous base → top, no gaps or overlaps.
- Every column base on a foundation / column below / beam (connectivity check).
- Rotation vs the schedule sketch; type dims vs the catalog.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Columns floating above the foundation | Base level undefined | Base rule (B3.3), flag LOW CONFIDENCE | [IMPORTED KPwBI] |
| Wrong orientation | b/h assumed | Check the schedule sketch; ask | [IMPORTED KPwBI] |
| Extra posts beside columns | Misread an end-on section label | Trace leaders (drawing-interpretation §5) | [IMPORTED KPwBI] |
| Column too short for the beam | Top set to level, beam deeper / higher | Top = slab/beam top; height chain | [THEORY] |

## Related
`building-logic.md`, `foundations.md`, `beams.md`, `revit-families.md`, `model-validation.md`.
