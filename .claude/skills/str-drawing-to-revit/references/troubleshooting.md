# Troubleshooting — symptom index

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20. Add a row whenever a *new* failure mode is understood; put the fix detail in the element file and link here.

## How to troubleshoot
1. Reproduce on **one** element. 2. Read the exact error (try/catch, return `(ex.InnerException??ex).Message`). 3. Change the method (not just retry). 4. Verify the fix in the model. 5. Document (SKILL.md §8). Don't document untested workarounds as procedures.

| Symptom | Likely cause | Fix | Detail | Status |
|---|---|---|---|---|
| API call hangs ("timeout") | Modal dialog in Revit (overlap warning) | Check Revit window; non-overlapping rebuild | slabs.md | [VERIFIED KPwBI] |
| Script timeout, nothing committed | Script too large | Split to ≲4k char scripts | api §4 | [VERIFIED KPwBI] |
| `执行失败 … target of an invocation` | Runtime exception | try/catch, return InnerException message | api §4 | [VERIFIED KPwBI] |
| `代码编译错误` | Compile error (int[] literal, local fn) | double[], Func<> | api §4 | [VERIFIED KPwBI] |
| Type creation threw | Create+set+swap in one call | Three calls | revit-families | [VERIFIED KPwBI] |
| Clash script threw | Intersect filters | Bounding-box overlap | model-validation | [VERIFIED KPwBI] |
| BuiltInParameter missing | Not in this Revit version | Guard / object method | api §4 | [VERIFIED KPwBI] |
| Beams sideways off line | Y justification | Y_JUSTIFICATION=1 | beams | [VERIFIED KPwBI] |
| Beams notched | Auto-join | DisallowJoinAtEnd | beams | [VERIFIED KPwBI] |
| Everything shifted vs PDF | Global scale | Piecewise calibration | grids-and-levels §5 | [VERIFIED KPwBI] |
| Elements missing from view | Template filters | Remove filters | slabs / documentation | [VERIFIED KPwBI] |
| Member count/height impossible | Misread end-on section | Trace leaders | drawing-interpretation §5 | [VERIFIED KPwBI] |
| Wrong profile on extension | Missed profile letter | Read letter on every segment | structural-framing | [VERIFIED KPwBI] |
| Elements cross a joint | Grid-to-grid modelling | Find joints first | beams | [VERIFIED KPwBI] |
| Orphan foundations | Demolished frame included | Ask; check sheet status | foundations | [VERIFIED KPwBI] |
| Project-doc write refused | Doc not read in full this session | Read in full, edit, write | — (KPwBI doc tool) | [VERIFIED KPwBI] |
| Skill route not found | Row missing/typo | `python3 scripts/check_skill.py` | SKILL.md §2 | [VERIFIED container] |

## Documentation/view gotchas `[VERIFIED KPwBI]`
- Structural Plan view type injected 6 filters incl. hidden "Floors - Concrete NOT": remove from working views.
- Inspection views: plan per level (Coordination discipline, range slab top −1.7 m to +1.2 m), 3D per level with section box, overall 3D; structural categories only, floors 45–55% transparent; filters: LOW CONFIDENCE red, steel blue, concrete grey, slabs by thickness.
- Sheets, dimensions, tags, schedules: **not yet done** `[OPEN]` — follow project template and ask.
