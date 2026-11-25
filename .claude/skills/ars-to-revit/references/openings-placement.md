# Door and window placement — hosted, within the wall, right sill, right facing, cutting (OST_Doors, OST_Windows)

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24 · Revit tested: none yet in this skill.
> This file is **Stage B (placement)** for doors and windows. Prerequisites: verified types (`openings-families.md` A6) and the host walls modelled (`walls.md`). Rules: `building-logic.md` §2.1–2.3.

## 1. Scope
Place every door and window instance from the plans/keyplans and elevations: position along its host wall, level, sill, facing/hand, Mark and Comments; prove each one is hosted and cuts.

## B1. Where the positions and heights are
- **Plans / keyplans** for position and code (tags `P1`, `AW-04`, `D42`…). Tag positions from vector text with `-bbox` / `get_text("words")` + nearest number `[IMPORTED KPwBI-ARS]`; where vector coordinates are unreliable (nested transforms), raster crops with mm rulers `[IMPORTED KPwBI-ARS]`.
- **Elevations** for x positions (overlay check) and sill/head heights; schedule for default sill.
- Calibrate each sheet on its own grid (`drawing-interpretation.md` §4).

## B2. Instance table
mark (`DR-<code>-<lvl>-nn` / `W-<code>-<lvl>-nn`) · code → type · plan point (mm) · level · sill (windows) · **host wall** (row or id) · offset along the wall · fits within wall length? · facing side (exterior/room) · hand/swing · source (sheet, tag) · provenance.

## B2b. Clean the table before placing `[THEORY]` (KPwBI lessons applied before placing)
1. **Host each point:** nearest wall within ~900 mm whose bounding box spans the level `[IMPORTED KPwBI-ARS]`.
2. **Clamp along the wall** so the unit fits: half width + 200 mm from the wall ends `[IMPORTED KPwBI-ARS]`. A unit running into a wall end fails.
3. **Overlap check** along the same wall: doors vs windows, units vs each other; drop doubtful tags (keyplan leaders that end at a window glyph) and **list them**, don't guess (KPwBI removed 4) `[IMPORTED KPwBI-ARS]`.
4. **Counts per code vs schedule/keyplan.**
5. Split host walls? Never: merge collinear wall pieces first (walls whole) `[IMPORTED KPwBI-ARS]`.

## B3. Interpretation rules
- Exterior side = `Wall.Orientation`; door swing/hand from the plan arc; windows face out unless drawn otherwise.
- Codes in the drawing but not in the schedule → own type, LOW `[IMPORTED KPwBI-ARS]`.

## B4. Pilot one, check it in the next call
- Place one instance, then in a **separate later call** check it still exists, `FindInserts` lists it, host volume dropped, sill and position read back. Revit deleted doors at commit with "Can't make type" while the script said OK `[IMPORTED KPwBI-ARS]`. **Never create or edit types and place their instances in the same call:** windows placed that way stayed uncut (not in `FindInserts`, wall volume unchanged); re-placed in a new call they cut `[VERIFIED 2026-11-25, scratch model]`.
- **Open problem:** on 100 mm Generic walls (KPwBI Lantai Dasar) every door type vanished at commit (masonry frame depth 150/100/80 tried); the same families worked on 150/250/300 walls and a storefront `[OPEN]`. Test one door on each thin wall type before batching.

## B5. Place once `[IMPORTED KPwBI-ARS]`
1. **Never load/reload families and place in the same call.**
2. `doc.Create.NewFamilyInstance(pt, symbol, wall, level, StructuralType.NonStructural)`.
3. Set `INSTANCE_SILL_HEIGHT_PARAM` (windows) **every time**: placing with a point at level z gives sill 0 and ignores the type's Default Sill Height; copy it from the type (or the drawing) right after placing `[VERIFIED 2026-11-25, scratch model]`.
4. `doc.Regenerate()`, **then** `flipFacing()` if `FacingOrientation · wall.Orientation < 0` (or per the drawing), then `Regenerate()` again. Flipping before Regenerate leaves units uncut.
5. First placement after a load sometimes fails: delete and re-place.
6. Mark + Comments; per-instance try/catch; return `mark | id | result`; one level per call.
- MCP alternative `create_point_based_element` (hostWallId, facingFlipped) exists `[THEORY]`, not yet tried; prefer the script route until it is tested.

## B5b. Audit and repair
Per level: every insert in `host.FindInserts(true,true,true,true)` and host volume dropped `[IMPORTED KPwBI-ARS]`; persistence in a later call; overlaps along walls (bounding boxes) `[IMPORTED KPwBI-ARS]`; within wall length; sill/head vs elevation; facing; counts vs schedule. Uncut units: delete and re-place with the B5 order `[IMPORTED KPwBI-ARS]`.

## B6. Verification
Elevation overlay of x positions `[IMPORTED KPwBI-ARS]`; counts per code per level = keyplan; 100 % hosted and cutting; warnings not higher than before.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Hosted but uncut (FindInserts 0) | Placed in the same call as a family reload; flipped before Regenerate | Delete and re-place: place, sill, Regenerate, flip, Regenerate | [IMPORTED KPwBI-ARS] |
| Doors vanish at commit, script said OK | "Can't make type" on 100 mm Generic walls | Unresolved; test one per wall type; check in a later call | [OPEN] |
| Doors clash with windows | Keyplan leaders end at window glyphs | Overlap check; drop doubtful tags and list them | [IMPORTED KPwBI-ARS] |
| Door facing wrong | Raycast unreliable on open sides | Use model facts (exterior side / drawing) | [IMPORTED KPwBI-ARS] |
| Unit fails near a wall end | Unit runs past the wall end | Clamp half width + 200 mm from ends | [IMPORTED KPwBI-ARS] |

## Related
`openings-families.md`, `walls.md`, `building-logic.md`, `model-validation.md`.
