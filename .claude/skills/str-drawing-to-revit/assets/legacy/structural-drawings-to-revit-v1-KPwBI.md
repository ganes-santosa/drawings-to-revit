---
name: "structural-drawings-to-revit"
description: "Turn structural construction drawings (PDF plans, sections, details, schedules) into an accurate, organised Revit structural model via the Revit MCP / API, with logging and QC."
---

# Structural drawings to Revit

Use this skill when a task asks for a Revit structural model to be built from, or checked against, structural drawings. Typical inputs are columns, beams, slabs, foundations, steel roof trusses, canopies and retrofit or jacketing work. It applies most directly when Claude edits Revit through the `mcp-server-for-revit` tools (`send_code_to_revit`) and reads PDF drawing sets in a Linux workspace.

Almost all of this knowledge comes from one real project: the renovation of KPwBI DIY Gedung Utama. That job was a 120-page structural DED and a Revit 2026 model with about 840 framing members, 66 floors, 52 pile caps, a steel roof truss system and a portico canopy. Items marked **[general]** are standard practice and did not come out of that session.

The skill has five parts, all in this file. The headings match the planned reference files:
- Part 1: working principles and workflow (SKILL core)
- Part 2: drawing interpretation (`references/drawing-interpretation.md`)
- Part 3: modelling workflow and Revit / MCP techniques (`references/modeling-workflow.md`)
- Part 4: documentation and views (`references/documentation-standards.md`)
- Part 5: troubleshooting knowledge base and session lessons (`references/troubleshooting.md`, `references/session-lessons.md`)
- Part 6: quality control checklist

Read Parts 2 and 3 before modelling. Read Part 5 whenever something fails or looks odd. Run Part 6 before calling any discipline or level done.

---

## PART 1. Working principles and end-to-end workflow

### 1.1 Non-negotiable principles
1. **The drawings are the source of truth.** If it is drawn, model it. If it is not drawn, do not invent it. Model drawn offsets as drawn: a beam drawn 45 mm off grid goes 45 mm off grid. Never snap something to a grid just because a grid is nearby.
2. **Final state.** For renovation or retrofit work, model the final condition: jacketed or strengthened sizes, retrofit levels, existing elements that remain. Do not model demolished elements. Check each sheet title for "Eksisting", "Existing", "Bongkaran" or "Demolition" before modelling from it.
3. **Drawn but not dimensioned means model it with your best estimate. Never leave it out.** (User preference.) If an element is drawn but its size, position or height is not written, work it out as accurately as you can, in this order: measure it from the calibrated vector geometry; take it from a related sheet (section, detail, schedule, architectural drawing); take it from known adjacent or repeated elements; as a last resort, judge it visually from proportions. Leaving a drawn element out is worse than a flagged estimate. This does not override principle 1: if an element is not drawn at all, it is not modelled.
4. **Inferred is not documented.** When you measure or infer a dimension, record the source, the method and a confidence level. Put `LOW CONFIDENCE` in the element's Comments, and log it so it can be refined later.
5. **Ask before choosing between conflicting drawings,** and before deleting anything the user modelled or anything already in the model. Give 2–3 options with a recommended one. The user answers fast. Explain any destructive or large batch change before running it.
6. **Work incrementally.** Do one level or one element family at a time. Verify it, log it, then move on. Never try the whole model in one script.
7. **Don't repeat a failing approach.** After one failure, read the error, change the method (split the script, change the API call, change the check) and record the lesson.
8. **Low quota, high accuracy.** Use small scripts, don't redo finished work, and keep narration short. End with a short report: the outcome plus one next step.

### 1.2 End-to-end workflow
1. **Inventory the drawing set.** List every sheet and its page number (use `pdftotext` plus the visual index pages). Mark which sheets are existing, demolition or new, plan, section or detail, and which part of the building each covers.
2. **Establish the reference frame.** Set out grids (named, with spacing), levels (FFL and the structural slab top, SFL, per zone), the datum of each sheet (canopy or architecture sheets can use a different zero), and the conversion from plan coordinates to Revit internal coordinates.
3. **Calibrate each plan sheet** from its own vector grid lines, piecewise (Part 2.3). Verify the calibration on every grid line before you measure anything.
4. **Build the logic before geometry.** Columns, then beams level by level, then slabs, then foundations, then roof steel, then secondary items. Identify dependencies: slab top sets beam top, and beam soffit sets column base.
5. **Model one level or element group per step** with small scripts (about 4k characters or less). Give every element a Mark and Comments (source sheet, type tag, confidence).
6. **Check each step** against the drawing: overlay or measure, compare counts with the drawing tables, and look at Revit warnings.
7. **Log as you go** in a project doc. Record the source, the rules, coordinates of non-obvious elements, assumptions, conflicts with their resolution, and what is NOT modelled and why.
8. **Audit the full model** (Part 6) at the end of each discipline, and again whenever the user asks for a "final gloss over" or a check "for anything suspicious".
9. **Report briefly,** update the doc, and offer one next step.

### 1.3 When the user points at something
If the user sends a screenshot with something circled, or says "these ones I've selected":
- Call `get_selected_elements` (Revit MCP), or work out the area from the screenshot.
- Then re-read that exact part of the drawing at high DPI before answering. Twice in the session the first guess about what the user meant was wrong: first a different set of members, then the outer thin outline lines rather than the members.

---

## PART 2. Drawing interpretation

### 2.1 Reading a structural DED set (session-derived)
- **Sheet order** in the source set was: foundation (existing), plans per floor (existing, then retrofit), column plan and schedule, jacketing types and details, beam reinforcement details, beam strengthening, slab details (the metal-deck sections), roof truss plan and sections, connection details, canopy sheets, then other structures (bridge, flagpole, green wall, remise canopy).
- **Existing vs new:** the only foundation plan was titled "Eksisting". Four caps on it belonged to a demolished canopy frame and were "attached to nothing". The new canopy had its own foundation on separate sheets. Always ask: is this element existing-to-remain, existing-to-demolish, or new?
- **Labels and line types on the plan sheets**, worked out from PDF vector line widths:
  - dashed line pairs at width 6.0 = beam faces (centre and width come from the pair);
  - width 7.0 = slab and building outline;
  - width 2.0 X-marks = voids;
  - grey hatch = waterproofing.
  - An "X-bracing" pattern inside a cell was void marking, not bracing. Check line width and the legend before modelling bracing.
- **Slab tags** (S1, S2, SN1A, ...) could be read with `pdftotext -bbox`. Beam labels were often vector glyphs, so read them visually from 300–400 dpi crops.
- **Slab schedule conflicts:** the slab table on the plan said SN1A = 120, while the slab detail sheet said 150 (a metal deck: 0.75 mm deck, 50 mm ribs plus 100 mm topping). This was resolved by asking the user (150). Afterwards, steel under metal-deck slabs has its top at SFL − 150, and steel under conventional slabs stays at SFL.
- **Section labels pointing at end-on members:** in the truss sections, a "WF250x125" label pointed to an I-section drawn end-on inside the support column at bottom-chord level. That is the eave beam, not an extra post. Misreading it added 30 wrong posts and put 44 eave beams 950 mm too high. Rule: trace exactly what a leader points to, and check whether the section is a cut through a member running perpendicular to the view.
- **Profile letter tables:** the roof plan had a profile table (A WF250x175, B WF300x150x6.5x9, C WF250x125, D WF200x100, E 2L70x70x6). Read the letter on every member, including extensions past supports. Hip and valley extensions were labelled A, but had first been modelled as D overhangs.
- **Insets can be at a different scale than their title.** The mezzanine inset said 1:100 but was drawn at 1:200. Calibrate insets on their own dimension ticks.
- **Eccentric members are real.** On this job the treasury perimeter beams sat 120 mm inside the column centres, and the roof G25 sat 100 mm inside rows 1 and 3. Both were drawn that way and kept. Secondary beams sat at 1A − 1200 and 2A + 600, not on grids 1A / 2A.
- **Dilatation joints:** the joint was a double thin line about 76 mm apart. Everything in the joint strip belongs to one structure and stops at the joint. Beams first modelled from grid to grid crossed the joint by about 350 mm, and the user spotted one sticking out past the slab.
- **Slab edges** follow the drawn thick outline, not beam faces or grid-based guesses. Edges were first set at 1825 / 24575, but the drawn outline was 1944 / 24458 with jogs. Edge slabs that stopped at beam faces left cantilever stubs sticking out.
- **Heights not on structural sheets:** the front roof block had a plan only. Heights came from the architectural elevation (apex, eave tip) and section (slope). Always say which discipline a height came from.
- **Datums differ between sheet groups:** the canopy sheets used the architect datum (L1 = −0.050). The project value was canopy value + 2.300. Check one known level on each sheet group.
- **Plans vs dimensioned details:** the retrofit plans drew canopy columns about 60–800 mm away from the dimensioned canopy plan. The dimensioned sheet was used and the conflict logged as LOW CONFIDENCE.
- **Pile type from glyphs:** pile types A / B / C were told apart by letter shape (A has straight strokes; B / C have curves), and the counts were cross-checked against the sheet table. They matched exactly.

### 2.2 Dimension inference hierarchy
1. Explicit dimension or schedule value.
2. A value from another related sheet (section, detail, schedule, architecture).
3. A value measured from vector geometry with a verified grid calibration.
4. A visual or proportional estimate, which always gets LOW CONFIDENCE.
Never leave a drawn element out only because no dimension is written. Measure or estimate it, and flag it (principle 3). Session examples:
- Mezzanine knee-brace section not labelled: WF200x100 assumed.
- F-G void member depth unreadable: 170x400 assumed.
- Front roof block heights not on the structural sheets: taken from the architectural elevation and section.
- Pile-cap tops not given: set to the soffit of the deepest beam.
All of these were tagged LOW CONFIDENCE.

### 2.3 PDF tooling (workspace had no network, so only installed tools)
- `pdftoppm -f N -l N -r 300..900 -png` for crops to read visually. Use 400 dpi for labels and 500–900 dpi for overlays.
- `pdftotext -layout/-raw/-bbox` for text where it exists, such as sheet codes and slab tags.
- `pdfplumber` for vector lines, dashes and arcs. An SVG-conversion route dropped the 0.24 pt dashed and arc linework of the foundation sheet, while pdfplumber kept it.
- **Calibration (critical):**
  - Find the vector grid lines on each sheet and record their pt coordinates.
  - Map pt to mm piecewise, grid to grid, per axis. Do not use one global scale.
  - The first calibration assumed row 1' at 310.0 pt and 105.88 mm/pt. The true values were 308.93 pt and about 105.84 mm/pt. That shifted the roof about 112 mm north and the east wing 30–43 mm east, and the error went unnoticed through several checks.
  - After calibrating, confirm that known on-grid members land on grid (for example, row-2 girders at 13200).
- **Automated edge test [session tool, code not preserved]:**
  - A script (`chk2.py`) compared modelled beam faces against the PDF dashed-line pairs and listed offsets.
  - Offsets of 30–80 mm on hatched main frames and up to 16 mm elsewhere were judged drafting or line-weight noise.
  - Larger offsets were investigated one by one.

---

## PART 3. Modelling workflow and Revit / MCP techniques

### 3.1 Coordinates and levels
- Use one plan coordinate system in every log: x = mm east of grid A, y = mm south of the first grid row. Revit internal (session values): X = x − 217837, Y = 172339 − y, ft = mm / 304.8. Write the conversion in the log, with the axis flip.
- Levels are named as on the drawings, at FFL. Keep the SFL per zone in the log (SFL = FFL − 50 typically; −100 at the mezzanine and roof; several local zones at the ground floor). Elements get their elevation from level plus offset.

### 3.2 Columns (concrete)
- Use final jacketed (JK) sizes from the jacketing detail sheets, and existing sizes where no JK type applies.
- Split each column into stacks per storey (S1 base to L1 slab, S2, S3). Leave out a stack where the drawing shows no column above.
- **Base level:** the drawings gave no pile-cap top. Bases were set at the soffit of the deepest beam framing in at the lowest floor (LOW CONFIDENCE), and cap tops were set to the column base.
- Mark `K-<grid>/<row>-S<n>`.
- Orientation (b along X, h along Y) was assumed and logged.

### 3.3 Beams
- Concrete family "BALOK BETON PERSEGI" (b, h); types named `BALOK BETON bxhmm`. Steel family types are named by profile, for example `WF350x175x7x11`, with tag codes BS1..BS6.
- **Placement:** Z justification = Top, with top = SFL set through the end offsets.
- **Y_JUSTIFICATION must be 1 (Center).** The concrete family flexes only one face with b, so the default "Origin" put every beam (b − 200)/2 off its line. That is 300 mm for an 800-wide beam, and it affected all 492 beams. The family could not be edited through the API (a transaction is always open), so the fix was the instance parameter.
- **Joins:**
  - Disallow auto-join (`StructuralFramingUtils.DisallowJoinAtEnd`) at every beam end that is not inside a column footprint. Otherwise Revit notches and trims beams strangely.
  - Keep joins at column ends.
  - Merge collinear beams of the same type that meet at a column into one continuous member (602 → 492 beams).
  - Keep secondary beams split where they frame into girders.
- **Steps between slab zones:** a beam on a boundary with a small step (400 mm or less) takes the higher SFL. For large steps (1.7–2.1 m), boundary beams go at the lower level and step walls are added.
- **Sloped members** (knee braces) were placed as framing with `StructuralType.Beam`. The Brace type snapped its top to the beam centreline.
- Marks: `BLn-W/E/T-nnn`, `BLA-*`, `BLD-*`, and steel `BSL1/BSL2/BSM/BSA-nnn`. Comments hold the type tag, the sheet and LOW CONFIDENCE where it applies.

### 3.4 Slabs
- Use floor types per slab schedule thickness, for example `PELAT BETON 120mm (S1/S2/S3/SN1A)` and `PELAT METAL DECK 150mm (SN1A/SN1B)`, with type marks.
- Draw the outline from the drawn thick line. Openings come from the X-marked voids and the stair and shaft outlines. Split slabs at dilatation joints.
- **Rebuilding a floor that temporarily overlaps a neighbour** brings up the modal "Highlighted floors overlap" warning. That blocks the API and looks exactly like a timeout. Rebuild in an order that never overlaps, a few floors per call.
- Logic check: every beam top is at the slab top above it, or carries a step wall.

### 3.5 Steel
- **Use families wherever they exist** (user rule): wide-flange beam families and UC-based column families.
- When an exact size is missing, duplicate a type: `src.Duplicate(name)`, then set h, b, t, s, r in a separate call. For example, `KOLOM BAJA WF300x150x6.5x9` and `KOLOM BAJA HB300x300x10x15` were made from the UC family.
- If you substitute the nearest existing family size, flag it LOW CONFIDENCE.
- **No angle or CNP family existed** in the project or the library, so double angles and purlins were made as DirectShapes:
  - `GeometryCreationUtilities.CreateExtrusionGeometry` with an I-section, 2L or 12-point CNP profile;
  - category Structural Framing;
  - for 2L sections, a 12 mm gusset gap between the angles.
  - Purlin CNP150x65x20x3.2: the web lies on the rafter top, flanges point up, lips turn in, and the web centre sits 46 mm outboard at eave tips.
- Keep the truss geometry in the log: support y, ridge, heel z, chord centreline z, panel points, diagonal direction (Pratt), and member sizes per member type.

### 3.6 Foundations
- **DirectShape is the company convention for foundations.** Use category Structural Foundations.
- Split each foundation into two model groups: `PONDASI <type> <grid> - PILE CAP` and `PONDASI <type> <grid> - TIANG BOR`. Marks: `PC-<type>-<grid>`, `TB-<type>-x/y`.
- Pile length = Leff from the cap soffit.
- Delete by deleting the group element: `document.Delete(group.Id)`.

### 3.7 MCP / API mechanics (most important technical lessons)
- Tool: `mcp__remote-devices__mcp-server-for-revit__send_code_to_revit`. If it is not callable, load its schema first with ToolSearch `select:<full name>`.
- The code runs inside `Execute` with `document` available and a transaction already open. `return` a string, and build that string with a StringBuilder for reports.
- **Keep scripts to about 4k characters or less.** A 9k script with many local functions timed out at about 80 s three times, with nothing committed. The same logic as three scripts of about 4k each ran in under a second.
- Error strings come back in Chinese:
  - `执行失败: Exception has been thrown by the target of an invocation` is a runtime error. Wrap the risky part in try/catch and return `(ex.InnerException??ex).Message`.
  - `代码编译错误` is a compile error and gives the line number.
- **Compiler quirks:**
  - `int[]` literals failed; use `double[]`.
  - Prefer `Func<>` lambdas.
  - Some BuiltInParameters do not exist in Revit 2026 (for example `ROOF_CURVE_OVERHANG`). Guard with `?.` and try/catch, or use object methods such as `FootPrintRoof.get_Overhang`.
- **Multi-step type work:** creating a type, setting its parameters and swapping instances in one script threw an exception. Three separate calls, each with try/catch, worked.
- **Clash checks:** `ElementIntersectsElementFilter`-style scripts threw exceptions. Bounding-box overlap checks were reliable and fast.
- Use `ALL_MODEL_MARK` for marks and `ALL_MODEL_INSTANCE_COMMENTS` for comments.
- **Moving elements in bulk:** `ElementTransformUtils.MoveElement` worked, for example moving 44 eave beams down 950 mm. Append the reason to Comments.
- **Renaming views:** `v.Name = newName`, inside try/catch per view (names must be unique). Report OK or FAIL for each.
- Bash in the workspace had no network, so no pip or npm installs. Use the installed tools.

---

## PART 4. Documentation and views (what was actually done)
- **Inspection views per level:**
  - a structural plan named `0n <LEVEL> - Denah struktur`: Coordination discipline, view range from slab top −1.7 m to about +1.2 m, crop around the building;
  - a 3D view named `0n <LEVEL> - 3D`, with the section box limited to that level;
  - `00 STRUKTUR - 3D semua level`.
  - Show only structural categories, with floors 45–55% transparent.
- **View filters:**
  - `LOW CONFIDENCE` (Comments contains the text, red, highest priority);
  - steel beams blue, concrete beams grey;
  - slabs coloured by thickness (150 blue, 120 yellow, 300/500 grey).
- **The Structural Plan view type in the template injected 6 filters,** including a hidden "Floors - Concrete NOT", that hid all the slabs. Remove the template's filters from working views.
- **User preference:** don't put the AI's name in view names. Views first named "CLAUDE - ..." had to be renamed. Use project-style names from the start.
- **Not done in the session (gap):** sheets, dimensions, tags, schedules, annotation standards. No session-derived standard exists for these yet. Follow the project's own template and ask.

---

## PART 5. Troubleshooting knowledge base

| Problem | Initial approach | What went wrong | Successful solution | Lesson |
|---|---|---|---|---|
| Concrete beams off their line | Placed with default Y justification | Family flexes one face, so solids sat (b−200)/2 off (300 mm for 800 wide) | Set Y_JUSTIFICATION = 1 (Center) on all beams | Check a test beam's solid against its location line before mass placement |
| Plan coordinates systematically shifted | One global scale (105.88 mm/pt), row 1' assumed at 310.0 pt | Roof about 112 mm north, east wing 30–43 mm east; earlier overlay checks were also wrong | Piecewise grid-to-grid calibration from each sheet's vector grid lines | Calibrate per sheet from vectors and verify on all grids |
| Beams notched or trimmed oddly | Default auto-join | Revit joined beam ends to unrelated members | DisallowJoinAtEnd at every end not in a column; keep column joins | Apply the join rule right after placing beams |
| Too many beam pieces | One beam per bay | 602 fragments, hard to audit | Merge collinear same-type beams at columns (→ 492) | Continuous members through columns; split secondaries at girders |
| Script timeout, nothing committed | One 9k script with many local functions | Hit the 80 s limit three times | Split into three scripts of about 4k | Keep scripts small; run in sequence |
| "Timeout" while rebuilding floors | Rebuilt overlapping floors | A modal overlap warning blocked the API | Rebuild in an order that never overlaps, few per call | Hanging calls may be modal dialogs, not slowness |
| Type creation threw | Duplicate, set parameters and swap in one script | Invocation exception | Three calls: create, set, swap, each in try/catch | Separate type changes from instance changes |
| Clash script threw | Intersect filters | Exceptions | Bounding-box overlap checks | Use simple, robust geometry tests |
| Compile errors | int[] literals, local functions | Host compiler rejected them | double[] arrays, Func<> lambdas | Use the simplest C# constructs |
| Missing BuiltInParameter | ROOF_CURVE_OVERHANG | Not in Revit 2026 | Use object methods or `?.` guards | Don't assume parameter names; guard them |
| 30 extra posts, eave beams 950 mm too high | Read "WF250x125" as a post beside the column; eave beams at heel z | The label pointed to the end-on eave beam at bottom-chord level | Deleted the posts, lowered the eave beams to the chord centreline, used the drawn WF300x150x6.5x9 columns | Trace leaders; recognise end-on sections |
| Hip overhangs wrong | Modelled as WF200x100 (D) | The plan labels the hip and valley extensions A | Replaced them with profile-A extensions | Read the profile letter on every segment |
| Outline members missing | Modelled main members only | The user circled the thin outer lines (eave-tip purlins) | Added CNP eave-tip purlins | Thin outer lines are members too; ask what a circle means |
| Secondary beams on the wrong lines | Put them on grids 1A / 2A | Drawn at 1A − 1200 and 2A + 600 | Moved them on L1 and L2 | Never assume a beam sits on the nearest grid |
| Gap beams crossing the dilatation joint | Modelled grid to grid (F to G) | Crossed the joint by about 350 mm; the user spotted it | Stopped them at the joint; added joint beams | Find the joints first; nothing crosses them |
| Slab edges wrong | Edges at grid-based values | Drawn outline differed; stubs stuck out past the slab | Redrew from the drawn 7.0-width outline | Slab outline = drawn thick line |
| Unattached foundation caps | Modelled every cap on the "existing" foundation plan | 4 caps belonged to a demolished canopy | Asked the user and deleted them; modelled the new canopy from its own sheets | Separate existing, demolished and new for each element |
| Slabs hidden in the plan view | Used the Structural Plan view type | Template injected filters ("Floors - Concrete NOT") | Removed the filters from the views | Check view filters when elements vanish |
| Bracing in a void cell | The X pattern looked like bracing | It was void marking (2.0 width) | Not modelled as bracing | Use line width and legend to decide meaning |
| Inset scale | Used the title scale 1:100 | Drawn at 1:200 | Calibrated on the dimension ticks | Verify each inset's scale |
| Knee brace top snapped | Brace structural type | Top snapped to the beam centreline | Placed as Beam type with sloped ends | Use Beam type for precise sloped members |
| Project doc write refused | project_write after editing locally | Tool needs the doc's full current text seen in the session | Read the doc in full (project_read or Read allow_large), edit, then write | Read in full before every doc rewrite |
| Conflicting slab thickness | Took the plan table value | The detail sheet disagreed | Asked the user; adopted the detail value and lowered the steel | Raise conflicts, don't pick silently |

### 5.1 User preferences and conventions (repeated or corrected during the session)
- "Follow the drawings: if it's drawn, draw it; if it's not drawn, don't."
- If something is drawn but has no dimension, estimate it as accurately as possible (measure, cross-reference, judge visually) rather than leaving it out. Flag it LOW CONFIDENCE.
- Model drawn offsets exactly ("45 mm off the grid, model it so").
- Families for H beams and columns; DirectShape only for foundations and items with no family.
- "No need to redo what you've done, focus on finishing it."
- Use as little quota as possible without losing accuracy.
- The user expects a full audit when asked ("check the entire model once more for anything suspicious"), and prefers AskUserQuestion with a recommended option.
- No "CLAUDE" in view names.

---

## PART 6. Quality control checklist

Run this at the end of each level or discipline, and as a full audit.
1. `document.GetWarnings()`: target 0. Group the warnings by description.
2. Marks: none blank, none duplicated (all categories you created).
3. Duplicate framing: same type, collinear, overlapping.
4. Floor-floor clashes and foundation overlaps (bounding box).
5. Each column stack is continuous from its base to the top storey, and lands on a cap or a drawn support.
6. Beam top = SFL of the slab it supports, or a documented step or step wall. Steel under metal deck sits at SFL − deck thickness.
7. Free beam ends and unsupported slab edges: list them. Each must be a drawn cantilever, joint face or void edge. Document the remaining ones as "as drawn".
8. Counts against the drawing tables (piles, caps, members).
9. Spot-check positions against the calibrated PDF vectors. Tolerance: up to about 16 mm is line-weight noise. Investigate anything over about 30 mm unless it is a known drafting offset.
10. Nothing crosses a dilatation joint.
11. Existing, demolished and new status confirmed for anything "attached to nothing".
12. LOW CONFIDENCE items reviewed and listed in the log.
13. Update the log: totals, changes and open items.

## Known limitations
- Vector text is often unreadable by tools, so labels need visual reading, which is slower and can be misread. Re-read key labels at a higher DPI.
- Structural sheets may not give foundation levels, truss heights for secondary blocks, or member sizes for minor framing. These become LOW CONFIDENCE inferences.
- The calibration and edge-test scripts used in the session were not preserved verbatim. Rebuild them from the descriptions in Part 2.3.
- Documentation output (sheets, tags, dimensions, schedules) was not part of the session. This skill has no tested standard for it.
- The Revit host's compiler and API limits are specific to the MCP plugin used. Re-check them on a new setup with a tiny test script.