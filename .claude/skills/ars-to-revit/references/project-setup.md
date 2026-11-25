# Project setup — active document, units, coordinates, levels (FFL/SFL), grids, structure link

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24 · Revit tested: none yet in this skill.

## 1. Scope
Everything element routes assume exists: the right Revit document, units, one coordinate conversion, levels, grids, and how the structure is present (link or in-file). Calibration of sheets: `drawing-interpretation.md` §4.

## 2. Orient before anything `[IMPORTED KPwBI-ARS]`
1. Read the project log (and area log if any). Never start from memory of an earlier chat. **One log per project, shared with the structural skill:** `<drawing set folder>\_log\project-log.md` (for the sample sets `samples\<project>\_log\`), from `assets/examples/project-log-template.md`. If the structural skill already set up units, levels and grids, reuse them and add only the architecture sections; differences between the disciplines are asked, never ranked.
2. **Check the active document:** the MCP writes to the *active* one. Read `document.Title`; list `document.Application.Documents` (open and linked). If the title is not the project the user named, stop and ask them to switch windows. KPwBI once edited the wrong building this way.
3. List what exists (levels, grids, walls, floors, roofs, links, loaded door/window families) before proposing work. Read-only probe: `revit-api-and-automation.md` §3.
4. **Do not touch a model other agents or people are working on.** Ask for a scratch or project copy for tests (user rule, 2026-11-24).

## 3. Units and coordinates
- API lengths are feet: mm ÷ 304.8; `ElementId.Value` (long) in Revit 2026 `[IMPORTED KPwBI-ARS]`.
- Write one plan coordinate system in the log (e.g. x mm east of grid A, y mm south of row 1) and the conversion to Revit (`X = x − 217837`, `Y = 172339 − y`: the KPwBI Utama example, note the y flip) `[IMPORTED KPwBI-ARS]`.
- Several buildings on one site can have different origins and rotations (KPwBI Penunjang linked at an offset and −3.48°): never link origin to origin without checking `[IMPORTED KPwBI-ARS]`.

## 4. Levels `[IMPORTED KPwBI-ARS]`
- Record **FFL and SFL per level** (SFL usually FFL − 50; −100 at mezzanine/roof on KPwBI). Architectural levels = FFL; structural slabs sit at SFL; the finish build-up (SFL → FFL) is the floor finish (`floors.md`).
- Sources: sections first, then elevations, then plan level marks (`±0.00`, `+3.700`, peil). Conflicts happen (KPwBI elevations −3400 vs plans/sections −3300): log, follow precedence (SKILL.md §5), say which was used.
- A building can have its own datum (KPwBI Penunjang ground −1000 vs Utama −3300).
- Level names follow the project (`LANTAI 1`, `LANTAI 2`, `DAK ATAP`, `TOP ATAP`).

## 5. Grids
- Grid names and positions from the plans (dimension chains between bubbles). Check them on every architectural sheet against the STR grid; off-grid walls keep their drawn offsets.
- `[THEORY]` `Grid.Create(doc, Line)` then `grid.Name = "A"`; MCP `create_grid` exists (not yet tried).

## 6. Structure (STR) present? `[IMPORTED KPwBI-ARS]`
- Linked: `RevitLinkInstance.GetLinkDocument()`; collect columns/framing/floors with `BoundingBoxIntersectsFilter` (Outline in feet); check the link transform (identity on KPwBI).
- Use real STR positions for anything structural-adjacent (column covers on grids missed the real columns by 1000 mm on KPwBI).
- **Architecture and structure are not ranked against each other:** where they differ (column size, slab level, beam soffit vs ceiling), log it and ask (SKILL.md §5). KPwBI followed STR as a project decision.
- No link and no structure in the file: ask whether to model architectural floors only, or wait for the STR model.

## 7. Gate
Project log has: document title, units, conversion, level table (FFL/SFL, source), grid table, STR status. Levels and grids in Revit read back equal to the table.

## Related
`drawing-interpretation.md`, `building-logic.md` §5 (heights), `revit-api-and-automation.md`.
