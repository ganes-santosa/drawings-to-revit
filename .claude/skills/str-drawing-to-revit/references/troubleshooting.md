# Troubleshooting — symptom index

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20. Add a row whenever a *new* failure mode is understood; put the fix detail in the element file and link here.

## How to troubleshoot
1. Reproduce on **one** element. 2. Read the exact error (try/catch, return `(ex.InnerException??ex).Message`). 3. Change the method (not just retry). 4. Verify the fix in the model. 5. Document (SKILL.md §8). Don't document untested workarounds as procedures.

| Symptom | Likely cause | Fix | Detail | Status |
|---|---|---|---|---|
| API call hangs ("timeout") | Modal dialog in Revit (overlap warning) | Check Revit window; non-overlapping rebuild | slabs.md | [IMPORTED KPwBI] |
| Script timeout, nothing committed | Script too large | Split to ≲4k char scripts | api §4 | [IMPORTED KPwBI] |
| `执行失败 … target of an invocation` | Runtime exception | try/catch, return InnerException message | api §4 | [IMPORTED KPwBI] |
| `代码编译错误` | Compile error (int[] literal, local fn) | double[], Func<> | api §4 | [IMPORTED KPwBI] |
| Type creation threw | Create+set+swap in one call | Three calls | revit-families | [IMPORTED KPwBI] |
| Clash script threw | Intersect filters | Bounding-box overlap | model-validation | [IMPORTED KPwBI] |
| BuiltInParameter missing | Not in this Revit version | Guard / object method | api §4 | [IMPORTED KPwBI] |
| Beams sideways off line | Y justification | Y_JUSTIFICATION=1 | beams | [IMPORTED KPwBI] |
| Beams notched | Auto-join | DisallowJoinAtEnd | beams | [IMPORTED KPwBI] |
| Everything shifted vs PDF | Global scale | Piecewise calibration | grids-and-levels §5 | [IMPORTED KPwBI] |
| Elements missing from view | Template filters | Remove filters | slabs / documentation | [IMPORTED KPwBI] |
| Member count/height impossible | Misread end-on section | Trace leaders | drawing-interpretation §5 | [IMPORTED KPwBI] |
| Wrong profile on extension | Missed profile letter | Read letter on every segment | roof-framing | [IMPORTED KPwBI] |
| Elements cross a joint | Grid-to-grid modelling | Find joints first | beams | [IMPORTED KPwBI] |
| Orphan foundations | Demolished frame included | Ask; check sheet status | foundations | [IMPORTED KPwBI] |
| Project-doc write refused | Doc not read in full this session | Read in full, edit, write | — (KPwBI doc tool) | [IMPORTED KPwBI] |
| Beams don't touch columns or each other ("floating") | End points taken from where the drawn line stops; wrong level; support not modelled yet | Support table, ends resolved to supports, connectivity check | building-logic | [THEORY] (user-reported) |
| Call "times out" while merging/trimming beams | Modal "Can't keep elements joined" dialog | User clicks Unjoin; count what committed, then continue; disallow joins before changing curves | beams B4–B5 | [VERIFIED RSUD] |
| Call "times out" right after placing beams | Modal "identical instances in the same place" (duplicate rows) | User dismisses (OK, not Delete); de-duplicate the instance table | beams B2 | [VERIFIED RSUD] |
| Reply does not match the script just sent | Result of the previous timed-out call | Ignore it; re-read the model state | api §4 | [VERIFIED RSUD] |
| Corner stubs and notches after extending ends | Overshoot: end landed past the target beam's end | Crossing point within target length; joint rules | beams B5b, building-logic §6 | [VERIFIED RSUD] |
| Column joins missing | DisallowJoinAtEnd applied at every end | AllowJoinAtEnd at column ends | beams | [VERIFIED RSUD] |
| Perimeter beams stick out past the columns | Beams from plan lines, columns from schedule; flush intent lost | Flush snap (perimeter only) | drawing-interpretation §5 | [VERIFIED RSUD] |
| Whole floor placed wrong | Sheet shifted vs sister sheets; alignment locked on wrong grid multiple | Constrained per-sheet grid alignment; check one column per sheet | grids-and-levels §5 | [VERIFIED RSUD] |
| Script timeout on large beam sets | Nested loops of API calls | Arrays first, write only changed elements | api §4 | [VERIFIED RSUD] |
| Beams dropped 50 mm / one beam at ground level after edits | Setting `LocationCurve.Curve` reset the end offsets to 0 | Read offsets before, write back after every curve edit; audit offsets per level | beams B4–B5 | [VERIFIED RSUD] |
| Beam faces stick out of the slab side along façades | Slab edges from the slab sheet, beams from the beam sheet (30–190 mm apart) | Slab edge = edge-beam outer face | slabs B2a.2 | [VERIFIED RSUD] |
| Jagged slab edges / "extrusion profiles" | Outlines traced from a raster | Cell grid of real face lines | slabs B2b.1 | [VERIFIED RSUD] |
| Slab corners notched, stepped, sliver strips, small holes | Loop artifacts | Artifact table with guards | slabs B2b.2 | [VERIFIED RSUD] |
| Beam sticks out into empty space | Panel cut away, edge beam missing, phantom beam, or wrong height | Classify first (four causes) | slabs B5b | [VERIFIED RSUD] |
| Modal "circular chain of references" | Hosted floor openings | Shaft openings | slabs B4–B5 | [VERIFIED RSUD] |
| "Insufficient memory", whole call rolled back | Several levels rebuilt in one call | One level per call | api §4 | [VERIFIED RSUD] |
| Same problem keeps coming back over several rounds | Only the user's selected instances were fixed | Treat the selection as a class; scan every level | slabs B5b, SKILL §4 | [VERIFIED RSUD] |
| Thin outer lines (eave-tip purlins) missing | Modelled main members only; user circled the outline | Thin outer lines are members too; ask what a circle means | roof-framing | [IMPORTED KPwBI] |
| Secondary beams on the wrong lines | Assumed nearest grid (1A/2A) | Use drawn offsets (1A − 1200, 2A + 600) | beams | [IMPORTED KPwBI] |
| Slab stubs stick out past the edge | Edges set from grids or beam faces | Redraw from the drawn thick outline | slabs | [IMPORTED KPwBI] |
| "Bracing" in a void cell | X pattern read as bracing | Line width 2.0 + legend = void marking | drawing-interpretation §5 | [IMPORTED KPwBI] |
| Inset positions wrong | Title said 1:100, drawn 1:200 | Calibrate on the inset's own ticks | grids-and-levels | [IMPORTED KPwBI] |
| Knee-brace top snapped to beam centreline | Brace structural type | Place as Beam type with sloped ends | beams | [IMPORTED KPwBI] |
| Slab thickness differs plan vs detail | Took the plan table value | Ask; adopt the answer and lower steel under metal deck | slabs | [IMPORTED KPwBI] |
| Skill route not found | Row missing/typo | `python scripts/check_skill.py` | SKILL.md §2 | [IMPORTED container] |

## Documentation/view gotchas `[IMPORTED KPwBI]`
- Structural Plan view type injected 6 filters incl. hidden "Floors - Concrete NOT": remove from working views.
- Inspection views: plan per level (Coordination discipline, range slab top −1.7 m to +1.2 m), 3D per level with section box, overall 3D; structural categories only, floors 45–55% transparent; filters: LOW CONFIDENCE red, steel blue, concrete grey, slabs by thickness.
- Sheets, dimensions, tags, schedules: **not yet done** `[OPEN]` — follow project template and ask.
| Elements doubled after re-running a batch | Script placed every row again | Skip existing Marks; `find_duplicates.cs` | api §5 | [THEORY] |
| Connectivity passes but a beam floats in 3D | Old check ignored height (beam on another floor counted) | Use the 2026-11-25 script (height test) | building-logic §6 | [THEORY] |
| Audit flags many correct beam offsets | Floor has several SFL zones, compared to one standard | Compare to the zone's SFL (level table with zone extents) | beams B6 | [THEORY] |
| Roof sheets not found by `find_schedules.py` | Text outlined on roof sheets | Drawing index, visual search, or ask the user | roof-framing §1.1 | [VERIFIED 2026-11-25, samples] |
| Purlin count wrong per slope | Spacing applied in plan, not along the slope | Spacing along the slope (plan = s × cos θ) | roof-framing B3.7 | [THEORY] |
