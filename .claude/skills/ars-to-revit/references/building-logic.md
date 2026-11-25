# Building logic — hosting, joins, enclosure, heights, ARS vs STR

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24 · Revit tested: none yet in this skill.

## 1. Scope
The architectural equivalent of the STR skill's "nothing floats": rules every element must satisfy *as a building*, plus the checks that prove them. Element files apply them; `model-validation.md` checks them.

## 2. Rules
1. **Every door and window is hosted in a wall** (or curtain wall) and lies **within its length**: the leaf/frame plus a margin fits between the wall ends. A window running into a wall end fails to place `[IMPORTED KPwBI-ARS]`. Clamp rule used on KPwBI: half width + 200 mm from the ends `[IMPORTED KPwBI-ARS]`.
2. **Every insert cuts its host.** It appears in `host.FindInserts(true,true,true,true)` and the host volume dropped `[IMPORTED KPwBI-ARS]`. An insert that does not cut is a failure, not a cosmetic issue.
3. **Walls whole, inserts cut.** Model walls as continuous runs (merge collinear pieces of the same type/level/height that touch) and let the families cut the openings. Do not split walls around openings `[IMPORTED KPwBI-ARS]`.
4. **Walls join cleanly and close into rooms.** Wall ends meet exactly (L, T, X joins); no gaps, no overlaps, no stubs. Each room drawn on the plan is a closed loop of wall faces (or room separation lines where the drawing shows an open boundary) `[THEORY]`.
5. **Walls sit on the floor below and reach the level/element above** as drawn: base = level (+ offset), top = level above, beam soffit, or slab underside per the section. No wall hangs in the air or pokes through the slab above `[THEORY]`.
6. **Floors sit inside the wall boundaries** they belong to: architectural finish floors stop at the wall finish face (or run under walls, by project convention: decide once, record it); no floor edge visible past an exterior wall face. A slab edge beyond the wall face showed inside niches on KPwBI `[IMPORTED KPwBI-ARS]`.
7. **Ceilings sit inside room boundaries at the drawn height** and below the structure above (beam soffit, slab underside, ducts if modelled) `[THEORY]`.
8. **Roofs rest on their supports:** wall tops, ring beams, trusses or purlins from STR; eave and ridge heights match the section `[IMPORTED KPwBI-ARS]`.
9. **No tiny overlaps.** New walls must sit exactly on existing faces; 1–4 mm overlaps raised modal dialogs on KPwBI `[IMPORTED KPwBI-ARS]`.

## 3. Host table (planning, before placing)
| Element | Valid host / support | Planning column |
|---|---|---|
| Door, window | wall (id or table row), within length, correct side | `host_wall`, `offset_along`, `facing` |
| Wall | level below, top constraint per section | `base_level`, `base_offset`, `top` |
| Floor | bounded by walls of that level | `boundary_walls` / outline source |
| Ceiling | room boundary, below structure | `room`, `height`, `structure_above` |
| Roof | wall tops / STR members | `supports`, `eave_z`, `ridge_z` |

## 4. Heights (height chain)
Heights come from **sections and elevations**, never from guesses: FFL per level → wall base; wall top from the section (level above, slab underside, beam soffit, parapet top); sill and head heights from the schedule and elevations; ceiling height from the ceiling plan / section; eave and ridge from the section. Record the chain in the project log before placing `[IMPORTED KPwBI-ARS]` (method) / `[THEORY]` (wording).

## 5. Architecture vs structure consistency
Check, never rank: column sizes and positions vs wall thickness and finishes; SFL vs FFL; beam soffit vs ceiling height and door head; slab edge vs exterior wall face; roof underside vs truss/purlin top. List differences and ask (SKILL.md §5).

## 6. Order of work (dependency)
levels/grids → STR check → walls (types, then walls, joins) → floors → door/window families → door/window placement → ceilings → roofs → audit. Window-dependent items (facade work, niches) must be regenerated if windows move `[IMPORTED KPwBI-ARS]`. Deleting a host wall deletes its inserts: capture their data first and re-place `[IMPORTED KPwBI-ARS]`.

## 7. Checks
`model-validation.md` checks 3–8 implement these rules. `[OPEN]` a read-only checker script (`scripts/revit/check_building_logic.cs`): inserts hosted/cutting/within length, wall end gaps, floors outside walls. Write and test it on a scratch model.

## Related
`walls.md`, `openings-placement.md`, `floors.md`, `ceilings.md`, `roofs.md`, `model-validation.md`.
