---
name: "architectural-drawings-to-revit"
description: "Turn architectural construction drawings (PDF plans, tampak, potongan, details, door/window schedules) into an accurate, organised Revit architectural model via the Revit MCP, with logging and QC."
---

# Architectural drawings -> Revit model

## Purpose, scope, activation
Use this skill when a construction-drawing set (vector PDFs) must become a Revit **architectural** model driven through the Revit MCP (`send_code_to_revit`): walls, windows, doors, facade cladding and niches, cornices, roofs, canopies, bridges, site/toposolid, and the linked-structure alignment that goes with them. It is distilled from the KPwBI DIY tender model (Gedung Utama, Gedung Penunjang, skybridge, site), Nov 2026, Revit 2026. For structural modelling use the structural skill; this one only covers reading the STR link.

The skill has seven parts. Parts A-E are method. F is the trial-and-error table. G is project facts. Each part separates **Proven here** (done and verified in KPwBI) from **General / untested** (standard practice we did not exercise).

| Consult | When |
|---|---|
| A Drawing interpretation | before modelling any package; when a sheet must be measured or calibrated |
| B Modelling workflow | while building each element type |
| C Documentation | naming, marks, comments, views, docs |
| D Automation | every MCP script; file staging; family building |
| E Quality control | after every package and at the end |
| F Trial-and-error | when something fails or before a known-risky operation |
| G KPwBI reference | when continuing this project (coordinates, levels, sheets, materials) |

## Critical principles (user's standing preferences; non-negotiable)
1. **The drawings are the source of truth.** If it is drawn, model it; if it is not drawn, don't. Model drawn offsets exactly as drawn (a wall drawn 45 mm off grid is 45 mm off grid). Do not invent design.
2. **Drawn but not dimensioned = model it with your best estimate; never leave it out.** Estimate in this order: (1) measure the calibrated vector geometry; (2) take it from a related sheet (elevation, section, 1:50 detail, schedule, structural drawing/STR link); (3) take it from adjacent or repeated elements; (4) last resort, judge proportions visually. Record source, method and confidence in the project doc, and write `LOW CONFIDENCE` (or LOW / MEDIUM) in the element's Comments. An element in the drawing but missing from the schedule is still modelled (LOW).
3. **Interpretations are not facts.** If you are naming what an element *is* (skylight, frame, louvre, niche) from shape or hatch alone, say so in the reply and the doc, and ask when it changes the build. (Lesson: the Utama roof top was modelled as a glazed skylight from a hatch; it was not one.)
4. **Ask before** resolving conflicts between drawings, before deleting or moving anything the user modelled, and before large or destructive batches. Give options with one recommended. The user answers fast. When the request is clear and safe, just do it.
5. **Native families and system types wherever they exist** (walls, floors, roofs, doors, windows, columns). DirectShape only when nothing editable fits (company convention also keeps foundations as DirectShape). The user twice asked to convert DirectShapes to editable elements; default to editable.
6. **Model the final renovated state.** Existing elements that stay + new work. No demolished items.
7. **Exterior first.** Outward appearance (facade, openings, roof, canopies, cornices) has priority; interior only where the user asked (Penunjang interior walls were wanted).
8. **Don't clean up the user's content** unless asked (their Generic walls and massing roof stay; modifying walls is allowed if it makes the model cleaner, and say so).
9. **Follow the STR link** for anything structural-adjacent (columns, canopy steel, trusses). Where architecture and STR differ, follow STR and write the difference in the doc.
10. **Walls whole, inserts cut.** Merge split collinear walls (same type/level/height, touching) when placing windows/doors; model the wall whole and let the family cut the opening; every insert must be verified to cut (Part E).
11. **Quota-minimal.** Small scripts (<= ~4k chars), batch independent calls, don't redo finished work ("focus on finishing it"), no narration between tool calls. First sentence of a task says what you are about to do. Finish each package with a short report: outcome + one next step + "please save the Revit model". Update the project doc.
12. **No "CLAUDE" in view, filter or element names.** Use neutral names such as `CHK <AREA> 3D`.
13. **Keep deferred things deferred** ("that's on the skybridge, it's for later"). When the user narrows scope ("no need to re-read, just change the materials"; "no need to model more door families"), do exactly that.
14. Match an established sibling system when the user points to it ("follow the Penunjang roof materials") instead of re-deriving.

## End-to-end workflow
1. **Orient.** Read the project's master doc and the area doc. Check open Revit documents and `document.Title` (the MCP writes to the *active* document). List what exists (levels, grids, walls, roofs, links, families) before proposing work.
2. **Understand the drawings before modelling.** Find sheets by title, read plan + elevation + section + 1:50 detail + schedule for the package, and the render if one exists. Decide what each element *is*. Ask once if genuinely ambiguous (offer options, recommend one).
3. **Set the sequence and dependencies** (Part B.0). Agree the package order with the user.
4. **Extract numbers.** Calibrate each sheet from its own grid lines; list items with coordinates, sizes, levels, source and confidence (a JSON/CSV in the workspace or on the user's PC).
5. **Build one package at a time** with small scripts: create types first, then instances, Regenerate, then dependent operations (flip, cut, paint).
6. **Verify each significant step**: persistence after commit, inserts cut, no new warnings, numbers vs drawing, and a 3D image check for visible work.
7. **Document**: update the project doc (what, where, marks, confidence, open items); short report; remind to save.
8. **Final validation**: overlay/compare against elevations and sections; warnings; duplicates; STR clashes (Part E).

Reliable methods beat clever ones: if a technique failed once here (void cuts, dynamic C#, giant scripts, per-wall cornice pieces), use the proven alternative in Part F rather than retrying it.

## Quality-control requirements (minimum per package)
- Every new element still exists in a **separate, later call** (Revit can delete elements at commit, e.g. "Can't make type").
- Every window/door/louvre appears in `host.FindInserts(true,true,true,true)` and the host volume dropped.
- Warnings count is not higher than before (or each new warning is explained).
- Visible geometry checked in an exported 3D image against the elevation/render.
- Marks + Comments (source, confidence) set; doc updated.

## Known limitations
- No network in the workspace and no pip/npm; only installed tools (pdftoppm, pdftotext, pdfplumber, PIL, PyMuPDF if present).
- Door placement on 100 mm Generic walls (Utama Lantai Dasar) fails with "Can't make type"; cause unresolved (Part F row 23).
- Stairs, railings, ceilings, rooms, floor finishes, curtain walls, sheets, tags, schedules and view templates were **not** done in these sessions; guidance for them below is untested.
- Element ids change when shapes are recreated; refer to marks.

---

# Part A - Drawing interpretation

## A.1 Proven here
**Finding sheets.** `pdftotext -f N -l N -layout file.pdf -` reads title blocks (sheet number and title are searchable). Text *inside* drawings is usually split into glyphs and not searchable: use `pdftotext -bbox` and pair a code word ("AW", "D") with the nearest number to locate tags. Build a page map per PDF part once and store it in the project doc.

**Sheet types and what each was used for**
- Plans (denah, 1:250-1:400 on A3): wall lines, openings, grid, levels, tags. Walls = pairs of parallel vector lines 0.9-4.6 pt apart (at 88.2 mm/pt); centre and thickness from the pair.
- Elevations (tampak): window/door x positions (overlay check), sill/head heights, bands, cornice line, finish legend (e.g. LM01 limestone, W1 paint, GR01 granite, GK01 tile), top levels.
- Sections (potongan): floor-to-floor, roof pitch per direction (pitches differed by direction on Penunjang: 34.9 deg vs 29.4 deg), fascia/eave heights, knee walls, depths of ledges and piers.
- 1:50 partial facade sheets (parsial fasad): niche step widths/depths, cornice profile steps (read at 300 dpi, about 2 mm/px).
- Schedules (Part4): window/door codes with W x H, sill, frame, glazing. Keyplans (Part3/Part4): where each code sits (tags D.., AW..). Keyplans are 1:400 with leaders; some leaders end ambiguously at window glyphs: treat those as doubtful and check against the elevation.
- Renders (user-supplied or "Gambar 3D"): design intent for niches, materials, which faces are stone vs paint. Used to correct misreadings (recessed niche, not projecting frame).
- Structural sheets / STR link: the alignment reference for canopy steel, columns, roof trusses and purlins.

**Calibration (critical).** Never use a single global scale or approximate grid positions. Read the vector grid lines with pdfplumber and map **piecewise grid-to-grid** per sheet; verify on every grid line before measuring. A 0.04 % scale error plus a 1 pt origin error shifted the roof 112 mm. Then verify against a known element (Penunjang: bubble-derived calibration was off x +11 / y -118 mm, found by checking columns). Cross-check scale with section level lines (e.g. 5500 between floors) and printed dimensions.
- Raster measuring: mm/px = 25.4 / dpi x scale (1:50 at 300 dpi = 4.23 mm/px; 1:100 at 250 dpi = 10.16; 1:400 at 600 dpi = 16.9).
- Some keyplan pages use nested transforms where pdfplumber coordinates were unreliable; render crops with mm rulers drawn on them (pdftoppm + PIL) and read positions visually instead.
- Vector fill paths (not raster tracing) give exact zone outlines for site paving; merge tiled fills by cancelling shared edges.

**Datums and levels.** Record FFL and SFL per level (SFL usually FFL-50; -100 at mezz/roof here). Note conflicts (Utama elevations show Lantai Dasar -3400, plans/sections -3300; -3300 used and noted). A building can have its own datum (Penunjang ground -1000 vs Utama -3300).

**Elevation overlay check.** Render the elevation at known dpi, derive px <-> x mm from two grid lines, draw ticks at the placed element positions, compare.

## A.2 General / untested here
- Wall-type (tipe dinding), finish (finishing lantai/dinding) and ceiling (plafond) plans were mapped but not used: they would give wall build-ups, finish thicknesses SFL->FFL and ceiling heights.
- Demolition sets (bongkaran) were mapped but never read; use them to decide existing-to-remain vs removed before modelling a renovation element.
- Standard details (railings, plafond, door/window criteria) were mapped, not used.

# Part B - Revit modelling workflow

## B.0 Sequence and dependencies (proven)
Levels/grids -> STR link check (or structure built in-file if no STR) -> walls (merge collinear) -> slabs/floors -> windows (families, then placement) -> facade cladding/niches (depends on window positions) -> cornice/bands (depends on wall + skin outline) -> roof (depends on wall top + STR trusses) -> canopies (depend on STR steel) -> doors (cut walls and skin) -> site/bridge -> audit. Window-dependent items must be regenerated if windows move.

## B.1 Linked structure (proven)
`RevitLinkInstance.GetLinkDocument()`, collect columns/framing/floors with `BoundingBoxIntersectsFilter` (Outline in feet). Place architecture on actual STR positions: canopy covers on grids G/J missed the real columns by 1000 mm; the canopy roof was rebuilt from the STR steel extents so steel no longer poked through. Check the link transform (identity at origin here).

## B.2 Walls (proven)
- User walls: Generic types, level to level, location line mixed (Finish Face Exterior / Centerline). Read `Wall.Orientation` = exterior side; check `Flipped`.
- Created walls: duplicate a type, one layer, named by material and thickness (`PJ LM01 200mm`, `KPW - Jembatan Dinding Limestone 250` with its own Type Mark). Base level = highest level at or below the bottom; base offset + unconnected height carry exact z. Set `WALL_HEIGHT_TYPE` only after Regenerate on a new wall.
- Joins: rings use default mitre joins; boxes/claddings disallow joins (`WallUtils.DisallowWallJoinAtEnd`). Before deleting joined walls: disallow joins and `JoinGeometryUtils.UnjoinGeometry`, else a modal "Can't keep elements joined" blocks the API.
- Overlap dialogs: new walls must sit exactly on the face of existing walls (1-4 mm overlaps raised dialogs; fixed by snapping to the exact face).
- Deleting a host wall deletes its inserts: capture data and re-place.

## B.3 Facade cladding, niches, cornices (proven)
- Stone skin: either (a) DirectShape boxes per exterior wall (category Walls, material LM01, mark `SKIN-...`), niches by **Boolean Difference on plain Solids before creating the DirectShape**; or (b) editable: stacked one-layer walls (e.g. 2 x 100 mm), each with a rectangular wall opening (`NewOpening`) for its niche step. (b) is what the user prefers for editability.
- Niche recipe (Utama): outer step = window cluster +200 each side, head +400, 100 proud; inner step +200, head +200, at the wall face. Penunjang: +300/+150(/+15), heads +450/+300(/+150). Windows within 350 mm merge into one cluster; stacked floors form one tall niche.
- Exterior wall detection: `ReferenceIntersector` rays from both sides in a 3D view; hit within 400 mm = blocked; exactly one free side = exterior. Unreliable where the plan is open (it failed for door facing) - then use the side the skin is on.
- Continuous profiles (cornice): ONE closed outline, each profile layer an extrusion with outer loop = outline offset outward by the layer projection, inner loop = offset inward (embedded); corners from intersections of adjacent offset lines (`CurveLoop.CreateViaOffset` or own mitre maths); outer CCW, inner CW; `GeometryCreationUtilities.CreateExtrusionGeometry`. Outline from: rasterise wall + skin footprints (20 mm grid), morphological closing (r 500 mm seals door gaps), flood fill from outside, plug open interior halls with hand-placed core rectangles, trace boundary, hand-clean jogs < 300 mm.
- DirectShape categories: Walls (cladding, cornice), Roofs (canopies), Columns (column covers), Generic Models (finials/ornament). Check `DirectShape.IsValidCategoryId`.
- Paint finish faces: `HostObjectUtils.GetSideFaces` -> `document.Paint(id, face, matId)`; pick faces by normal. DirectShape faces can be painted too.
- Slab edges showing inside niches: recreate the slab so its edge sits at the wall face.

## B.4 Windows (proven)
- One family per schedule code: built by script from `Metric Window.rft` (`NewFamilyDocument`, own Transaction, FamilyManager sets Width/Height/Default Sill), frame 50x100, glass on a Glass subcategory, fixed geometry, type name `<code> WxH`, file `JENDELA_<code>.rfa`. **Must contain an Opening cut** (`fd.FamilyCreate.NewOpening(wall, curveArray)` rectangle over the frame extents); reopen the file and count Opening elements.
- Wide openings (> ~4 m) in Metric Window.rft: first extend the template host wall (LocationCurve to +/-6 m, height 4 m) and Regenerate, THEN set Width/Height, else "Can't make cut-out" dialogs drop the cut.
- Max 2 families per call. To reload: delete the Family element (no instances) then LoadFamily (it does not overwrite).
- Placement: `NewFamilyInstance(pt, symbol, wall, level, NonStructural)`, set `INSTANCE_SILL_HEIGHT_PARAM`, Regenerate, THEN `flipFacing()` if `FacingOrientation . wall.Orientation < 0`, Regenerate. Never load/reload families and place in the same call. First placement after a load sometimes fails: delete and re-place. A window running into a wall end fails.
- Built-as-drawn codes (not in the schedule) get their own families, marked LOW.
- Bridge window with stepped niche voids inside the family (`KPW_AW-29 Window Niche.rfa`) worked for a repeated module.

## B.5 Doors (proven, with an open problem)
- User wanted doors placed accurately with roughly right sizes using **existing families**: duplicate stock symbols (`M_Door-Passage-Single-Flush`, `-Double-Flush`, `-Single-Vision_Lite`) per schedule code, set `DOOR_WIDTH`/`DOOR_HEIGHT`, name `<code> - <desc> WxH`. Panels/transoms/sidelights not modelled (note it).
- Placement from keyplan points: snap to the nearest wall within ~900 mm whose bbox spans the level, clamp the point along the wall so the leaf fits (half width + 200 mm from ends). Mark `DR-<code>-<lvl>-<nn>`.
- Doors cut only after `flipFacing` + Regenerate (same as windows). Verify FindInserts.
- Check overlap with existing windows along the same wall before placing; drop doubtful tags (4 removed) and list them.
- Doors in walls covered by a DirectShape skin: cut the skin too (Boolean Difference of a box tool on the skin Solid, recreate the DirectShape, keep mark/comment). Per-door try/catch; Regenerate and re-collect between cuts on the same wall; perturb tool dims by ~1 mm to avoid coincident faces at wall ends.
- **Open:** on 100 mm Generic walls (Lantai Dasar) every door type vanished at commit with "Can't make type" (Masonry Frame Depth 150/100/80 tried). Same families worked on 150/250/300 walls and a storefront. Test one instance and check it in the next call before any batch.

## B.6 Floors / slabs (proven parts)
- `Floor.Create(doc, List<CurveLoop>, typeId, levelId)` then `FLOOR_HEIGHTABOVELEVEL_PARAM`; to change an outline, delete and recreate (no hosted elements). Structural slab tops at SFL (FFL-50). Avoid creating temporary overlaps (modal "floors overlap").
- Ramp floor: sloped floor (15.3 %) / bridge floor ramp +7800 -> +6900.
- General/untested: finish floors SFL->FFL per finishing plans.

## B.7 Roofs (proven)
- `NewFootPrintRoof(CurveArray, level, roofType, out ModelCurveArray)`; inner loop = opening. `set_DefinesSlope` + `set_SlopeAngle(curve, rise/run)` (NOT radians). Assign slopes by curve coordinates, not index (GetProfiles order differs). Sketch plane = underside; thickness added upward (vertical t/cos). Regenerate before reading bboxes; probe heights with a downward `ReferenceIntersector`.
- Follow the truss geometry from the STR log/link: eave tip, ridge, slope per face (Utama main 0.4833 rise/run, purlin top = roof underside).
- Flat top on a hip (Penunjang system): Cutoff Level at TOP ATAP minus (thickness/cos correction; 356 mm there) leaves an opening exactly at the deck lines; fill with a 200 mm concrete deck at TOP ATAP, a 150x200 coping ring (W1), finials on the deck.
- Roof type: duplicate an existing RoofType, set layer width/material via CompoundStructure. When swapping a roof's type to a different thickness, adjust the base offset by the thickness difference to keep the top surface.
- User wants roofs editable: rebuild DirectShape roof parts as FootPrintRoofs.

## B.8 Canopies, columns covers, bridge, site (proven)
- Canopy: body/glass as DirectShapes in Roofs sized to STR steel (soffit under steel bottom, deck over steel top, overhang chamfers), skylight cut through deck and soffit snapped to purlins. Covers in Columns centred on STR columns.
- Bridge: own wall/fascia/soffit/column types with distinct Type Marks (fixes duplicate-mark warning), stone surface pattern as model pattern, windows chained from the dimension chains.
- Site: site coordinates = Utama internal; linked Penunjang at offset + rotation -3.48 deg. Toposolids sharing an edge are flagged overlapping: keep a 20 mm joint. Subdivisions inherit their type's thickness: use 20 mm "SUB" types with Sub-divide Offset 20. `Toposolid.Split` also splits disconnected parts into new toposolids. Snap near-axis edges (< 0.5 deg) to the axis. Use SlabShapeEditor for level changes.
- General/untested: stairs, railings, ceilings, rooms, curtain walls (only user M_Storefront walls exist).

# Part C - Documentation
## C.1 Proven here
- **Marks** (`ALL_MODEL_MARK`) with readable schemes: `W-<lvl>-nnn`, `K-<lvl>-nn`, `S-<lvl>-nn`, `W-AW-xx-<lvl>-nn`, `DR-<code>-<lvl>-nn`, `SKIN-...`, `CORNICE-RING`, `R-AT-01`, `ROOF-TILE-TOP`, `JB-...`. Refer to marks in docs (ids change).
- **Comments** (`ALL_MODEL_INSTANCE_COMMENTS`): category tag + source sheet + confidence (e.g. "FACADE-CORNICE closed ring ... LOW").
- Material names with spec code: `LM01 - Limestone ...`, `GK01 - Genteng Keramik`, `W1 - Cat Exterior Water Based (Grey)`, `GR01 - Granit Grey (Graphite) 20mm`, `TG02 - Laminated Glass Clear`, `AL01 - Aluminium Solid Panel Grey`.
- Type names: code + description + size (`AW-04 1800x3500`, `D42 - Bulletproof double 1900x3000`, `GK01 - Atap Genteng Keramik 120mm`). Keep Indonesian names where the project uses them.
- Check views: duplicate a 3D view (`CHK PENUNJANG 3D`, `CHK SITE 3D`, `CHK JEMBATAN PERSP`), crop box not section box, hide levels/grids. A colour filter "Comments contains LOW CONFIDENCE" exists in STR (badly named with CLAUDE; rename).
- STR inspection views were renamed at user request to `0n <LEVEL> - Denah struktur` / `0n <LEVEL> - 3D`.
- Project docs: one master state doc + one doc per area; edit by `project_read` -> change -> `project_write` full content (`local_path` writes need the doc's full current text read in the same conversation). Later date wins on conflicts; mark superseded statements explicitly.
## C.2 Gaps (not done)
Sheets, tags, schedules, view templates, dimensioning, room naming. If asked, plan them from scratch; no session experience to reuse.

# Part D - Automation (Revit MCP and the PC bridge)
## D.1 Proven here
- `send_code_to_revit`: body of Execute, `document` in scope, a transaction already open, return a string. Limit ~80 s. Keep scripts <= ~4k chars (a 9k script timed out three times; split in three ran in < 1 s). Typed C# only (a `dynamic` version timed out).
- Errors arrive in Chinese: "执行失败: Exception has been thrown by the target of an invocation" = runtime exception (wrap risky parts in try/catch and return the message); "代码编译错误" = compile error with line number; "代码执行超时" = timeout.
- Transaction semantics: a throwing call rolls back everything; a call that catches and returns commits the steps before the failure; a timed-out call may still have completed - query state before retrying. Revit may **delete elements at commit** (user sees a dialog such as "Can't make type") although the script returned OK: verify in the next call.
- Responses can come back out of step (a reply carried the previous call's result): re-query state when a result looks wrong.
- Compiler quirks: avoid `?.` chains and null `.AsString()`; `int[]` literals sometimes fail (use double[]/long[]); Revit 2026 uses `ElementId.Value` (no IntegerValue) and `new ElementId(long)`; some BuiltInParameters don't exist in 2026 (guard); no `WallType.CrossSection`.
- Persist between calls: `AppDomain.CurrentDomain.SetData/GetData` (lives while Revit stays open). Cache computed geometry/types there.
- Create types in one call, set parameters in the next, swap/place in a third when stability matters.
- Families: `EditFamily` fails inside the tool transaction; use `Application.OpenDocumentFile` / `NewFamilyDocument` + own Transaction, SaveAs, Close; delete `.0001.rfa` backups.
- Several documents open: the MCP acts on the **active** one. Check `document.Title` before writing; ask the user to switch windows if needed. `document.Application.Documents` lists open/linked docs.
- **Never call `say_hello`** (modal dialog blocks the API). Avoid operations that raise modal warnings; they look like timeouts.
- Other MCP tools used: `get_selected_elements` (find what the user selected).
- **Bridge to the PC:** connected folders via `get_device_info`; `device_list_dir`; `device_stage_files` copies PC files to `/mnt/user-data/uploads/<folder>/<relpath>` (a new chat needs re-staging). Request folder access only when needed (the user declined one unneeded request). C# can write results/images to a PC folder (`...\_chk\`) which are then staged - faster than returning big strings.
- Visual check: duplicate a 3D view, disable section box, `ViewOrientation3D(eye, up, forward)` with up perpendicular to forward, `ImageExportOptions` (PixelSize 4000, FitToPage), stage the image, crop with PIL.
- Workspace PDF tools: pdfinfo, pdftotext (-layout/-raw/-bbox), pdftoppm (-r, -x/-y/-W/-H crops), pdfplumber (vectors; it kept 0.24 pt lines that an SVG route dropped).

# Part E - Quality control
## E.1 Proven here
- Per package: persistence check (separate call), FindInserts + host volume drop, warnings delta, 3D image vs elevation/render, numbers vs drawing (bbox z of roofs vs eave/ridge levels).
- Calibration check on every grid line; re-check against a known element.
- Elevation overlay for window/door x positions.
- Clash-style checks by bbox overlap (doors vs windows on the same wall; pier pieces vs walls; fascia vs skin) and by Boolean subtraction of overlaps.
- Look *behind* what you model: piers stopped at +5.9 exposed the column; extend to the slab underside.
- Beam families flexing one face only made beams sit off their location line: set `Y_JUSTIFICATION = Center` on every beam (STR) - check eccentricity before trusting STR geometry; intentional drawn eccentricities stay (record them).
- Duplicate Type Mark warnings: give new types their own marks.
- Final audit list: warnings, duplicates (copied STR slabs in ARS), clashes with the STR link, unhosted/uncut inserts, LOW items list.
## E.2 Common mistakes seen
Modelling from a hatch/outline without a label; placing on grids instead of real STR positions; flipping before Regenerate; loading and placing in one call; trusting a returned "OK" without re-checking; editing the wrong open document; naming views with CLAUDE.

# Part F - Trial-and-error knowledge base

| # | Problem | Initial approach | What went wrong | Successful solution | Lesson |
|---|---|---|---|---|---|
| 1 | Recessed facade niches | Void cuts: non-hosted generic voids, wall-based voids, SolidSolidCutUtils on DirectShape | None cut reliably | Additive skin: per-wall DirectShape boxes with niches made by Boolean Difference on the Solid before DirectShape; later stacked walls with NewOpening per step | Build additively; booleans on plain Solids work, voids on DirectShapes don't |
| 2 | Windows sit in the wall uncut | Family without opening geometry | No cut, "Can't make cut-out" | Add `NewOpening` rectangle in the family; reopen and count Openings; verify FindInserts | Every window family needs an Opening cut |
| 3 | Louvres hosted but uncut | Placed in the same call as family delete/reload, flipped before Regenerate | FindInserts = 0 | Delete and re-place: place, sill, Regenerate, flip if needed, Regenerate | Never load and place in one call; flip after Regenerate |
| 4 | Window wider than ~4 m | Set Width/Height on Metric Window.rft | Modal "Can't make cut-out", cut lost | Extend template host wall to +/-6 m, height 4 m, Regenerate, then set size | Make the host bigger first |
| 5 | Script timeouts | One 9k-char script with local functions | 3 timeouts, nothing committed | Split into ~4k scripts | Keep scripts small |
| 6 | Slow geometry build | `dynamic` C# | Timeout | Typed C# + AppDomain cache (44 ms) | Typed only |
| 7 | API "hangs" | say_hello; deleting joined walls; overlapping floors/walls | Modal dialogs block the API | Never say_hello; unjoin/disallow joins before delete; order operations to avoid overlap | Treat a sudden timeout as a possible dialog; ask the user to check Revit |
| 8 | Wrong roof slopes | Slopes by curve index; angle in radians | Wrong faces sloped | Assign by curve coordinates; set_SlopeAngle takes rise/run | Match curves by geometry |
| 9 | Roof too high | Sketch at eave top | Thickness added upward | Offset base by t/cos; Regenerate and read bbox | Sketch plane = underside |
| 10 | Utama roof top identity | Read a long hipped rectangle with blue hatch as a glazed skylight | User: not a skylight; no label existed | Swapped to GK01 tile type (offset -115 to keep top), matched Penunjang materials; planned flat deck | Say when an identity is inferred; ask |
| 11 | Canopy column covers | Placed on grids G..J | Outer two missed real columns by 1000 mm | Read column centres from the STR link | Align to STR, not grids |
| 12 | Canopy roof vs steel | Drawn section dims | Steel poked through | Rebuilt from STR steel extents (soffit under bottom, deck over top) | Follow STR where it differs, note it |
| 13 | Blotchy cornice, corners not meeting | 45 per-wall shapes with neighbour-detected mitres | Didn't follow the true perimeter | One closed outline, offset-line mitres, layered extrusions, one DirectShape | Continuous profiles = one closed ring |
| 14 | Cornice outline leaking inward | Wall-only footprint, small closing | Open halls and door gaps broke the loop | Include skin footprints, closing r=500, plug halls with core rectangles, trace, hand-clean jogs | Seal gaps deliberately; check single loop |
| 15 | Roof/beam 112 mm off | Global scale 105.88 mm/pt and approx grid origin | Systematic shift | Piecewise grid-to-grid calibration from vector grid lines | Calibrate per sheet on all grids |
| 16 | Penunjang plan offsets | Calibration from grid-bubble text | x +11 / y -118 mm error | Corrected against column positions | Verify calibration on a known element |
| 17 | Beams off their line (STR) | Family with Origin justification | One face flexed: up to 300 mm offset | Y_JUSTIFICATION = Center on all beams | Check family behaviour before trusting geometry |
| 18 | Door facing / exterior side | Raycast from both sides | Unreliable on open sides | Use the side the skin DirectShape is on | Use model facts over rays where open |
| 19 | Doors not cutting | Placed only | FindInserts 0 | flipFacing + Regenerate | Same rule as windows |
| 20 | Skin not opened at doors | Doors cut only the wall | Skin covered the doorway | Boolean Difference on skin Solid, recreate DS | Cut every layer in front of an insert |
| 21 | Skin cut batch failed | All cuts in one block | First failure rolled back the call; coincident faces at ends; null bbox after recreate | Per-door try/catch, perturb tool by ~1 mm, Regenerate and re-collect | Make batches fault-tolerant |
| 22 | Doors clashing with windows | Trusted keyplan leaders | Some leaders ended at window glyphs | Overlap check along the wall; deleted 4 doubtful doors and listed them | Check overlaps before placing |
| 23 | LD doors vanish | Placed on 100 mm Generic walls; frame depth 150->100->80 | Revit deleted them at commit, "Can't make type"; script said OK | Unresolved; same types work on 150+ walls | Verify persistence in a later call; test one before batching |
| 24 | Keyplan positions | pdfplumber coordinates | Nested transforms gave wrong positions | Raster crops with mm rulers | Validate extracted coordinates visually |
| 25 | Tags not found | pdftotext search | Glyphs split | `-bbox` + nearest number | Use bbox pairing |
| 26 | Penunjang facade | Projecting window surrounds, thin 300 fascia, 30 mm column cladding | User render showed recessed niches and deeper granite | Deleted and rebuilt from render + section + plan | Study the element's nature before modelling |
| 27 | Penunjang west band height | Read from L2 FFL | User corrected to +5.90..+7.22 | Rebuilt to user values | Apply user corrections exactly; record them |
| 28 | Grey band inside niches | Slab edge beyond wall face | Visible slab edge | Recreate slab to the wall face | Check slab edges at facades |
| 29 | Columns exposed under fascia | Piers stopped at +5.9 | 700 mm of column visible | Piers to slab underside, columns subtracted | Check what is behind/below |
| 30 | Toposolid overlaps | Shared edges; subdivisions on 1000 mm types | Overlap flags, 1 m slabs z-fighting | 20 mm joints; 20 mm SUB types with offset 20 | Subdivisions inherit thickness |
| 31 | Overlap dialogs during wall conversion | New walls 1-4 mm into hosts | Modal dialogs | Snap new walls to exact faces | Exact faces, no tiny overlaps |
| 32 | Wrong document edited | Assumed the active doc | Penunjang active while working on Utama | Check `document.Title` every write; ask user to switch | Check title first |
| 33 | Family update not taking | LoadFamily over existing | Not overwritten | Delete Family element, then load | Delete before reload |
| 34 | Doc write refused | project_write with local_path | Doc text not read this conversation | project_read first, then write full content | Read before write |
| 35 | View naming | "CLAUDE - FACADE CHECK" | User dislikes CLAUDE | Neutral `CHK ...` names | No CLAUDE in names |
| 36 | Out-of-step tool replies | Trusted the reply | A reply carried the prior call's result | Re-query state | Recheck surprising results |

# Part G - KPwBI DIY reference (session-specific facts)
- Paths: PC `E:\TENDER 2026\KPWBI BI DIY\` = `D:\Outpost\ADHI Karya\KPWBI BI DIY\` (same content). Drawings `DOKUMEN TENDER\Gbr_Arsitektur_DKU DIY_Part1..4.pdf`; Revit `REVIT\` (ARS_GED.UTAMA, STR_GED. UTAMA linked, ARS/STR_GED. PENUNJANG, SITEPLAN); families `REVIT\FAMILIES\Jendela\JENDELA_<code>.rfa`; check images `_chk\` (deletable).
- Utama coordinates: x mm east of grid A, y mm south of row 1'; Revit X = x - 217837, Y = 172339 - y (mm). Grids A 0 ... P 97200 (7200 modules, G 37800, K 61200); rows 1' 0, 1 2400, 1A 9000, 2 13200, 2A 18000, 3 24000, 3A 26400.
- Utama levels: LANTAI DASAR -3300, LD TIMUR -1900, MUKA TANAH 0, DROP OFF +1450, L1 +2300, L2 +7800, MEZZ +11650, ATAP +12550, TOP ATAP +20000.
- Penunjang: Revit X = -202554 + x, Y = 199659 - y (1.1 = north row); levels LD -1000, L1 +2700, L2 +6900, L3 +10500, ATAP +14500, DAK ATAP +17300, TOP +20000. Never link origin-to-origin with Utama (site: offset 84701, -4002, rotation -3.48 deg).
- Sheet map: Part1 p49-57 Utama plans/tampak/potongan (1:400), p58-63 Penunjang; Part2 finishes/wall types/ceilings, stairs A-5001..5122, canopies A-5501..5504, skybridge A-5401..5406; Part3 facade parts A-6001..6026 (1:50), standard details A-7001..7025, keyplans pintu A-8001..8006, jendela A-8007..8010; Part4 schedules pintu A-8101..8110, jendela A-8111..8126.
- Materials: LM01 limestone (232,226,210), GK01 tile (140,62,40), W1 grey paint (176,178,180), GR01 granite, TG02 glass, AL01 aluminium.
- Roof system (Penunjang, to follow on Utama): GK01 hip, cutoff, 200 concrete deck at TOP ATAP, W1 coping 150x200, grey mustaka finials, W1 fascia ring at eave, knee walls.
- Project docs: start with `claude/00-project-state-and-knowledge.md`, then the area doc.