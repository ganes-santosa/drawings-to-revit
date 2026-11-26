# Project log — <project>

One log per project, shared by the structural (str) and architectural (ars) skills. Saved as `<drawing set folder>\_log\project-log.md` (each skill's `project-setup.md`). Setup is done once; the second skill reads it and adds only its own sections.

## Common (whichever skill sets up first)
- Drawing sets: discipline, parts, sheets, revisions, dates · Revit version · active Revit document title · Date
- Units & scale · Plan coordinate system: x = …, y = … · Revit conversion: X = …, Y = … (axis flip?), ft = mm/304.8
- Levels: name | FFL | SFL by zone (each zone's plan extent: polygon or grid range, so scripts can look up the expected offset at any point) | source sheet · conflicts between plan, section and elevation levels · Height chain (slab top → beam top → column base → cap top)
- Grids: name | position | source · Calibration residuals per sheet
- STR / ARS relationship: structure built in this file or linked · transform · differences between the disciplines (asked, never ranked)
- Discipline precedence when ARS and STR differ (asked once; RSUD: STR governs, undrawn elements are not invented and get an RFI tag) · date and who decided
- Conventions: Mark patterns · type names · material names (spec codes) · Comments format
- Family folder · log folder (if not next to the drawings)

## Structure (str-drawing-to-revit)
- **Modelling decisions (asked once at setup):** beam segmentation A continuous / B split at supports / C continuous within zones (+ zone lines) · slab segmentation · column stacks · roof structure method (Revit Structural Trusses / Structural Framing members) · roof scope (purlins / rods / light-gauge) · date and who decided
- Type catalogs: columns, beams, slabs, foundations, roof (`type-catalog-template.csv`), final versions
- Coordinates of non-obvious elements (off-grid, eccentric, joint strips)
- Roof geometry record per truss/frame (`roof-framing.md` B2): plan line + gridlines of every copy, supports and support top z, heel / ridge / eave z, slope, chord centreline z, panel points, web pattern, profile per segment; arches: span, rise, radius, height reference

## Architecture (ars-to-revit)
- Decisions: finishes as wall layers or separate walls · finish floors vs combined floors · width/height basis in schedules · exterior first (per project) · date and who decided
- Type catalogs: walls, floors, ceilings, roofs, doors/windows (`type-catalog-template.csv`), final versions
- Coordinates of non-obvious elements (off-grid, drawn offsets)

## Both
- Element counts: discipline | category | modelled | expected (schedule / plan) | notes
- Conflicts (ID | discipline | topic | A | B | impact | resolution)
- Assumptions (LOW CONFIDENCE list with id/mark/method)
- NOT modelled + why · deferred by the user
- Open questions
- Change history (date | discipline | what changed | dependents re-checked)
