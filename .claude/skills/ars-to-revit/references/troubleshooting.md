# Troubleshooting — symptom index

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24. Add a row for every newly understood failure; fix detail goes in the element file. `F#` = row in the legacy KPwBI trial-and-error table (`assets/legacy/`).

## How to troubleshoot
1. Reproduce on **one** element. 2. Read the exact error (try/catch, return the inner message). 3. Change the method, don't retry. 4. Verify the fix in the model. 5. Record it (SKILL.md §8).

| Symptom | Likely cause | Fix | Detail | Status |
|---|---|---|---|---|
| Call "times out", Revit seems frozen | Modal dialog (overlap, unjoin, identical instances, cut-out, say_hello) | User dismisses (never Delete); count what committed | api §4 | [IMPORTED KPwBI-ARS] F7, [VERIFIED 2026-11-24 say_hello] |
| Script timeout, nothing committed | Script too large / `dynamic` | ≲ 4k chars, typed C# | api §4 | [IMPORTED KPwBI-ARS] F5, F6 |
| `执行失败 … target of an invocation` | Runtime exception | try/catch, return inner message | api §4 | [IMPORTED KPwBI-ARS] |
| `代码编译错误` | Compile error (quirks) | See api §4 quirks | api §4 | [IMPORTED KPwBI-ARS] |
| Reply doesn't match the script sent | Previous call's late result | Re-query state | api §4 | [IMPORTED KPwBI-ARS] F36 |
| Elements gone although script said OK | Deleted at commit ("Can't make type") | Verify in a later call | api §4 | [IMPORTED KPwBI-ARS] F23 |
| Changes landed in the wrong building | Wrong active document | Check `document.Title` before writing | project-setup §2 | [IMPORTED KPwBI-ARS] F32 |
| Window in wall, uncut | Family without Opening | `NewOpening` in family | openings-families | [IMPORTED KPwBI-ARS] F2 |
| Wide window loses its cut | Template host wall too small | Extend host wall first | openings-families | [IMPORTED KPwBI-ARS] F4 |
| Hosted but uncut | Load+place in one call; flip before Regenerate | Re-place in B5 order | openings-placement | [IMPORTED KPwBI-ARS] F3, F19 |
| Family change not taking | LoadFamily doesn't overwrite | Delete Family, load | openings-families | [IMPORTED KPwBI-ARS] F33 |
| Doors vanish on 100 mm walls | Unknown ("Can't make type") | Test one per wall type | openings-placement | [OPEN] F23 |
| Doors clash with windows | Ambiguous keyplan leaders | Overlap check, list doubtful tags | openings-placement | [IMPORTED KPwBI-ARS] F22 |
| Door facing wrong | Raycast on open sides | Use model facts | openings-placement | [IMPORTED KPwBI-ARS] F18 |
| Tags not found by text search | Glyphs split | bbox + nearest number | drawing-interpretation §3 | [IMPORTED KPwBI-ARS] F25 |
| Keyplan positions wrong | Nested PDF transforms | Raster crops with mm rulers | drawing-interpretation §4 | [IMPORTED KPwBI-ARS] F24 |
| Schedule search finds nothing | Outlined text / scans (RSUD, Hunver) | Visual reading; ask the user to point | drawing-interpretation §3 | [VERIFIED 2026-11-24] |
| Everything shifted vs PDF | Global scale | Piecewise per-sheet calibration | drawing-interpretation §4 | [IMPORTED KPwBI-ARS] F15 |
| Plan offsets off by ~100 mm | Calibration from bubble text | Verify on a known element | drawing-interpretation §4 | [IMPORTED KPwBI-ARS] F16 |
| Element misidentified (skylight, frame) | Identity from hatch/shape | Say it's an inference; ask; study render/section | drawing-interpretation §5 | [IMPORTED KPwBI-ARS] F10, F26 |
| User-corrected value lost | Re-derived from drawing | Apply corrections exactly, record | drawing-interpretation §5 | [IMPORTED KPwBI-ARS] F27 |
| API hangs deleting walls | "Can't keep elements joined" | Disallow joins + unjoin first | walls | [IMPORTED KPwBI-ARS] F7 |
| Overlap dialogs placing walls | 1–4 mm overlaps | Snap to exact faces | walls | [IMPORTED KPwBI-ARS] F31 |
| Grey band in niches / slab edge visible | Floor edge beyond wall face | Recreate floor to the wall face | floors | [IMPORTED KPwBI-ARS] F28 |
| Floors overlap dialog | Temporary overlap during rebuild | Order operations | floors | [IMPORTED KPwBI-ARS] F7 |
| Wrong roof faces sloped | Slope by index; radians | By coordinates; rise/run | roofs | [IMPORTED KPwBI-ARS] F8 |
| Roof too high | Sketch at eave top | Sketch = underside; t/cos offset | roofs | [IMPORTED KPwBI-ARS] F9 |
| Architecture misses real columns | Placed on grids | Read positions from the STR link | project-setup §6 | [IMPORTED KPwBI-ARS] F11, F12 |
| Column exposed below fascia | Element stopped short | Look behind/below; extend to slab underside | model-validation §2 | [IMPORTED KPwBI-ARS] F29 |
| Duplicate Type Mark warnings | Types share marks | Unique Type Mark per new type | types-and-materials §5 | [IMPORTED KPwBI-ARS] |
| User dislikes view names | "CLAUDE" in names | Neutral `CHK …` names | SKILL §4 | [IMPORTED KPwBI-ARS] F35 |
| Skill route not found | Row missing/typo | `python scripts/check_skill.py` | SKILL §2 | [VERIFIED 2026-11-24] |

Parked topics (facade niches F1, F13, F14, F20, F21; site toposolids F30; doc tool F34) stay in `assets/legacy/` until those routes exist.

## Related
`revit-api-and-automation.md`, element files.
