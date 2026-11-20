---
name: drawing-extract
description: Extract structural data (grids, levels, columns, beams, slabs, footings, walls, schedules) from structural construction drawings into structured JSON for Revit modeling. Use when given structural plan/section/schedule sheets.
---

# drawing-extract

## Steps

1. Identify sheet type: plan, section, detail, schedule. Note level/scale from title block.
2. Extract grids first (names, positions, spacing). All other positions reference grids.
3. Extract levels (name, elevation, units).
4. Extract members per sheet: tag, type/size, grid location, level, offsets.
5. Read schedules (column/beam/footing) and join to plan tags.
6. Emit JSON. Flag ambiguous or missing items under `"issues"`; never guess sizes.

## Output schema

```json
{
  "units": "mm",
  "grids": [{"name": "A", "dir": "x", "pos": 0}],
  "levels": [{"name": "L1", "elev": 0}],
  "members": [{"tag": "C1", "kind": "column", "type": "400x400 RC", "level": "L1", "at": ["A", "1"]}],
  "issues": []
}
```
