# Beams — concrete and steel beams (Structural Framing, OST_StructuralFraming)

> Legend: SKILL.md §8 · Last reviewed: 2026-11-23 · Revit tested: RSUD Cakung field report (Revit 2026, `mcp-server-for-revit`, ~2,330 → 904 beams on 4 floors; `assets/field-reports/2026-11-23-rsud-cakung-beam-cleanliness.md`) for placement, clean-up and audit; KPwBI items imported; the rest `[THEORY]`.
> Order of work: `workflows/element-modeling-workflow.md` (Stage A types → gate → Stage B: instance table → **clean the table** → place once → **audit and repair** → gate). This file supplies the beam-specific details for each step.
> Support and connectivity rules (nothing floats): `building-logic.md` — read it before placing. Roof steel, trusses, purlins: `structural-framing.md`.

## 1. Scope
Floor and roof beams, concrete and steel: types, plan lines, end points, elevations, justification, joins, continuity, clean-up and audit. Not covered: beam design, rebar.

**The big lesson (RSUD):** placing beams exactly where the drawn lines start and stop gives a model that looks right in plan but is wrong as a structure: ends hanging in the air, edge beams missing, cantilever tips untied, notched corners, girders chopped into pieces, perimeter beams sticking out past columns. The user found every one by orbiting a 3D view. The cure: **clean the planning table before placing** (B2b), so beams go into Revit connected, merged and flush the first time; then an **audit-and-repair pass** in the model (B5b, B6) for what only shows once things are in Revit. The rules come from RSUD, where they ran as a clean-up after placing `[VERIFIED RSUD]`; running them on the table first is the chosen design (user decision 2026-11-23) `[THEORY]` until tested on a floor.

---

## A. Types

### A1. Where the beam types are on the drawings
- **Beam schedule** (`TABEL BALOK`, `DAFTAR BALOK`, `BEAM SCHEDULE`, `DETAIL PENULANGAN BALOK`, `TABULASI PENULANGAN BALOK`): rows per mark with b × h and rebar at support/midspan, often with cross-section sketches. May be split per level.
- **Plan tags** that carry the size directly: `B1 300x600`, `G1 (400x800)`.
- **Steel:** profile name in the tag or a **profile-letter table** on the framing plan (A = WF250x175 …) `[IMPORTED KPwBI]`; codes like BS1..BS6.
- Strengthening sheets (retrofit) may change the final size.
- Find it: `scripts/find_schedules.py <folder> --element beams`; confirm visually; ask the user if unclear.

### A2. What to extract per type
| Field | Notes |
|---|---|
| Mark | B1, B2, G1, BA, BL, sloof/tie beam (TB, S), edge beams (L1, L2), cantilevers (OV, Sov "overstek") … |
| Level range | The same mark can differ per level: one catalog row per mark per level |
| b × h (mm) | concrete; or steel profile with h, b, tw, tf (r if given) |
| Material | concrete grade / steel grade if given |
| Rebar | record only |
| Source | sheet, revision, page, provenance |

### A3. Catalog notes
- Cross-check the schedule against sections (a section showing a different depth = conflict, ask).
- Every mark on the beam plans is in the schedule; every schedule mark is used. Edge-beam marks (L1/L2) often appear only on plans: catalog them too.
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
Beam layout plan per level (beam faces as paired, often dashed lines; tags; offsets from grids); sections for top/soffit relative to the slab; slab plan for SFL zones and steps; joint locations. **Calibrate each sheet on its own grid** (sheets can be shifted against each other: `grids-and-levels.md` §5).

### B2. Instance table columns
`mark | type | level | start (x,y) | end (x,y) | start support | end support | top elevation (SFL zone) | Y offset/eccentricity | flush-with-column? | CANTILEVER? | source | provenance`
Then clean it (B2b) before anything is placed.

### B2a. Interpretation rules (how to fill the table)
1. **Line:** centreline = midpoint of the face pair; check its width against `b`. Eccentric beams stay eccentric when drawn off-grid by a dimension (KPwBI: perimeter beams 120 mm inside column centres; roof G25 100 mm inside rows 1 and 3; secondaries at 1A − 1200 and 2A + 600) `[IMPORTED KPwBI]`.
2. **Flush intent:** a façade/edge beam drawn with its outer face on the columns' outer face keeps that *relationship* (flush), even when the column position comes from the schedule and differs from the plan outline. Rules: `drawing-interpretation.md` §5 "Flush intent" `[VERIFIED RSUD]` (concept).
3. **Edge beams drawn differently:** one-sided edge beams (a single dashed face line beside the slab outline) and outline-only edge beams (L1/L2) are beams too. Model them and tag `LOW CONFIDENCE`; never list them as "not modelled" (`drawing-interpretation.md` §5) `[VERIFIED RSUD]`.
4. **Ends: resolved to the support,** along the beam's own axis: column centre, girder centreline, wall line. Not where the drawn line stops. Drawn cantilevers end where dimensioned and get `CANTILEVER` in Comments (`building-logic.md` §4).
5. **Elevation:** top = SFL of the slab it supports, unless drawn otherwise. Steel under a metal-deck slab: top = SFL − slab thickness `[IMPORTED KPwBI]`.
6. **Steps:** ≤ 400 mm → boundary beam takes the higher SFL; large steps (1.7–2.1 m) → boundary beam at the lower level + step walls `[IMPORTED KPwBI]` (a convention: confirm with the user).
7. **Joints:** nothing crosses a dilatation joint; beams stop at it `[IMPORTED KPwBI]`.
8. **Segmentation follows the project decision** (asked once at setup, `project-setup.md` §3 step 5b; read it from the project log; if missing, ask before placing):
   - **A. Continuous:** one instance per continuous run of the same type, secondaries included. On RSUD the user chose this ("split pieces provide no benefit") `[VERIFIED RSUD]`.
   - **B. Split at supports:** one instance per span. Primary beams break at every column (both ends inside the column footprint); secondaries break at the girder or column they frame into (ends on the girder centreline). Default when 4D/phasing is likely or unknown `[THEORY]` (not yet run).
   - **C. Continuous within zones:** as A inside each zone, split where a run crosses a zone line the team supplied `[THEORY]`.
   - Every mode: split at dilatation joints and where the type changes (an OV2 cantilever continuing a B3).

### B2b. Clean the planning table before placing
Do the geometry on the table (plain data), not on beams already in Revit. Placing clean data once avoids the modal dialogs ("identical instances", "Can't keep elements joined"), the chain reactions (a moved girder stranding the beams that frame into it) and the wasted work (RSUD placed ~2,330 beams and merged them down to 904).

**Status:** every rule below ran on RSUD as a clean-up *after* placing `[VERIFIED RSUD]`, thresholds `[EXPERIMENTAL RSUD]`. Running them on the table *before* placing is `[THEORY]`: test on one floor first and compare the audit numbers (B6) with RSUD's.

**Inputs:** the instance table (B2); the columns **as modelled** (place columns first and read back their positions and bounding boxes, because the column schedule wins over the plan outline); dilatation joints; cantilever marks (OV / Sov / drawn cantilevers). Run the maths in Python on the extracted table, or as array maths inside one `send_code_to_revit` call that reads the columns: either way, record which in the project log.

**Steps, in this fixed order** (each step can break the one before; this order avoids it):
1. **De-duplicate:** same type + collinear + overlapping rows → one row. Duplicates would raise "identical instances in the same place" `[VERIFIED RSUD]`.
2. **Add missing edge and tie beams:** one-sided and outline-only edge beams (`drawing-interpretation.md` §5), and tie beams across rows of cantilever tips where the slab edge runs across them. Tag `LOW CONFIDENCE` (a general tie-beam rule is `[THEORY]`: model and flag, or ask).
3. **Resolve every end to a support** (`building-logic.md` §6): look forward along the beam axis for the nearest column (the line passes through its footprint) or roughly perpendicular crossing beam (|cos| ≤ 0.5, crossing point *within* that beam's length); cap 4 m; if moved > 1.5 m, note `LOW CONFIDENCE: end extended N mm to nearest support (connectivity rule)`. An end that will not resolve usually means a missing support: go back to step 2.
4. **Flush intent:** façade/edge beams drawn flush with the columns' outer face get their outer face on the **modelled** column face (`drawing-interpretation.md` §5). Perimeter only; move 8–320 mm only; group the collinear run and use the outermost face; note `flush with outer column face (N mm)`. Then repeat step 3 for beams that framed into a moved beam.
5. **Apply the segmentation mode** (B2a.8). First merge collinear pieces into runs, always: same type, same level and top height (±10 mm), both ends within 10 mm of the same line, touching or overlapping (gap ≤ 50 mm). This also removes accidental fragments from detection `[VERIFIED RSUD]`. Then:
   - **A:** keep the runs. Keep the lowest Mark, note `merged continuous from 001,002,...`, inherit `LOW CONFIDENCE`.
   - **B:** cut each run at every support along it: at column centres (cut point = the beam line's nearest point to the column centre; both new ends sit inside the column) and, for secondaries, at the centrelines of girders they frame into. Pieces inherit type, offsets, `LOW CONFIDENCE` and the source comment; Marks get a span suffix (`-S1`, `-S2` …) `[THEORY]`.
   - **C:** keep the runs, then cut where a run crosses a zone line. Note the zone in each piece's Comments (e.g. `ZONE Z2`) `[THEORY]`.
   - Never merge across a dilatation joint. Different types on one line stay separate.
   Cutting *after* merging gives clean, predictable span pieces (no leftover fragments from where drawn lines happened to stop).
6. **Set the joints:**

   | Joint | How to recognise it | Where the end goes |
   |---|---|---|
   | **T** (frames into the side of another beam) | end near the other beam's centreline, away from that beam's ends | exactly on the other beam's **centreline** |
   | **L-corner** (two beams end at each other) | crossing point within ~half a width + 100 mm of the other beam's end, and **no collinear continuation** past it | **both** beams extend past the crossing point by the **other** beam's half-width, filling the corner square |
   | **Collinear, different types** (B4 continuing as B8) | same line, ends overlap or gap | both ends meet at one common point (midpoint of the overlap) |
   | **In a column** | end inside the column footprint | leave it; Revit join allowed |

7. **Check the table (planning gate):** run the connected-end test, an overlap scan and a duplicate-mark check on the table itself. Target: 0 non-cantilever free ends (or a listed few for the user), 0 overlaps > 50 mm (an overlap of exactly 2 × half-width betrays a crossing mistaken for a corner: trim to the common point), 0 duplicate marks. Only then place.

### B3. Cross-check before placing
Counts per mark vs the schedule/plan, every row has a verified type (Stage A), heights follow the height chain (workflow B3), and the table gate (B2b step 7) passed.

### B4–B5. Revit procedure
```csharp
// one beam; points in mm from the instance table
var sym = (FamilySymbol)document.GetElement(new ElementId(TYPE_ID));
if (!sym.IsActive) sym.Activate();
var lvl = (Level)document.GetElement(new ElementId(LEVEL_ID));
double z = lvl.Elevation;
var crv = Line.CreateBound(new XYZ(X0/304.8, Y0/304.8, z), new XYZ(X1/304.8, Y1/304.8, z));
var b = document.Create.NewFamilyInstance(crv, sym, lvl, Autodesk.Revit.DB.Structure.StructuralType.Beam);
b.get_Parameter(BuiltInParameter.Y_JUSTIFICATION).Set(1);                           // Center
b.get_Parameter(BuiltInParameter.Z_JUSTIFICATION).Set(0);                           // Top
b.get_Parameter(BuiltInParameter.STRUCTURAL_BEAM_END0_ELEVATION).Set(OFF_MM/304.8); // start level offset
b.get_Parameter(BuiltInParameter.STRUCTURAL_BEAM_END1_ELEVATION).Set(OFF_MM/304.8); // end level offset
b.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("BL2-W-001");
b.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set("B1 | S-401 p15 | EXPLICIT");
return b.Id.ToString();
```
- The creation call, `Y_JUSTIFICATION = 1` (Center), `Z_JUSTIFICATION = 0` (Top) and top height via `STRUCTURAL_BEAM_END0/1_ELEVATION`: run on ~2,300 beams `[VERIFIED RSUD]` (confirms KPwBI).
- **Move or trim** a beam: `((LocationCurve)el.Location).Curve = Line.CreateBound(a, b)` `[VERIFIED RSUD]`. **Warning: setting the curve resets `STRUCTURAL_BEAM_END0/1_ELEVATION` to 0** `[VERIFIED RSUD]` (10 beams dropped 50 mm on RSUD). Read both end offsets *before* the edit and write them back after it.
- **Curved beams:** `document.Create.NewFamilyInstance(arc, symbol, level, StructuralType.Beam)` with an `Arc` works for a concrete rectangular family `[VERIFIED RSUD]` (3 curved S1 300x600 edge beams). Centreline radius = slab outline radius ± half the beam width (− for a convex corner, + for a concave one). Straight beams running past the arc are trimmed at the arc beam's centreline circle.
- **"Beam or Brace is slightly off axis"** comes from 2–7 mm endpoint drift: snap the endpoints orthogonal (average the shared coordinate), then restore the end offsets (4 warnings → 0) `[VERIFIED RSUD]`.
- **Joins:** `StructuralFramingUtils.DisallowJoinAtEnd(b, k)` at ends **not** inside a column; `AllowJoinAtEnd(b, k)` at ends inside a column `[VERIFIED RSUD]`. Disallowing at *every* end is a mistake (RSUD had to re-allow 1,573 column ends). Disallow the join **before** changing the curve, or Revit may raise "Can't keep elements joined" `[EXPERIMENTAL RSUD]`.
- Sloped members (knee braces): `StructuralType.Beam` with sloped ends, not Brace `[IMPORTED KPwBI]`.
- Marks `[IMPORTED KPwBI]`: concrete `BLn-W/E/T-nnn`, `BLA-*`, `BLD-*`; steel `BSL1/BSL2/BSM/BSA-nnn` (RSUD used `ST-BM-L01-nnn`). Comments: drawing mark, sheet/page, provenance, `LOW CONFIDENCE`, `CANTILEVER`, and every clean-up action appended.
- Order: columns first, then primary beams, then secondaries.
- **Speed:** copy all end points into plain arrays, do the maths there, then write only the changed beams. Nested loops of Revit API calls (e.g. `Line.Project`) time out; the array method handles 700 × 700 beams, and four floors, in one call under a second `[VERIFIED RSUD]`.
- MCP alternative: `create_line_based_element` sets no justification, offsets, joins or marks: use the script above.

### B5b. Audit and repair after placing (what only shows in the model)
Some problems only appear once beams are in Revit: a support the table never had, real column sizes differing from the plan, Revit's own join behaviour, things the user spots in 3D. So after each floor is placed:

1. **Audit** (B6): `scripts/revit/check_connectivity.cs` for free ends and column bases, plus overlaps, duplicate marks, beams through a column interior, long spans, LOW CONFIDENCE count.
2. **Joins:** `AllowJoinAtEnd` at ends inside a column, `DisallowJoinAtEnd` elsewhere; disallow **before** changing any curve, or Revit may raise "Can't keep elements joined" `[VERIFIED RSUD]` / `[EXPERIMENTAL RSUD]`.
3. **Repair only the beams the audit lists**, with the same rules as B2b steps 3–6 (and write the end offsets back after every curve edit), editing in place: `((LocationCurve)el.Location).Curve = Line.CreateBound(a, b)` `[VERIFIED RSUD]`. Copy end points into arrays, do the maths, write only the changed beams.
4. **After every geometry change, re-scan** free ends with a ±400 mm search, forward **or** backward (a moved girder left 11 beams 274 mm short on RSUD), then an overlap scan, trimming overlaps to the common point `[VERIFIED RSUD]`.
5. If a modal dialog appears, the call looks like a timeout: the user dismisses it (Unjoin / OK, never Delete); count what committed before retrying (`revit-api-and-automation.md` §4).
6. **Re-audit.** The floor is done at zero, or at a short list the user accepts. Show the user the numbers and the list.

If the repair pass finds many problems, the table cleaning (B2b) missed something systematic: fix the rule or the detection there and record the lesson, rather than repairing beam by beam.

### B6. Verification — the audit (what "done" means for a floor)
Report per floor `[VERIFIED RSUD]` (script); targets `[EXPERIMENTAL RSUD]`:
- **Free ends**, split into cantilever tips (allowed) and others (list with mark and coordinates; target 0 or a list the user accepts);
- **Collinear overlaps > 50 mm** (target 0);
- **Duplicate marks** (target 0);
- **Beams passing through a column interior** without ending in it: mode B target 0; modes A/C expected at supports, review the rest;
- **Segmentation matches the project decision:** mode B, every beam ends at a support or cantilever tip; mode C, no beam crosses a zone line; every mode, no beam crosses a dilatation joint;
- **Long unsupported spans** (review);
- **End offsets ≠ the level standard** (e.g. −50), except drawn steps and upstands: catches beams reset by a curve edit or placed at the wrong level (RSUD: one beam at offset −18000, invisible in plan, "floating" in 3D) `[VERIFIED RSUD]`;
- **Cantilever (OV/Sov) tips without an edge beam closing the row** (target 0: a free tip means a missing edge beam) `[VERIFIED RSUD]`;
- **Count of `LOW CONFIDENCE` beams.**

Also:
- Count per mark/type vs the schedule/plan.
- `LocationCurve` end points vs the calibrated centreline (≤ 16 mm line-weight noise; investigate > 30 mm) `[IMPORTED KPwBI]`.
- Solid vs location: bounding-box centre of a test beam vs its location line, < 1 mm sideways.
- Top elevation = SFL of the slab above, or a documented step / step wall.
- Nothing crosses a joint; `document.GetWarnings()` grouped.

RSUD final numbers for reference: duplicate marks 0, overlaps 0, non-cantilever free ends Lt1 7, Lt2 1, Lt3 ~8, Lt4 5, all listed for the user.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Beams offset sideways by (b−200)/2 | Default Y justification; family flexes one face only | Y_JUSTIFICATION = 1 on all beams; test one beam's solid first | [IMPORTED KPwBI] |
| Beam ends hang in the air | Drawn line stops at a column face, a text label or a dash gap; sheets calibrated slightly differently | Resolve ends to supports (B2b step 3); audit (B5b) | [VERIFIED RSUD] |
| Corner stubs and notches after extending ends | End allowed to land up to ~450 mm *past* the target beam's end (overshoot) | Crossing point must lie within the target beam; corners go to the joint step | [VERIFIED RSUD] |
| End extended to the wrong support | 4 m search crossed a void or stair opening | Flag long extensions (> 1.5 m) and review | [VERIFIED RSUD] |
| Stubborn free end | The supporting beam was never modelled (edge beam drawn differently) | Find and model the missing support (B2b step 2, B2a.3) | [VERIFIED RSUD] |
| Secondaries strung along a girder fall short after a move | Girder moved by the flush snap | Re-scan ±400 mm after every geometry change | [VERIFIED RSUD] |
| Overlaps of exactly 2 × half-width | Crossing classified as an L-corner | Check for a collinear continuation first; trim to common point | [VERIFIED RSUD] |
| Flush snap moved interior beams | Snapped every eccentric beam (55 + 9 conflicts on one floor) | Perimeter-only test, run-grouped (15 on that floor) | [VERIFIED RSUD] |
| Girders chopped into irregular pieces | Placement cut wherever drawn lines stopped or crossed | Merge into runs first (441 runs, 2,330 → 904 on RSUD), then apply the segmentation mode | [VERIFIED RSUD] (merge) |
| Project later needs 4D zones but beams are continuous | Segmentation not asked at setup | Ask at setup (mode B when unsure); to convert later, cut runs at supports as in B2b step 5 B, restore offsets after every curve edit | [THEORY] |
| Column joins missing everywhere | DisallowJoinAtEnd applied at every end | AllowJoinAtEnd at column ends | [VERIFIED RSUD] |
| Beams notched/trimmed strangely | Auto-join to unrelated members | DisallowJoinAtEnd at non-column ends | [IMPORTED KPwBI] |
| Beams crossing a dilatation joint | Modelled grid-to-grid | Stop at the joint; add joint beams; never merge across | [IMPORTED KPwBI] |
| Secondary beams on the wrong lines | Assumed nearest grid | Drawn offsets (1A − 1200) | [IMPORTED KPwBI] |
| Knee-brace top snapped | Brace structural type | Beam type | [IMPORTED KPwBI] |
| Eave beams 950 mm high | Misread end-on section label | Trace leaders | [IMPORTED KPwBI] |
| Beam not at drawn size | Nearest size substituted silently | Exact type (A5) or LOW CONFIDENCE + user OK | [IMPORTED KPwBI] |
| A deeper beam's end face shows below a shallower one at a T | Real geometry | Accept | [VERIFIED RSUD] |

## Related
`building-logic.md`, `columns.md`, `slabs.md`, `structural-framing.md`, `drawing-interpretation.md`, `revit-families.md`, `model-validation.md`, `assets/field-reports/2026-11-23-rsud-cakung-beam-cleanliness.md`.
