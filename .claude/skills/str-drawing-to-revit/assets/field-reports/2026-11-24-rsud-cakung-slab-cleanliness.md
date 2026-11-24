# Handover to the skill agent: slab cleanliness, corner artifacts, protruding beams, true arcs

From: the structure agent on the RSUD Cakung tender model (a 6-floor hospital plus roof and stair-roof; structural DED of 84 pages).
Session: 2026-11-23 to 2026-11-24. Scope: slabs and dak on Lantai 1 to 6, Rooftop (+26.00) and Atap Tangga (+29.00). That is about 180 slabs and 59 shaft openings. It also covered the beams found to be inconsistent with them.
Setup: **Revit 2026**, driven through **mcp-server-for-revit** `send_code_to_revit`. C# runs inside `Execute` with `document` and an open transaction. PDF work used pdfplumber, poppler and OpenCV in a Linux workspace. The slab outlines were generated in Python and written to text files. Revit read those files and built the floors.

This report follows on from `2026-11-23-rsud-cakung-beam-cleanliness.md`. The tags mean the same as there:
- **[VERIFIED RSUD]**: run in Revit 2026 on this model, with the result checked by an audit script and/or the user's 3D screenshots.
- **[EXPERIMENTAL RSUD]**: run, and the numbers came out right, but the user hasn't confirmed the result in 3D yet.
- **[THEORY]**: reasoned, not run.

I read the repo at `main` (`SKILL.md`, `references/slabs.md`, `beams.md`, `building-logic.md`, `model-validation.md`, `troubleshooting.md`, `lessons-learned.md`, and the beam field report). File and section names under "Skill impact" refer to that state.

The scripts I used are attached in `slab-cleanup-scripts/` (Python, about 1–5 kB each; see the README there). They are field tools, not polished code. Project-specific constants are marked.

---

## 0. The big lesson in one paragraph

A slab outline that is "right" against the drawing can still look wrong in the model. What makes a model look clean is **internal consistency**:
- every slab corner is a plain rectangle corner, unless the drawing shows a curve;
- every slab edge that runs along an edge beam lies on that beam's outer face;
- every beam lies inside some slab, or is a drawn tie beam outside the building;
- every cantilever tip ends at an edge beam that encloses a slabbed panel.

The user found every problem in this report by orbiting a 3D view, over **five rounds**: jagged "extrusion profiles", corners that didn't meet, round corners, protruding beams (twice), and leftover notches. Each round found the next layer of artifacts. That happened because I fixed only the instances the user had selected, or one class of artifact at a time.

**Fix the class, not the instance. Run every audit in section 9 after every change, on every level.**

---

## 1. Slab outlines generated from a raster leave artifacts

**Found.** I generated slab outlines from a raster (25 mm/px) built like this:
1. Draw the beams as thick lines and add the columns.
2. Take the regions enclosed by beams as slab panels.
3. Merge the panels per level.
4. Vectorise the result.

In 3D the user saw:
- many small "extrusion profiles" (steps and jogs) along slab edges and around voids;
- corners that were stair-stepped, or slightly rounded, instead of square.

**Causes (all agent errors):**
- **Round line caps.** `cv2.line` draws beams with round caps, so every beam end became a semicircle in the mask. Fix: fill each beam as a rectangle polygon (`fillPoly`), never as a thick line.
- **Missing columns in the frame mask.** Without the columns, beam-end gaps leaked, so panels merged or broke. Fix: add the columns that span the level. Then remove the parts of the mask that are column-only (a morphological closing of about 33 px), so slabs don't grow bumps around columns.
- **Pixel corners.** Vectorising pixel boundaries gives 12.5 mm offsets and 1-pixel jogs, and neighbouring pieces end up with different rounding.

**Rule (the working method).** The raster may only decide *which cells are slab*. The geometry must come from vectors:
1. Build a **cell grid** from real coordinate lines: beam faces (merge lines within 80 mm into the dominant face), column faces only where needed, drawn slab-outline lines (priority lines), the dilatation-joint lines, and the edges of the floor above.
2. Label each cell by majority vote (slab / sunk / dak / opening), then trace loops along the grid lines.
3. Snap edges within 200 mm of a priority line onto that line.
4. Inset neighbouring pieces (sunk or dak against the main slab) by 20 mm. That keeps shared edges from touching, which would raise the modal "floors overlap" dialog.

**Evidence.** All levels were rebuilt this way: 165 slabs, 59 shafts, 0 overlap dialogs, sketch edges shorter than 200 mm reduced from hundreds to 50. The user accepted it, then found the next layer (sections 2–4).

**Status.** [VERIFIED RSUD]

**Skill impact.**
- `slabs.md` B4–B5: add "never send raster outlines to Revit; trace on a grid of real face lines".
- `troubleshooting.md`: new row, "jagged slab edges / extrusion profiles → raster outline".

---

## 2. Corner artifacts: a short taxonomy and the fix for each

Even after section 1, the user kept finding corners that "don't meet like the corners of a rectangle". They come in five kinds. Each can be detected on the vector loop alone, which is cheap, and each has one fix.

| Kind | Shape on the loop | Typical cause | Fix | Limits used |
|---|---|---|---|---|
| **Corner step** | two short edges forming a staircase between two long, perpendicular edges | the slab edge wraps a column corner, or two beam faces meet off-line at a corner | replace the three corner points by the intersection of the two long edges (a plain corner) | both short edges ≤ 900 mm |
| **U-cap (notch or bump)** | a short edge whose two neighbours point in opposite directions | the slab steps around a beam end or column on a straight edge | shift the short edge back by the smaller depth. Equal depths remove the cap completely; unequal depths leave a single step | cap width ≤ 900, both depths ≤ 1000 |
| **Sliver** | a U-cap only a few mm to 120 mm wide but long (seen: 63 mm × 2.8 m) | cell-grid lines too close together | remove it (same shift) | width ≤ 120, any depth, outer loops only |
| **Column hole** | a small hole in a slab with no piece or opening inside it | column footprint left in the mask | delete the hole loop (the column cuts the slab through its join) | < about 1.5 m², nothing inside |
| **Paired step** | piece A has a bump that fits a notch in neighbouring piece B (slab vs dak, main-slab hole vs sunk piece) | the boundary between pieces follows an upper floor or a hatch edge | fix both pieces together, keeping the 20 mm gap | as above |

**Guards (all needed; each was learned from a near-miss):**
- **Overlap test.** Rasterise every piece of the level at 10 mm in a box around the change. Accept the change only if the count of overlapping pixels does not grow. If it does, try a complementary fix on the overlapping piece (the paired step). Otherwise skip the change.
- **Only shift caps where both sides are short.** A loose rule (one depth ≤ 700) once proposed removing a 533 mm strip of slab along a whole 8.4 m bay at the expansion joint.
- **Validity.** After each change: no self-intersection, at least 4 vertices, holes still inside the outer loop. Then simplify (remove duplicate and collinear points).
- **Leave alone:** steps along shaft or stair openings (the edge follows the opening), and real voids that have no shaft element.

**Evidence.**
- Round 1: 32 corner steps filled plus their matching holes.
- Round 2: 6 U-caps or paired steps, 1 sliver, 2 column holes.
- All levels rebuilt, with 0 overlap warnings and 0 Revit warnings at the end.
- Scripts: `corner.py`, `corner2.py` (`clean2`, `pairs`), `cap.py`.

**Status.** Detection and fix: [VERIFIED RSUD] (counts, warnings). User 3D confirmation of the last round: pending, so [EXPERIMENTAL RSUD].

**Skill impact.**
- New `slabs.md` section "B5b. Slab clean-up after placing", with the table above.
- `model-validation.md`: a new check "slab loop artifacts = 0" (section 9).
- Remember that a column cuts through a floor anyway (Revit join). So "fill to a square corner over the column" is always right for structural slabs, and "notch around the column" never is.

---

## 3. Beams sticking out sideways: the slab edge must be the edge beam's outer face

**Found.** The user selected perimeter beams whose outer face stood 50–260 mm outside the slab edge, along whole sides of the building. That was about 100 edges over 7 levels.

**Cause.** Following `slabs.md` B3 rule 1 ("outline = the drawn thick line, not beam faces"), the slab edges came from the drawn outline on the *slab* sheet. The beams had been placed (by another agent) from the *beam* sheet. Calibration differs between sheets by about 30–190 mm, so beams and slab disagree.

**Rule (replaces the strict reading of B3 rule 1).**
1. **The drawn outline decides the slab's extent:** which areas are slab, the terrace, cantilever strips, curves.
2. **Where an edge beam runs along an edge, the slab edge is that beam's outer face, in the model.** They must coincide, because that is how they are built.
   - Test: an axis-parallel edge of at least 300 mm; parallel modelled beams whose outer face is 25–260 mm from it (either direction); together covering at least 80 % of the edge length.
   - Then move the whole edge onto the face. Moving whole edges keeps corners square.
3. Where there is no edge beam, the drawn outline stays the edge.
4. **Exclude:** edges on a dilatation joint (they stay on the joint; snapping to the joint beam left a gap to the joint). Also exclude internal boundaries between pieces (slab vs dak vs sunk). Detect those by sampling 120 mm outside the edge: if the sample is inside another piece, it is internal.
5. **If the offset is over about 100 mm, suspect the beam.** Check the beam against the beam sheet, because one of the two is misplaced. Example: the Lt1 north row beam is about 190 mm off sheet p31.

This doesn't contradict KPwBI. There, edges set at beam faces *where no edge beam ran* left stubs. The two rules combine as "outline for extent, edge-beam face for the edge line".

**Evidence.** `snapedge.py` snapped 6–18 edges per level, all levels were rebuilt, and the side-protrusion scan dropped from 69 hits to 13. The remaining 13 are faces along openings, which is correct, plus a few beams that are themselves off their drawn line (section 4).

**Status.** [VERIFIED RSUD] (scan numbers). User confirmation pending.

**Skill impact.**
- `slabs.md` B3 rule 1: rewrite as above.
- `building-logic.md` §2 (slab supports): "slab edge = outer face of the supporting edge beam".
- `troubleshooting.md`: "beam faces stick out of the slab side → slab edge on the drawn outline from a different sheet than the beam; snap edge to beam face".

---

## 4. Beams sticking out of the slab: usually a slab problem, sometimes a beam problem

**Found.** Over three rounds the user selected beams that stuck out into empty space. Each had one of four different causes. Classify before fixing:

| Cause | What it looks like | Seen | Fix |
|---|---|---|---|
| **A panel was cut away by an over-wide exclusion zone** | a cantilever row and edge beam with no slab | Lt1 S entrance terrace: "leave the forecourt out" was implemented as rectangles over the full width, which also deleted the terrace *inside* the drawn outline. Lt1 N cantilever strip stopped short | the drawn outline polygon is the extent (section 5) |
| **The edge beam was never modelled, so the panel was never enclosed and never slabbed** | cantilevers (OV/Sov) with free tips; a panel without slab | Lt5 NE and SE panels east of the joint (L1 and L2 edge beams missing) | add the edge beam (from the beam sheet), then the slab panel. The enclosed-panel slab logic can't see an open frame |
| **Phantom beam** | a beam not on any drawing | Lt5 OV2 east of the joint; a north–south "OV2" that should have been four east–west OV1 cantilevers; an Lt1 placeholder beam cutting a curved corner | check the beam sheet *and* the slab sheet; delete it, with the user's OK |
| **Beam at the wrong height or position** | a beam floating far from its floor, or running beside its column line | an Lt5 beam at elevation 0 (level offset −18000); a B7 placed 300 mm off its column line | read back offsets and positions (section 7); fix |

Beams outside the building that are drawn there (ground-floor tie beams of the forecourt and drop-off) are correct. List them once and exclude them from the scan.

**Detection (scripts attached).**
- `prot.py`: a beam centreline more than w/2 + 100 mm outside every slab (distance transform on the slab mask).
- `side.py`: a beam face 40–1200 mm outside the slab along at least 0.9 m (sideways protrusion, section 3).
- `freeend.py`: beam ends with no other beam within half-width + 260 mm. Filter by type: free **OV/Sov** ends mean a missing edge beam.
- `encl.py`: panels framed by beams that have no slab or opening.

**Status.** [VERIFIED RSUD]

**Skill impact.**
- `slabs.md` B6: add the four scans.
- `beams.md` B6 / `building-logic.md` §6: "a free cantilever tip is allowed only if an edge beam closes the row. Cantilevers without a tip beam mean the edge beam is missing."
- `model-validation.md`: new checks (section 9).

---

## 5. "Model only to the building extent" must use the drawn outline, not rectangles

**Found.** The user said the forecourt has a drop-off road, so leave it out and only model to the extent of the building. I implemented that as four exclusion rectangles. They also removed:
- the entrance terrace (inside the drawn outline, with cantilever beams and curved edge beams, matching the terrace on the architectural plan);
- a strip on the north side.

**Rule.** The building extent is the **drawn slab outline polygon**: polylines and Bézier curves of the outline line weight, on the slab sheet. Cross-check it against the architectural ground-floor plan, where the terrace or kerb line shows the same shape. Exclusion rectangles are allowed only as a last resort, clipped to the outside of that polygon.

**Status.** [VERIFIED RSUD]

**Skill impact.** `slabs.md` B3: add "extent = the drawn outline polygon; never rectangles".

---

## 6. True round corners: detect them, then model them as arcs

**Found.**
- The user asked that round corners be true arcs, not many short lines.
- My first scan concluded "no curved slab edges in STR". It was wrong: I classed the terrace arcs as drop-off kerbs because they lay in the forecourt area. The scan has to look at the **outline objects themselves**.

**Detection (pdfplumber).**
- Curved outline pieces come as `curve` objects whose `path` contains `('c', p1, p2, p3)` Bézier segments, at the outline line weight (0.71 pt here).
- A quarter circle has its two control points on the tangent lines. The centre is the corner of the control polygon opposite the arc: for `m P0 c P1 P2 P3` with P1 straight below or beside P0, centre = (x of P3, y of P0) or the reverse. The radius is |P0 − centre| in pt; convert with the sheet calibration.
- **Convex or concave:** the beam's inner face line (dashed, offset by the beam width) lies on the slab side. If the inner face is farther from the centre than the outline, the slab is outside the circle: a concave corner.
- **Calibration is anisotropic** (x and y scales differ by about 2 %), so the converted "circle" becomes an ellipse. Use one round radius, and set the centre so the arc is tangent to both straight edges in model coordinates.

**Revit.**
- Floor sketch: `CurveLoop.Append(Arc.Create(start, end, pointOnArc))`, mixed with `Line`s, in loop order. `Floor.Create` accepted it at once.
- Curved beams: `document.Create.NewFamilyInstance(arc, symbol, level, StructuralType.Beam)` worked for a concrete rectangular family. The centreline radius is the outline radius ± half the beam width (− for convex, + for concave).
- Straight beams that ran past the arc into the forecourt were trimmed at the arc beam's centreline circle.

**Evidence.** 1 terrace slab (3 arcs: R4000 convex, R4996 concave, R2504 convex, plus a 45° chamfer) and 3 curved S1 300x600 edge beams were built. The area read back as 228 m², against a hand estimate of about 224 m².

**Status.** [VERIFIED RSUD] (built and read back). User 3D check pending.

**Skill impact.**
- `drawing-interpretation.md` §5: Bézier detection and the centre rule.
- `slabs.md` B4–B5: an arc loop snippet.
- `beams.md` B4–B5: curved beams.
- Also: when the user asks for round corners, scan every slab outline for `c` segments before saying there are none.

---

## 7. Revit mechanics found this session

| Finding | Evidence | Status |
|---|---|---|
| **Setting `LocationCurve.Curve` resets `STRUCTURAL_BEAM_END0/1_ELEVATION` to 0.** Ten beams I had moved or extended dropped 50 mm, from top −50 to top 0. After any curve edit, write the end offsets back explicitly (read them *before* the edit). | Global read-back of end offsets found them | [VERIFIED RSUD] |
| **Read back end offsets on every level.** One beam sat at level offset −18000 (that is, at ground level while referenced to Lantai 5). It was invisible in plan, and obvious in 3D as a "floating" beam. Check: every beam's end offsets equal the level's standard value (−50 here), except drawn steps and upstands. | Found | [VERIFIED RSUD] |
| "Beam or Brace is slightly off axis" came from 2–7 mm drift between endpoints. Snap the endpoints orthogonal (average the shared coordinate), then restore the offsets. 4 warnings went to 0. | Run | [VERIFIED RSUD] |
| **Shaft openings, not sketch holes or hosted openings,** for voids, lifts and stairs. Hosted floor openings raised the modal "There is a circular chain of references" dialog. Use `document.Create.NewOpening(baseLevel, topLevel, CurveArray)`, then set "Top Constraint" = the slab's level, "Top Offset" 0, "Base Offset" = −(slab thickness + finish margin) (−280 here; −400 for the slab on grade). Shafts have no Mark or Comments parameter. | 59 shafts, 0 dialogs | [VERIFIED RSUD] |
| **"Highlighted floors overlap" modal** appeared when pieces touched along an edge with rounding differences. Inset sunk and dak pieces 20 mm from the main slab. Delete and rebuild the whole level in one call, in an order that never overlaps. | Repeated until fixed | [VERIFIED RSUD] (extends the KPwBI row) |
| **One level per call.** Rebuilding several levels in one call raised "insufficient memory" and rolled back. | Seen | [VERIFIED RSUD] |
| **Iterating a cached element list after a `Delete` in the same script throws InvalidObject.** The catch returned, and the edits before the error *stayed committed*. Delete last, or re-collect after deleting, then read back what committed. | Seen | [VERIFIED RSUD] (adds to the beam report's row) |
| An exception in the *reporting* part of a script (e.g. reading warnings) rolled back the whole call, including the modelling. Keep reporting in a separate read-only call. | Seen | [VERIFIED RSUD] |
| `Floor` area (`HOST_AREA_COMPUTED`) reads 0 until `document.Regenerate()`. | Seen | [VERIFIED RSUD] |
| Floor type layers: `CompoundStructure.CreateSimpleCompoundStructure` failed on the EndCap condition. Copy the compound structure of an existing type and use `SetLayers`. | Run | [VERIFIED RSUD] (corrects the `[THEORY]` single-layer snippet in `slabs.md` A4–A5 for multi-layer types) |
| A file-based hand-off (Python writes `R,tag` / `L` / points / `O` / points; C# reads it with `File.ReadAllLines`) keeps each Revit script under 4 kB, whatever the slab count. | Run on all levels | [VERIFIED RSUD] |

---

## 8. Slab, sunk slab and dak pieces, and how a change ripples down

- **Piece types per level:**
  - **B** main slab;
  - **S** sunk wet-area slab (top −100, from the hatched panels, checked against the architectural toilets);
  - **D** dak (exposed roof slab with waterproofing): the area *not covered by any slab above*, computed as the union of all higher floors and the stair roofs.
- **A change on one level changes the dak on the levels below it.** Adding the Lt5 SE panel turned the Lt4 area under it from dak into a normal slab. After any edit, re-run the cover calculation for the levels below, or edit them in the same pass.
- **Keep post-processing as idempotent scripts on the vector file:** generate → corner/cap clean → snap edges to beams → corner/cap clean again → audit → rebuild. That way, regenerating from the raster pipeline doesn't wipe the manual fixes. Hand edits (a new panel, an arc piece) go in as named patches that can be re-applied.
- Hand-built pieces that are not in the generated file (the arc terrace) must be excluded from the delete-and-rebuild filter (here, Mark prefix `PL-LT1-T`). Add them to the overlap test as fixed pieces.

**Status.** [VERIFIED RSUD]

**Skill impact.**
- `slabs.md` A3: list the piece types (B / S / D) and how D is derived.
- `slabs.md` B5: the ripple rule and the pipeline order.

---

## 9. The slab audit: what "done" means for a level

Run all of these after every change, on every level, and report the numbers. A level is done at zero, or at a short list the user has accepted.

| # | Check | Pass |
|---|---|---|
| 1 | Revit warnings (all, grouped) | 0 unexplained |
| 2 | Floor overlap (rasterised pieces of one level) | 0 px |
| 3 | Corner steps (two short edges ≤ 900 at a corner) | 0, except along openings |
| 4 | U-caps (width ≤ 900, depths ≤ 1000) and slivers (≤ 120) | 0, except along openings |
| 5 | Holes with nothing inside (no piece, no opening) | 0, or each listed as a void |
| 6 | Sketch edges < 200 mm | each explained (opening steps, drawn hatch shapes) |
| 7 | Beam centreline outside every slab by > w/2 + 100 | 0, except listed tie beams outside the building |
| 8 | Beam face outside the slab edge by 40–1200 along ≥ 0.9 m | 0, except faces along openings |
| 9 | Free beam ends; OV/Sov tips without an edge beam | 0 |
| 10 | Panels framed by beams with no slab or opening | 0, except voids |
| 11 | Beam end offsets ≠ the level standard | 0, except drawn steps and upstands |
| 12 | Edge beam vs drawn outline offset > 100 mm | each checked against the beam sheet |

**Skill impact.** `model-validation.md`: add these as checks #19–#24, or under "slab audit". Referencing them from `slabs.md` B6 would be enough.

---

## 10. Process lessons

- **"Fix them all" means a full-model pass.** The user selects a few examples. Treat them as a class, scan every level for it, and report the count found and fixed. Three of the five rounds would have been one round if I had done that.
- **Don't trust a "none found" scan for something the user asked about** until you have looked at the raw objects in the area they meant (the round corners in section 6).
- **Explaining before fixing pays off when the cause is a drawing question.** For the Lt5 steel-roof ring, I listed what each selected beam should be, from the sheet, and which were phantom or misplaced. The user then decided. For mechanical artifacts (corners, slivers, offsets) the user wants them just fixed.
- **Record status as you go.** The project timelog / status-board rule cost little and made the five-round story auditable.

---

## 11. Gaps in the skill that this session exposed

1. `slabs.md` B3 rule 1 ("outline = drawn line, not beam faces") needs the section 3 refinement. As written, it produces sideways-protruding beams whenever slab and beam sheets are calibrated separately.
2. `slabs.md` has no post-placement clean-up (B5b) and no slab audit beyond area, elevation and overlap.
3. Curved outlines and curved beams are not covered anywhere.
4. The beam-curve edit snippet in `beams.md` B4–B5 needs the "offsets reset, write them back" warning.
5. `building-logic.md` should add "a cantilever row needs an edge beam at its tips; free OV tips mean a missing beam" and "slab edge = edge-beam outer face".
6. Shaft openings vs sketch holes vs hosted openings is not in `slabs.md`.
7. `model-validation.md` #6 (beam top vs slab) should also read back the end offsets themselves (section 7, rows 1–2).

---

## Attached scripts (`slab-cleanup-scripts/`)

| File | What it does |
|---|---|
| `corner.py` | slab-file parse/write, loop area, first corner-step detector |
| `corner2.py` | `clean2` (corner steps, incl. sunk piece + matching main-slab hole), `pairs` (slab/dak paired steps) |
| `cap.py` | U-cap / sliver collapse with the raster overlap guard and validity check; `simplify` |
| `snapedge.py` | snap slab edges to edge-beam outer faces (section 3 rule and exclusions) |
| `prot.py` / `protlib.py` | beams outside slab (scan #7); slab masks incl. hand-built arc pieces |
| `side.py` | beam faces outside the slab edge (scan #8) |
| `freeend.py` | free beam ends (scan #9) |
| `encl.py` | framed panels without slab (scan #10) |
| `audit.py` | short sketch edges per level (scan #6) |

Inputs:
- slab files `slab_<LEVEL>.txt`, in the format `R,<B|S|D>` / `L` / `x,y` lines / `O` / `x,y` lines, in mm from grid 1 / grid A;
- a beam export CSV: `id;mark;type;level;x0;y0;x1;y1;width;L|A`, one Revit call.

Project-specific constants are marked (paths, level names, joint x-range 67350–67950, the RSUD arc terrace, the `DEL`/`UPD`/`ADD` patches in `snapedge.py`). Replace them, or parameterise them, before reuse. Not yet run on another project, so treat all of them as [EXPERIMENTAL] outside RSUD.
