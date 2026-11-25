# Door and window families — from the schedule to placeable types (OST_Doors, OST_Windows)

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24 · Revit tested: none yet in this skill.
> This file is **Stage A (types)** of `workflows/element-modeling-workflow.md` for doors and windows. Placement (Stage B): `openings-placement.md`. Doors and windows share one module because their schedules sit together and their families are built the same way.

## 1. Scope
Read the door/window schedule, catalogue every code, and make one placeable, **cutting** Revit type per code: use an existing type, duplicate a stock family, or build a family. Not here: curtain-wall panels, storefronts, louvres beyond a simple window family (ask).

## A1. Where the types are
- **Schedules:** `SCHEDULE PINTU nn`, `SCHEDULE JENDELA nn`, `JADWAL/SKEDUL PINTU JENDELA`, `TABEL KUSEN`, `DAFTAR PINTU`. KPwBI: A-8101..8110 doors, A-8111..8126 windows (Part4 p3–28); `find_schedules.py --element openings` puts all 26 at the top `[VERIFIED 2026-11-24]`.
- **Schedule layout (KPwBI):** one or more codes per sheet, each with FIGURE (tampak/denah/potongan of the unit), TYPE, LOCATION, FRAME, LEAF/PANEL, HARDWARE, REMARKS. Header words are text; **sizes and codes are outlined: read them visually at 300 dpi** `[VERIFIED 2026-11-24]`.
- **Keyplans** (`KEYPLAN PINTU/JENDELA`, KPwBI A-8001..8012) say where each code is used: needed for the count and for Stage B.
- Elevations confirm sill/head heights and window rhythms; 1:50 details give frame sections.

## A2. Extract per code
code (P1, PJ-02, J3, AW-04, D42, BV1…) · door/window/louvre · description (single/double swing, sliding, fixed, casement) · **W × H (structural opening or frame outside? note which)** · sill height (windows) · frame material + section (e.g. aluminium 50×100) · leaf/panel + glazing (TG02…) · hardware (record only) · fire rating · location/rooms · count per level (from keyplan) · source sheet/page · provenance.

## A3. Catalog notes
- One Revit type per code (`<code> WxH` or `<code> - <desc> WxH`) `[IMPORTED KPwBI-ARS]`; same geometry used by two codes → still two types (codes are what the schedule counts).
- Codes on the keyplan/plan but not in the schedule: built as drawn, own type, LOW `[IMPORTED KPwBI-ARS]`.
- Codes in the schedule never used on a plan: list them; ask before skipping.
- Width/height basis must be consistent (opening vs frame vs leaf). If unclear, ask once and record.
- Ask the user the **detail level** once: "accurate size, approximate look" (KPwBI doors: stock families, no panels/transoms/sidelights, noted) vs "match the schedule figure" (custom families) `[IMPORTED KPwBI-ARS]`.

## A4. Map to what Revit has
`get_available_family_types` with `OST_Doors` / `OST_Windows`; list family, type, Width/Height. Status per code: `exists` / `duplicate` / `load` (user library) / `new family` / `blocked` (workflow A4). On this machine the standard content library was not found `[IMPORTED STR]`: ask for a library path before assuming `load`.

## A5. Create the types
### Duplicate a stock family (fastest; doors on KPwBI) `[IMPORTED KPwBI-ARS]`
Duplicate stock symbols (`M_Door-Passage-Single-Flush`, `M_Door-Passage-Double-Flush`, `M_Door-Passage-Single-Vision_Lite`) per code, set `DOOR_WIDTH` / `DOOR_HEIGHT` (windows: `WINDOW_WIDTH` / `WINDOW_HEIGHT` `[THEORY]`), name `<code> - <desc> WxH`. Duplicate in one call, set sizes in the next.

### Build a family from the template (windows on KPwBI) `[IMPORTED KPwBI-ARS]`
1. `app.NewFamilyDocument(<Metric Window.rft>)` in its **own** Transaction (not the tool's): `EditFamily` fails inside the tool transaction.
2. FamilyManager: Width, Height, Default Sill; frame 50×100; glass on a Glass subcategory; fixed geometry.
3. **Must contain an Opening cut:** `fd.FamilyCreate.NewOpening(hostWall, curveArray)` with a rectangle over the frame extents. Without it the window sits in the wall uncut ("Can't make cut-out").
4. **Wide units (> ~4 m):** first extend the template host wall (LocationCurve to ±6 m, height 4 m) and Regenerate, THEN set Width/Height, else "Can't make cut-out" dialogs drop the cut.
5. SaveAs to the family folder (`JENDELA_<code>.rfa`; KPwBI kept `REVIT\FAMILIES\Jendela\`), Close, delete `.0001.rfa` backups.
6. **Reopen the file and count Opening elements** (must be ≥ 1).
7. Max 2 families per call. Load in a separate call from placing.
- Family folder for this skill: ask at first use; default `<repo>/families/<Doors|Windows>/` (git-ignored).
- Template path on this machine: **no door or window `.rft` under `C:\ProgramData\Autodesk`** (only Revit Steel Connections structural templates) `[VERIFIED 2026-11-24]`. Ask the user for `Metric Window.rft` / `Metric Door.rft` (or their office template folder) before building; duplicating stock families already in the project needs no template `[OPEN]`.
- Repeated modules with stepped niche voids inside the family worked (`KPW_AW-29 Window Niche.rfa`) `[IMPORTED KPwBI-ARS]`.

### Reload a changed family `[IMPORTED KPwBI-ARS]`
`LoadFamily` does not overwrite: delete the Family element (no instances) and load again; re-place instances in a later call.

## A6. Gate
Per code: type id, Width/Height (and sill default) read back from parameters, category right, `symbol.IsActive` (activate), family contains an Opening (built families), unique Type Mark. Every keyplan code resolves to a type. Report `code | type | W×H ok | cut ok | id`. **Do not start placement until this passes.**

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Window in wall, no cut | Family has no Opening | `NewOpening` rectangle in the family; recount after reopening | [IMPORTED KPwBI-ARS] |
| "Can't make cut-out", cut lost on wide window | Template host wall too small | Extend host wall first, then size | [IMPORTED KPwBI-ARS] |
| Family update not taking | LoadFamily over an existing family | Delete Family, then load | [IMPORTED KPwBI-ARS] |
| `EditFamily` fails | Tool transaction already open | `NewFamilyDocument`/`OpenDocumentFile` + own Transaction | [IMPORTED KPwBI-ARS] |

## Related
`openings-placement.md`, `types-and-materials.md` §5 (names), `revit-api-and-automation.md` (family documents).
