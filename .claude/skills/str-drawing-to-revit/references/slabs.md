# Slabs — structural floors (OST_Floors)

> Legend: SKILL.md §8 · Last reviewed: 2026-11-24 · Revit tested: RSUD Cakung slab field report (Revit 2026, `mcp-server-for-revit`, ~180 slabs + 59 shafts on 8 levels; `assets/field-reports/2026-11-24-rsud-cakung-slab-cleanliness.md`, scripts in `assets/field-reports/2026-11-24-rsud-slab-cleanup-scripts/`) for outlines, clean-up, arcs, shafts and audit; KPwBI items imported; type creation `[THEORY]` except where tagged.
> Order of work: `workflows/element-modeling-workflow.md` (Stage A types → gate → Stage B: outline table → **clean the outlines** → build once per level → **audit and repair** → gate). This file supplies the slab-specific details.
> Support and connectivity rules (nothing floats): `building-logic.md` — read it before placing. Model the beams first.

## 1. Scope
Floor types (thickness, build-up, material), slab outlines (incl. true arcs), sunk and roof (dak) pieces, openings (shafts), levels and steps, splits at dilatation joints. Metal-deck slabs also set the steel level (`beams.md`). Not covered: rebar, slab design.

**The big lesson (RSUD):** a slab outline that is "right" against the drawing can still look wrong in the model. What makes a model clean is **internal consistency** `[VERIFIED RSUD]`:
- every slab corner is a plain rectangle corner, unless the drawing shows a curve;
- every slab edge that runs along an edge beam lies on that beam's **outer face**;
- every beam lies inside some slab, or is a drawn tie beam outside the building;
- every row of cantilevers ends at an edge beam that encloses a slabbed panel.

The user found the RSUD problems over **five rounds** of 3D review, because each round fixed only the selected instances or one kind of artifact. **Fix the class, not the instance: run the whole audit (B6) after every change, on every level.**

---

## A. Types

### A1. Where the slab types are on the drawings
- **Slab schedule** (`TABEL PELAT`, `DAFTAR PELAT`, `SLAB SCHEDULE`): mark → thickness (+ rebar). Often a small table on the slab plan (KPwBI p32 retrofit plan). Types may be named by thickness: `T12, T15, T20, T22` (DRC) `[VERIFIED 2026-11-20]`.
- **Slab details**: build-ups, metal-deck sections. The detail can disagree with the table (KPwBI: table 120, detail 150 metal deck; the user chose 150) `[IMPORTED KPwBI]`.
- Plan tags (S1, S2, SN1A …); tag text is often readable by `pdftotext -bbox` `[IMPORTED KPwBI]`.
- Find it: `scripts/find_schedules.py <folder> --element slabs`; confirm visually; ask if unclear.

### A2. What to extract per type
| Field | Notes |
|---|---|
| Mark | S1, S2, SN1A, PL1, T12 … |
| Thickness (mm) | from schedule **and** detail; conflict → ask |
| Build-up | plain concrete, or metal deck (deck gauge, rib height, topping) |
| Material | concrete grade if given |
| Rebar | record only |
| Source | sheet, revision, page, provenance |

### A3. Catalog notes
- One floor type per thickness + build-up + material; the name lists the marks it serves (KPwBI: `PELAT BETON 120mm (S1/S2/S3/SN1A)`, `PELAT METAL DECK 150mm (SN1A/SN1B)`, each with a type mark) `[IMPORTED KPwBI]`. KPwBI metal deck: 0.75 mm deck, 50 mm ribs + 100 mm topping = 150.
- **Piece kinds per level** `[VERIFIED RSUD]`:
  - **B** main slab;
  - **S** sunk wet-area slab (RSUD: top −100, from the hatched panels, checked against the architectural toilets);
  - **D** dak (exposed roof slab with waterproofing) = the area of a level **not covered by any slab above** (union of all higher floors and stair roofs). D is derived, not drawn.

### A4–A5. Make the types in Revit
Floors are a **system family**: no loadable family; duplicate an existing floor type and edit its compound structure.
```csharp
// call 1: duplicate a floor type
var src = (FloorType)document.GetElement(new ElementId(SRC_FLOOR_TYPE_ID));
var ft = (FloorType)src.Duplicate("PELAT BETON 120mm (S1/S2)");
return ft.Id.ToString();
```
```csharp
// call 2: set the layers by copying the source's compound structure and editing it
var ft = (FloorType)document.GetElement(new ElementId(NEW_ID));
var cs = ft.GetCompoundStructure();                 // copy of the duplicated type's structure
var layers = cs.GetLayers();
// edit the structural layer's width (mm/304.8) and material, then:
cs.SetLayers(layers);
ft.SetCompoundStructure(cs);
ft.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK).Set("S1");
return "ok";
```
- Copy-and-`SetLayers` worked; `CompoundStructure.CreateSimpleCompoundStructure` failed on the EndCap condition `[VERIFIED RSUD]`. `CreateSingleLayerCompoundStructure` for a one-layer type is `[THEORY]`.
- Metal deck: a `StructuralDeck` layer with a deck profile `[THEORY, OPEN]`; if unreliable, model the full thickness as concrete and note it.
- Floor instances must be **structural** (`FLOOR_PARAM_IS_STRUCTURAL`) `[THEORY]`.

### A6. Gate
Read back total thickness (`ft.GetCompoundStructure().GetWidth()` × 304.8) and the material per type; every slab mark on the plans resolves to a type.

---

## B. Placement

### B1. Where the outlines and levels are
Slab plan per level: thick outline (polylines **and Bézier curves**), tags, X-marked voids, stair/shaft openings, slope arrows, hatched sunk panels, dilatation joints (double thin line). Sections and level notes for SFL per zone. The architectural ground-floor plan for cross-checking the building extent (terraces, kerbs). **The beams must already be modelled** (their outer faces set edge lines, B2a.2).

### B2. Outline table (one per level)
Keep slab outlines as a **vector file per level**, generated and cleaned outside Revit, then read by Revit `[VERIFIED RSUD]`. RSUD format, in mm from grid 1 / grid A: `R,<B|S|D>` starts a piece, `L` starts a loop (first = outer, later = holes), `x,y` lines are points, `O` starts a shaft opening. Plus a beam export CSV (`id;mark;type;level;x0;y0;x1;y1;width;L|A`, L = line, A = arc) from one Revit call.
Per piece, record: kind (B/S/D), type, level, top elevation (SFL), source sheet, provenance. Hand-built pieces (e.g. an arc terrace) are named patches with their own Mark prefix (RSUD `PL-LT1-T`), re-applied after every regeneration.

### B2a. Interpretation rules (how to fill the table)
1. **Extent = the drawn slab outline polygon** (polylines and curves at the outline line weight on the slab sheet), cross-checked with the architectural plan. Never exclusion rectangles: on RSUD, "leave the forecourt out" done with rectangles also deleted the entrance terrace and a north strip that were inside the outline. Rectangles only as a last resort, clipped to the outside of the polygon `[VERIFIED RSUD]`.
2. **Edge line = the edge beam's outer face, where an edge beam runs along the edge** `[VERIFIED RSUD]`. This **replaces** the old strict rule "outline = drawn line, not beam faces": slab and beam sheets are calibrated separately (30–190 mm apart on RSUD), so taking edges from the slab sheet left beams sticking out sideways along whole façades (~100 edges on 7 levels).
   - Test: an axis-parallel edge ≥ 300 mm with parallel modelled beams whose outer face is 25–260 mm from it (either side), together covering ≥ 80 % of the edge. Then move the **whole edge** onto the face (keeps corners square).
   - Where no edge beam runs, the drawn outline stays the edge (KPwBI: edges set at beam faces *where no edge beam ran* left stubs `[IMPORTED KPwBI]`). Together: "outline for extent, edge-beam face for the edge line".
   - Exclude edges on a dilatation joint (they stay on the joint) and internal boundaries between pieces (sample 120 mm outside the edge: inside another piece = internal).
   - **Offset > ~100 mm: suspect the beam.** Check it against the beam sheet; one of the two is misplaced (RSUD Lt1 north row beam ~190 mm off sheet p31).
3. **Openings:** X-marked voids, stair, lift and shaft outlines → shaft openings (B4–B5), not sketch holes. **A void through several floors = one shaft per vertical run, from the start**; slab sketches keep only their outer outline plus holes for single-level voids. Cleaning up per-level voids later is hard (B5c) `[VERIFIED RSUD]`.
4. **Split at dilatation joints;** each side is its own slab.
5. **Top = SFL** of that zone; level offset = SFL − level elevation. Sunk pieces: their own offset (RSUD −100).
6. **True arcs:** if the outline has curve segments, model them as arcs (detection: `drawing-interpretation.md` §5 "Curved outlines"). Before saying "no curves", look at the raw outline objects in the area the user means.
7. **Supports:** every edge sits on a beam or wall, or is a drawn cantilever edge / void edge / joint face (building-logic §2).
8. **Dak = any slab area not covered by the level above** `[VERIFIED RSUD]`. Where ARS shows a room and STR shows its columns but no roof slab: add the slab, typed dak, with the edge beams STR does draw. Beams STR does not draw are left out (user rule, RSUD); the slab gets `MISSING SUPPORT … RFI` in Comments listing the beams it needs. Then re-type the slabs now covered by the new roof from dak to normal slab (only exposed slabs get waterproofing).


### B2b. Clean the outlines before building (on the vector file, not in Revit)
Order: **generate → corner/cap clean → snap edges to edge beams → corner/cap clean again → pre-build audit → build.** Keep every step an idempotent script on the vector file, so regenerating does not wipe fixes `[VERIFIED RSUD]`.

1. **Generate from vectors, never from a raster.** A raster may only decide *which cells are slab*; geometry comes from real coordinate lines `[VERIFIED RSUD]`:
   - build a **cell grid** from beam faces (merge lines within 80 mm into the dominant face), column faces only where needed, drawn slab-outline lines (priority lines), dilatation-joint lines and the edges of the floor above;
   - label each cell by majority vote (slab / sunk / dak / opening), trace loops along the grid lines;
   - snap edges within 200 mm of a priority line onto it;
   - **inset neighbouring pieces 20 mm** (sunk or dak against the main slab), so shared edges never touch (touching raises the modal "floors overlap" dialog).
   - If a raster mask is used for cell labels: fill beams as **rectangle polygons** (`fillPoly`), never thick lines (round caps make semicircles); include the columns that span the level, then close away column-only bumps (~33 px at 25 mm/px).
2. **Clean the loop artifacts** (each found on the vector loop alone) `[VERIFIED RSUD]` (last round's 3D check pending: `[EXPERIMENTAL RSUD]`):

   | Kind | Shape on the loop | Typical cause | Fix | Limits |
   |---|---|---|---|---|
   | **Corner step** | two short edges forming a staircase between two long perpendicular edges | edge wraps a column corner, or two beam faces meet off-line | replace the three corner points by the intersection of the long edges | both short edges ≤ 900 mm |
   | **U-cap** (notch or bump) | a short edge whose neighbours point in opposite directions | slab steps around a beam end or column on a straight edge | shift the short edge back by the smaller depth (equal depths remove it; unequal leave one step) | width ≤ 900, both depths ≤ 1000 |
   | **Sliver** | a U-cap a few mm to 120 mm wide but long (seen 63 mm × 2.8 m) | cell-grid lines too close | remove it (same shift) | width ≤ 120, any depth, outer loops only |
   | **Column hole** | small hole with no piece or opening inside | column footprint left in the mask | delete the hole loop (the column cuts the slab through its join) | < ~1.5 m², nothing inside |
   | **Paired step** | a bump in piece A fits a notch in neighbour B (slab vs dak, main-slab hole vs sunk piece) | piece boundary follows an upper floor or a hatch edge | fix both pieces together, keeping the 20 mm gap | as above |

   A column cuts through a floor anyway (Revit join): for structural slabs "fill to a square corner over the column" is always right, "notch around the column" never is.

   **Guards** (each learned from a near-miss):
   - *Overlap test:* rasterise all pieces of the level at 10 mm around the change; accept only if overlapping pixels do not increase; else try the paired fix on the overlapping piece; else skip.
   - *Both sides short:* only shift caps where both depths are short. A loose rule (one depth ≤ 700) once proposed deleting a 533 mm strip along a whole 8.4 m bay at the joint.
   - *Validity:* no self-intersection, ≥ 4 vertices, holes still inside the outer loop; then remove duplicate and collinear points.
   - *Leave alone:* steps along shaft or stair openings, and real voids without a shaft.
3. **Snap edges to edge-beam faces** (B2a.2).
4. **Clean again** (snapping can create new steps).
5. **Pre-build audit** on the file: B6 checks 2–6 and 12. Then build.

Scripts that implement this (RSUD-specific constants, `[EXPERIMENTAL RSUD]` elsewhere): `corner2.py` + `cap.py` (step 2), `snapedge.py` (step 3), `audit.py` (short edges), in `assets/field-reports/2026-11-24-rsud-slab-cleanup-scripts/`.

### B3. Cross-check before building
Area per mark vs the plan; every piece has a verified type (Stage A); heights follow the height chain; the pre-build audit (B2b.5) passed.

### B4–B5. Revit procedure
**File hand-off** `[VERIFIED RSUD]`: Python writes the outline file; the C# script reads it with `File.ReadAllLines` and builds the floors. This keeps every Revit script under ~4 kB whatever the slab count.
```csharp
// one slab with an arc edge and a hole; points in mm (from the file in practice)
Func<double, double, XYZ> P = (x, y) => new XYZ(x / 304.8, y / 304.8, 0);
var outer = new CurveLoop();
outer.Append(Line.CreateBound(P(0, 0), P(12000, 0)));
outer.Append(Line.CreateBound(P(12000, 0), P(12000, 4000)));
outer.Append(Arc.Create(P(12000, 4000), P(8000, 8000), P(10828, 6828)));   // start, end, point on arc
outer.Append(Line.CreateBound(P(8000, 8000), P(0, 8000)));
outer.Append(Line.CreateBound(P(0, 8000), P(0, 0)));
var loops = new List<CurveLoop> { outer };   // extra loops = holes (only for real slab holes; voids use shafts)
var f = Floor.Create(document, loops, new ElementId(FLOOR_TYPE_ID), new ElementId(LEVEL_ID));
f.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(OFFSET_MM / 304.8);
f.get_Parameter(BuiltInParameter.FLOOR_PARAM_IS_STRUCTURAL).Set(1);
f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("PL2-001");
f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set("S1 | S-501 p18 | EXPLICIT");
return f.Id.ToString();
```
- **Arcs:** `CurveLoop.Append(Arc.Create(start, end, pointOnArc))`, mixed with lines in loop order; `Floor.Create` accepted it at once `[VERIFIED RSUD]` (1 terrace slab, 3 arcs + a chamfer; area read back 228 m² vs ~224 estimated).
- **Openings = shaft openings** for voids, lifts and stairs `[VERIFIED RSUD]` (59 shafts, 0 dialogs): `document.Create.NewOpening(baseLevel, topLevel, CurveArray)`, then Top Constraint = the slab's level, Top Offset 0, Base Offset = −(slab thickness + finish margin) (RSUD −280; −400 for the slab on grade). Hosted floor openings raised the modal "There is a circular chain of references". Shafts have no Mark or Comments parameter.
- **Rebuild one level per call:** delete and rebuild the whole level in one call, in an order that never overlaps. Several levels in one call raised "insufficient memory" and rolled back `[VERIFIED RSUD]`. Overlapping floors raise the modal "Highlighted floors overlap", which blocks the API and looks like a timeout `[VERIFIED RSUD]` (extends KPwBI).
- **Hand-built pieces** (arc terraces) are excluded from the delete-and-rebuild filter by Mark prefix and included in the overlap test as fixed pieces `[VERIFIED RSUD]`.
- **Delete last** (or re-collect after deleting): iterating a cached list after `Delete` throws InvalidObject, and the edits before the error stay committed. Keep reporting (warnings, areas) in a separate read-only call: an exception there rolled back the modelling too `[VERIFIED RSUD]`.
- `HOST_AREA_COMPUTED` reads 0 until `document.Regenerate()` `[VERIFIED RSUD]`.
- `double[]` and `Func<>` instead of `int[]` and local functions (host compiler quirks) `[IMPORTED KPwBI]`.
- MCP alternative: `create_surface_based_element` (`OST_Floors`, outer loop only, no openings, no arcs) `[LIMITATION]`.

### B5b. Audit and repair after building
1. Run the **slab audit** (B6) on every level, not just the one changed.
2. **A beam sticking out of the slab: classify before fixing** `[VERIFIED RSUD]`:

   | Cause | What it looks like | Fix |
   |---|---|---|
   | Panel cut away by an over-wide exclusion | cantilever row and edge beam with no slab | extent = the drawn outline polygon (B2a.1) |
   | Edge beam never modelled, so the panel was never enclosed | OV/Sov cantilevers with free tips; a panel without slab | add the edge beam from the beam sheet, then the slab panel |
   | Phantom beam (on no drawing) | a beam not on the beam sheet or slab sheet | delete it, with the user's OK |
   | Beam at the wrong height or position | floating far from its floor; beside its column line | read back offsets and positions (`beams.md` B5b); fix |

   Drawn tie beams outside the building (forecourt, drop-off) are correct: list them once and exclude them from the scans.
3. **A change ripples down:** adding or removing slab on a level changes the dak (D) on every level below. Re-run the cover calculation for the levels below, or edit them in the same pass `[VERIFIED RSUD]`.
4. **"Fix them all" means the whole model:** treat the user's selection as one example of a class, scan every level for that class, and report how many were found and fixed.
5. Mechanical artifacts (corners, slivers, offsets): just fix them. Drawing questions (phantom or misplaced beams): list what each selected element should be per the sheet, then let the user decide.

### B5c. Continuous shafts through several floors (merging per-level voids) `[VERIFIED RSUD]`
RSUD had voids modelled level by level: 59 shaft openings plus 184 sketch holes, 51 of them duplicates. The user wanted one continuous shaft per vertical void. Method that worked:
1. **Export every void** with one Revit script (`File.WriteAllText` to the project folder works): source (shaft `Opening` in Shaft Openings with `BoundaryCurves`, or a slab sketch inner loop from `Sketch.Profile`, every loop except the outer one, which has the largest bbox area), level elevation, tessellated outline in plan mm.
2. **Analyse in Python** (bounding boxes if shapely is missing): pair each shaft with the sketch hole on the same level when they overlap > 50 %; cluster level by level with IoU ≥ 0.75 to the void on the next level down; within a cluster keep the longest contiguous run where every level is within a tolerance of the run's median bbox.
3. **Ask the user for the tolerance, with numbers:** the same void differed 30–520 mm between levels (each level traced from its own plan). RSUD options: ≤ 100, ≤ 250 (recommended), ≤ 520 mm, each with its shaft count and how far edges move; the user chose 250.
4. **One shaft per run:** `document.Create.NewOpening(bottomLevel, topLevel, curveArray)` with the median rectangle; base = lowest void level with `WALL_BASE_OFFSET` −280 (−400 at the slab on grade); top = highest void level, `WALL_TOP_OFFSET` 0. Then delete the per-level shafts of that run.
5. **Verify three ways:** (a) beams are not cut: framing volumes (`HOST_VOLUME_COMPUTED`) before and after one test shaft; shafts did not cut structural framing; test before the batch. (b) Only voided slabs are cut: for slabs whose bbox overlaps the shaft, test points (centre and four corners 150 mm in) against the slab **sketch** loops (even-odd rule), not its geometry; `ElementIntersectsSolidFilter` is circular here (a slab already cut never intersects the shaft). (c) **A hole in one slab does not mean the level is open:** at one RSUD level the hole was filled by a separate atrium roof slab, so the shaft had to start one level higher. Check every slab at that level.
6. **Record:** shafts have no Mark or Comments, so keep a table in the project log: mark, element id, levels, x/y range, per-level shafts replaced, maximum deviation, `LOW CONFIDENCE` when over 100 mm.
- **Split runs are expected:** a void drawn 500 mm off on one level splits the stack (RSUD west stair: Lantai 2–4 and Lantai 6–Rooftop). Do not force it beyond the agreed tolerance; list the split levels for the user.
- **Sketch holes cannot be removed by script:** the MCP always has a transaction open (`document.IsModifiable == true`), so `SketchEditScope` cannot start `[LIMIT]`. The only route is rebuilding the slab (`Floor.Create` with the remaining loops, copy type, level, offset, Mark, Comments, re-join every beam; RSUD slabs had 18–308 joins each); the user declined it as too invasive. With sketch holes kept, merge only stacks that already have shaft openings: a shaft over sketch-hole-only voids adds elements without removing any.

### B6. Verification — the slab audit (what "done" means for a level)
Run all after every change, on every level; report the numbers. Done at zero, or a short list the user accepts `[VERIFIED RSUD]` (checks); thresholds `[EXPERIMENTAL RSUD]`.

| # | Check | Pass |
|---|---|---|
| 1 | Revit warnings (all, grouped) | 0 unexplained |
| 2 | Floor overlap (rasterised pieces of one level) | 0 px |
| 3 | Corner steps (two short edges ≤ 900 at a corner) | 0, except along openings |
| 4 | U-caps (width ≤ 900, depths ≤ 1000) and slivers (≤ 120) | 0, except along openings |
| 5 | Holes with nothing inside (no piece, no opening) | 0, or each listed as a void |
| 6 | Sketch edges < 200 mm | each explained (opening steps, drawn hatch shapes) |
| 7 | Beam centreline outside every slab by > w/2 + 100 mm | 0, except listed tie beams outside the building |
| 8 | Beam face outside the slab edge by 40–1200 mm along ≥ 0.9 m | 0, except faces along openings |
| 9 | Free beam ends; OV/Sov tips without an edge beam | 0 |
| 10 | Panels framed by beams with no slab or opening | 0, except voids |
| 11 | Beam end offsets ≠ the expected offset for their SFL zone | 0, except drawn steps and upstands |
| 12 | Edge beam vs drawn outline offset > 100 mm | each checked against the beam sheet |

Scripts (RSUD-specific): `prot.py` (#7), `side.py` (#8), `freeend.py` (#9), `encl.py` (#10), `audit.py` (#6). Also: area per mark vs the plan (±1%); top elevation = SFL per zone; every beam top at the slab top above or a documented step.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Jagged slab edges, many small "extrusion profiles", stair-stepped or rounded corners | Outline traced from a raster (round line caps, pixel corners, missing columns) | Cell grid of real face lines (B2b.1) | [VERIFIED RSUD] |
| Corners "don't meet like a rectangle"; notches, slivers, small holes | Loop artifacts | Artifact table + guards (B2b.2) | [VERIFIED RSUD] |
| Beam faces stick out of the slab side along whole façades | Slab edges from the slab sheet, beams from the beam sheet (30–190 mm apart) | Snap edges to edge-beam outer faces (B2a.2) | [VERIFIED RSUD] |
| Cantilevers end in empty space / panel without slab | Edge beam never modelled; or panel cut by exclusion rectangles | Add the edge beam then the slab; extent = outline polygon | [VERIFIED RSUD] |
| Fix proposed to delete a long strip of slab | Cap rule too loose (one depth ≤ 700) | Both depths short (B2b guards) | [VERIFIED RSUD] |
| Modal "circular chain of references" | Hosted floor openings | Shaft openings | [VERIFIED RSUD] |
| Same void modelled on every level, plus sketch holes | Voids drawn per level | One shaft per vertical run from the start; merge later with B5c | [VERIFIED RSUD] |
| Shaft starts a level too low | A hole in the main slab was filled by another slab at that level | Test every slab at the level (B5c step 5c) | [VERIFIED RSUD] |
| Covered slab still typed dak | Roof added above later | Re-type covered slabs to normal (B2a.8) | [VERIFIED RSUD] |
| "Insufficient memory", whole call rolled back | Several levels rebuilt in one call | One level per call | [VERIFIED RSUD] |
| Round corners modelled as many short lines | Curves not detected (classed as kerbs) | Detect Bézier segments; arcs in the loop | [VERIFIED RSUD] |
| Dak wrong on the level below after an edit | Cover not recomputed | Re-run the cover calculation for lower levels | [VERIFIED RSUD] |
| API call hangs | Modal overlap warning | Inset neighbours 20 mm; non-overlapping order; dismiss | [VERIFIED RSUD] / [IMPORTED KPwBI] |
| Slab stubs past the edge | Edge at beam face where no edge beam ran | Drawn outline where no edge beam | [IMPORTED KPwBI] |
| Slabs invisible in plan | Template view filters ("Floors - Concrete NOT") | Remove the filters from working views | [IMPORTED KPwBI] |
| Wrong thickness | Plan table vs detail differ | Ask; log | [IMPORTED KPwBI] |

## Related
`building-logic.md`, `beams.md`, `drawing-interpretation.md`, `model-validation.md`, `assets/field-reports/2026-11-24-rsud-cakung-slab-cleanliness.md`.
