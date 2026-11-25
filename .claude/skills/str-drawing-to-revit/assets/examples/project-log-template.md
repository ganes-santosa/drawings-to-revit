# Project log — <project>

Saved as `<drawing set folder>\_log\project-log.md` (project-setup.md §3 step 6).

- Drawing set: sheets, revisions, dates · Tool/Revit version · Date
- Units & scale · Plan coordinate system: x = …, y = … · Revit conversion: X = …, Y = … (axis flip?), ft = mm/304.8
- Levels: name | FFL | SFL by zone (each zone's plan extent: polygon or grid range, so scripts can look up the expected offset at any point) | source · Height chain (slab top → beam top → column base → cap top)
- Grids: name | position | source · Calibration residuals per sheet
- Conventions: Mark patterns · type names · comments format
- **Modelling decisions (asked once at setup):** beam segmentation A continuous / B split at supports / C continuous within zones (+ zone lines) · slab segmentation · column stacks · roof scope (purlins / rods / light-gauge) · date and who decided
- Element tables / counts: category | modelled | expected | notes
- Coordinates of non-obvious elements (off-grid, eccentric, joint strips)
- Roof geometry record per truss/frame (roof-framing.md B2): plan line + gridlines of every copy, supports and support top z, heel / ridge / eave z, slope, chord centreline z, panel points, web pattern, profile per segment; arches: span, rise, radius, height reference
- Conflicts (ID | topic | A | B | impact | resolution)
- Assumptions (LOW CONFIDENCE list with id/mark/method)
- NOT modelled + why
- Open questions
- Change history
