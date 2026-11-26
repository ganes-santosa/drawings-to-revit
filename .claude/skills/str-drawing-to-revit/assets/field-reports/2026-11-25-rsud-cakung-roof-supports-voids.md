# Lessons for the structural-drawings-to-revit skill: steel roof frames, roof-support logic, continuous voids

_From: the structure chat, Tender RSUD Cakung (Revit 2026, mcp-server-for-revit), sessions on 2026-11-24 and 2026-11-25._
_For: the agent improving `structural-drawings-to-revit` at github.com/ganes-santosa/drawings-to-revit._
_How to use it: each lesson gives the incident (what went wrong), the rule (what to add to the skill), and where it belongs. Part numbers refer to the current SKILL.md layout. Everything below was tested in this session unless it is marked [untested]._

---

## A. Steel roof frame modelling (add to Part 3.5 Steel and Part 5 Troubleshooting)

### A1. Sloped and arched members: place them as `StructuralType.Beam`, never Brace
- **Incident:** 32 wind-bracing rods (ikatan angin D16) placed with `StructuralType.Brace` had their end points moved by up to 15 m. Revit re-attached the brace ends to nearby members.
- **Rule:** place every steel member as `StructuralType.Beam`, including bracing, knee braces, rods and sloped rafters. Do this even for elements that are braces by function. Read the end points back after placing (`LocationCurve.Curve.GetEndPoint`) and report the deviation. Target: 0.0 mm. Expect harmless "slightly off axis" warnings on skewed rods and accept them.
- This extends the existing knee-brace note in 3.3 ("Brace type snapped its top to the beam centreline") into a general rule for all steel.

### A2. Arc members: Revit can flatten them, so use straight pieces between supports
- **Incident:** trekstang (sag rods) drawn as arcs following an arched roof were created as arc beams. Revit flattened all 12 into horizontal lines at one z.
- **Rule:** for anything other than the main arched rafter, model the arc as straight segments between the members it physically connects. Sag rods go from one purlin to the next, at purlin mid-depth: 17 rods per line, 204 in total. For the arched rafter itself, one arc beam per frame worked, but verify its z after creation.

### A3. Setting `LocationCurve.Curve` resets the end offsets
- **Incident:** re-curving beams set their start and end offsets back to 0, so tops dropped 50 mm and some dropped a whole storey.
- **Rule:** after any curve edit, write `STRUCTURAL_BEAM_END0_ELEVATION` / `END1_ELEVATION` (or the z-offset params) back, then read them back to confirm.

### A4. Arched roof geometry: derive one circle from the section, then put each member on its own radius
Method that worked (Roof Utama, rooftop):
1. From the section vectors, read the circle centre (at the ridge grid, below the slab) and the top-of-steel radius. Check it against the dimensioned apex and eave heights.
2. Derive concentric radii from that one circle:
   - rafter centreline = R_top − d/2;
   - rafter soffit = R_top − d;
   - purlin mid-depth = R_top + purlin depth/2;
   - bracing nodes = rafter centreline (or as detailed).
3. Purlins go on the rafter top with the web normal to the roof surface. Space them by arc length, equal division from the ridge to the eave.
4. Watch out for developed drawings: the plan can draw purlins at developed (true arc-length) spacing and beyond the eave. Use the section for geometry and log the plan difference as a question.
5. Ridge and eave members: set the top flush with the rafter top or just under the rafter soffit, as the detail shows. Tag LOW CONFIDENCE if the detail is schematic.

### A5. Mono-pitch roof frames
- Read the slope from the section vectors, not the label: it was 10.0°, measured.
- Rafter positions along the roof come from the plan's rafter rectangles. Each post height comes from the section dimension measured from the beam top to the rafter top.
- High posts, low stubs and middle posts each sit on a named concrete beam. Record which one in Comments.

### A6. Families when the project has no steel content
- The project and the library on this PC had no steel content. Real families were built from the installed Metric templates (Structural Framing / Structural Column), one fixed size each. The ends are locked to Member Left/Right for framing, or Lower/Upper Ref Level for columns.
- Material: one project steel material from the spec (here BJ-37 / ST-37, fy 240 MPa), with the source in its identity data.
- Group: one model group per roof (`RANGKA ATAP UTAMA (E-G/4-7)` 299 members, `RANGKA ATAP AULA` 92). Marks are `RA-U-*` and `RA-A-*`, with a type code for rods: `RA-U-TS-LL-SS` = sag rod, line LL, segment SS.
- [general] When a group must be rebuilt, delete the members, recreate them, then call `NewGroup` again. Moving or changing a group brings up a modal warning (see D1).

### A7. What to log as not modelled (LOD 500 gap)
Haunches (cut WF), end plates, splice plates, base plates and anchors, bolts, gutter brackets. List them per roof in the package doc with their detail sheet and page, so a later LOD 500 pass can pick them up.

---

## B. Roof-frame building logic: what supports the roof (add to Part 2 as a new subsection, and to the Part 6 QC checklist)

### B1. The roof sections govern the column plan under a steel roof
- **Incident:** the Lantai 5–6 column plan drew 600×600 concrete columns at the aula roof grid lines. The roof sections and details showed steel WF posts standing on concrete beams at +17.95 in the same places. Modelled as drawn on the column plan, the concrete columns pierced the roof by up to 3.3 m.
- **Rule:** where a steel roof sits on a storey, check the column plan for that storey against the roof sections and connection details. If the sections show steel posts or stubs on a beam, the concrete column stops at the beam below and the steel post carries on. Never let a column rise through a roof. Log the conflict, and ask if it is not clear.

### B2. Every vertical member must carry something, and every roof edge must land on something
Run both checks after any roof is modelled:
- **Top check (columns carrying nothing):** for each column stack, test whether anything frames into its top: a beam, a slab, a roof post base, or the next column. If nothing does, it is suspect.
  - **Incident:** 30+ columns were drawn on the STR column plans with nothing on top.
  - **Resolution:** cross-check each one with the architectural plans, sections and elevations. Either a roof or room exists there that STR forgot (model the roof: see B3), or the column is a drafting leftover.
  - **User's final rule:** if a column is drawn on STR but carries nothing, keep it in the model, tag it, and put it in a hidden model group (`KOLOM TERGAMBAR TANPA BEBAN`, hidden in every view). Exclude that group from quantities unless it is confirmed. Don't delete drawn elements outright.
- **Bottom check (roof edges without support):** check every roof edge or rafter end for a post, column or beam under it.
  - **Incident:** the user spotted that the aula roof's south edge had no vertical member.
  - **Resolution:** the column plans for both storeys drew a KT1 at that spot, but it was missing from the column schedule. It was added: concrete KT1 up to Lantai 5, and a steel WF400 post from there to the rafter, following the same pattern as the matching grid line.
  - **Rule:** look for the pattern on parallel grid lines, and check every column plan for a label, even one missing from the schedule.
- **Free beams:** a beam that a column plan or section does not place under the roof must not be invented. **Incident:** a B7 beam had been placed along two purlin lines. It belonged on the grid-10 column line, where the sections centre it, and the posts stand on it.

### B3. Rooms with no roof: the dak rule and the "missing support" tag
- **Rule from this project:** a dak (roof slab with waterproofing) is any slab area not covered by the level above.
- When the ARS drawings show a room and the STR drawings show its columns but no roof slab, add the slab. Type it as dak and add the edge beams that STR does draw.
- **User rule:** beams that STR does not draw are left out. The slab gets the comment `MISSING SUPPORT … RFI` listing the beams it needs. Then re-type the slabs now covered by the new roof from dak to normal slab, since only exposed slabs get waterproofing.

### B4. Order of checks before calling a roof done (add to Part 6)
1. Every post base sits on a modelled beam or column top. Record the base level and offset, including plate and grout thickness from the base detail (here +26.00 = 25.95 top of concrete + 25 + 25).
2. Every post top reaches the rafter centreline.
3. No concrete column passes through any roof member. Test with a bounding box against the roof group.
4. Every roof edge and rafter end has a vertical support or a beam under it.
5. Every column top carries something; otherwise put it in the hidden group or ask.
6. Bracing end points are read back (deviation 0).
7. Group member counts are recorded in the package doc.

---

## C. Continuous voids through several floors (add to Part 3.4 Slabs, as a new "Shafts" item)

### C1. The problem
Slab voids for lifts, stairs and ducts had been modelled level by level. Each level had a 280 mm shaft opening (400 mm at the ground floor), and the same void was also drawn as a hole in the slab sketch. The result was 59 shaft openings plus 184 sketch holes, 51 of them duplicates of each other. The user wants one continuous shaft per vertical void.

### C2. Method that worked
1. **Export every void** to a file with a Revit script. Writing straight to the project folder with `File.WriteAllText` works. For each void, record:
   - source: a shaft opening (`Opening` in category Shaft Openings, `BoundaryCurves`), or a slab sketch inner loop (`Sketch.Profile`, every loop except the outer one, which has the largest bbox area);
   - level elevation;
   - the tessellated outline in plan mm.
2. **Analyse in Python** in the workspace (shapely was not installed, so bounding boxes were used):
   - Pair each shaft with the sketch hole on the same level when they overlap by more than 50 %.
   - Cluster voids level by level, using IoU ≥ 0.75 with the void on the next level down.
   - Within a cluster, keep the longest contiguous run of levels where every level is within a tolerance of the run's median bbox.
3. **Ask the user for the tolerance, with numbers.** The same void differed 30–520 mm between levels, because each level was traced from its own plan. The options given were ≤100, ≤250 (recommended) and ≤520 mm, each with its shaft count and how far edges would move. The user chose 250 mm.
4. **Create one shaft per run:**
   - `document.Create.NewOpening(bottomLevel, topLevel, curveArray)`, using the median rectangle;
   - base = lowest void level, with `WALL_BASE_OFFSET` −280 (−400 at the ground floor);
   - top = highest void level, with `WALL_TOP_OFFSET` 0.
   Then delete the per-level shafts in that run.
5. **Verify, three ways:**
   - **Beams aren't cut:** compare framing volumes (`HOST_VOLUME_COMPUTED`) before and after one test shaft. Shaft openings did not cut structural framing. Test this before the batch.
   - **Only voided slabs are cut:** test the slabs whose bbox overlaps the shaft. Use the slab's sketch, not its geometry: points at the centre and at the four corners 150 mm in, tested against the outer and inner loops (even-odd rule). `ElementIntersectsSolidFilter` against the slab is circular here, because a slab already cut by the shaft never intersects it.
   - **The sketch test caught a real error:** at one level, the hole in the main slab was filled by a separate roof slab (an atrium roof at that level, open above). The shaft had to start one level higher. Rule: a hole in one slab does not mean the level is open; check every slab at that level.
6. **Record:** shaft openings have **no Mark or Comments** parameters in Revit. Keep a table in the package doc: mark, element ID, levels, x/y range, how many per-level shafts it replaced, maximum deviation, and LOW CONFIDENCE where the deviation is over 100 mm.

### C3. Holes in the slab sketches: the transaction limitation
- The MCP template always has a transaction open (`document.IsModifiable == true`). That means `SketchEditScope` cannot start, so a slab's sketch holes cannot be removed from a script.
- The only route is to rebuild the slab: `Floor.Create` with the remaining loops, then copy type, level, offset, Mark and Comments, and re-join every beam. The slabs here had 18–308 geometry joins each. The user declined this as too invasive and kept the sketch holes.
- So the skill should say: **model new vertical voids as shafts from the start, not as sketch holes.** Use one shaft per vertical run, and keep slab sketches to their outer outline, plus holes only for voids on a single level. Doing that up front avoids the cleanup entirely.
- With sketch holes kept, only merge stacks that already have shaft openings. Adding a shaft over voids that exist only as sketch holes adds elements without removing any.

### C4. Split runs are expected
When one level of a stair void is drawn 500 mm off, the stack splits (here the west stair became Lantai 2–4 and Lantai 6–Rooftop). Don't force it into one run beyond the agreed tolerance. List the split levels in the doc so the user can confirm or correct the drawing.

---

## D. Other lessons from these sessions (Part 3.7 MCP mechanics and Part 5)

1. **A modal warning looks exactly like a timeout.** "Highlighted floors overlap", moving a group, and similar warnings block the API, so the script call times out. When a call times out, first ask the user to close any Revit dialog. Then **re-query what was actually committed** before retrying, because part of the work may already exist (here 32 of 32 rods existed after the "timeout").
2. **Avoid overlap warnings by construction:** create a new slab so its outline never overlaps a neighbour, even briefly, or delete the old one first in the same call.
3. **Bulk end-point moves catch innocent members.** Moving beams onto column centrelines and then shifting "all beam ends at the old point" also moved 12 unrelated girder ends. Rule: select the ends to move explicitly, by element ID and end index, and exclude ends that sit at a column centre. Read back afterwards.
4. **Tagging by type over-applies.** Tagging "all S5 beams LOW" hit 33 beams when only 1 was meant. Tag by element, not by type, unless the user says type.
5. **Bounding-box claims need a geometry check before you tell the user.** One statement ("the Lantai 3 slab passes over row H") came from a bbox and was wrong. Confirm with the sketch outline or a point test before using it in a question.
6. **Deleting and then reusing an element in the same script** throws an exception. Split the work into two calls and re-query by Mark.
7. **Compile quirks in Revit 2026:**
   - `ElementId.Value` (long) works and `IntegerValue` fails;
   - `new ElementId(long)`;
   - only `double[]` literals are safe;
   - `Element` has no `SketchId`, so cast to `Floor` first;
   - `Document.HasOpenTransaction` does not exist, so use `IsModifiable`.
8. **Lift pits:** pile caps under a lift pit go to the pit underside (here −1900), not the general cap level. Lower the piles with them and extend the columns down. The user called it "general building logic", although the plans didn't say so.
9. **Recovery after a crash or power outage:** check what the reopened file contains against the package docs, element by element (counts, marks, tags, group sizes, warnings). Then re-apply only the missing decision blocks and compare with the last audit's counts. This works only if the docs record element IDs, marks and counts after every block, so keep doing that.
10. **Cross-discipline rule the user set:** where ARS and STR differ, the model follows STR. Elements that STR does not draw are not invented; the element they should connect to gets an RFI tag instead.
11. **Point the user to documents and pages.** For every open question, give the sheet code and the PDF page (for example "S-11 p25 vs S-34 p48"). The user asked for this explicitly, and it speeds up their decisions.
