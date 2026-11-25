# Door and window families — from the schedule to placeable types (OST_Doors, OST_Windows)

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-25 (A1–A3 from the KPwBI sheets; A5 piloted) · Revit tested: Revit 2026 scratch project, 2026-11-25 (A5b, A5d).
> This file is **Stage A (types)** of `workflows/element-modeling-workflow.md` for doors and windows. Placement (Stage B): `openings-placement.md`. Doors and windows share one module because their schedules sit together and their families are built the same way.

## 1. Scope
Read the door/window schedule, catalogue every code, and make one placeable, **cutting** Revit type per code: use an existing type, duplicate a stock family, or build a family. Not here: curtain-wall panels, storefronts, louvres beyond a simple window family (ask).

## A1. Where the types are
- **Schedules:** `SCHEDULE PINTU nn`, `SCHEDULE JENDELA nn`, `JADWAL/SKEDUL PINTU JENDELA`, `TABEL KUSEN`, `DAFTAR PINTU`. KPwBI: A-8101..8110 doors, A-8111..8126 windows (Part4 p3–28); `find_schedules.py --element openings` puts all 26 at the top `[VERIFIED 2026-11-24]`.
- **Schedule layout (KPwBI)** `[VERIFIED 2026-11-25, samples]`: 1:50, landscape, **2–4 codes side by side** per sheet (a wide unit can take a whole sheet, and the next sheet may continue with its table only). Column per code: header row `TYPE` (circle with letter over number, e.g. D/42, AW/04, GP/01A, plus a title such as `STEEL DOOR DOUBLE SWING`), `FIGURE` (TAMPAK elevation with height chain, POTONGAN section, DENAH plan with width chain), then rows `LOCATION … QUANTITY : n UNITS`, `FRAME`, `LEAF / PANEL`, `HARDWARE` (sub-rows HANDLE, ESCUTCHEON, LOCKCASE, CYLINDER, HINGES, DOOR CLOSER / SYSTEM), `REMARKS` (fire rating, brands). Header words are text; **everything inside (codes, sizes, specs) is outlined**: render ~125 dpi to see the layout, then crop the figure and table at 190–260 dpi.
- **Codes on KPwBI:** doors D42–D65 (no D01–D41 in the architecture set), windows GP01A/GP01B/GP02–GP09 (glass partitions), AW01–AW29 (aluminium), plus screens K01 (krawangan), J01–J02 (jeruji) on the window sheets. GP01B sits on the last sheet, not next to GP01A.
- **Keyplans** (`KEYPLAN PINTU/JENDELA`, KPwBI A-8001..8012) say where each code is used: needed for the count and for Stage B. **Their tags are real text** (letter line + number line in one circle): pair them by position to count per code and floor (`drawing-interpretation.md` §3). One GP keyplan (A-8010) had no readable tags; one sheet's drawing title says PINTU while its title block says JENDELA.
- Elevations confirm sill/head heights and window rhythms; 1:50 details give frame sections.

## A2. Extract per code
code (P1, PJ-02, J3, AW-04, D42, BV1…) · door/window/louvre/partition/screen · description (single/double swing, sliding, fixed, projected) · **W × H (structural opening or frame outside? note which)** · sill height (windows) · frame material + section (e.g. aluminium 50×100) · leaf/panel + glazing (TG02…) · hardware (record only) · fire rating · location/rooms · **schedule quantity and keyplan count, side by side** · source sheet/page · provenance.

## A3. Catalog notes
**Traps found on the KPwBI schedules** `[VERIFIED 2026-11-25, samples]`:
- **Size basis = frame outside = wall opening:** text "Ukuran Opening 900 x 2400 mm" and the drawing shows leaf 800 + 2×50 frame. Vault doors say "WALL OPENING" and "CLEARANCE" separately: model the wall opening.
- **Order is not always W × H:** D51 text "UKURAN 3000 X 2300" is height × width; check against the figure.
- **Add the chains:** totals sometimes disagree with their parts (AW01 parts 1626 vs 1625, AW18 plan parts 6475 vs 6450) and elevation vs plan vs section disagree on 7 codes (e.g. AW05 2650 / 2600, AW11 3850 / 3750). Record both, RFI, never pick silently.
- **Many cells are blank:** QUANTITY blank or "-" on most codes, LOCATION blank on some, sills missing on about half the windows, one door (D57) has no height. Counts then come from keyplans; heights from sections/elevations.
- **Schedule quantity ≠ keyplan count** on 9 codes (D42 6 vs 3 tags …), location text names the wrong building on 3 windows (AW23/27/28), and one door (D64) is on no keyplan: RFI each.
- **One code, two things:** D43/D45 = swing or vault door + a sliding grille on a track; D42/D53–D55 include transoms and side lights; D65 is a door with a 650 sill. Decide family scope per code.
- **Not every code is a door/window:** GP partitions, frameless lobby glazing (D57, D58 9.15 m high, D60 7.5 m storefront), AW29 curtain module and screens K01/J01/J02 may be curtain walls or parked items: ask before building families.
- Existing items kept (D42 bulletproof door retouched, D62/D63 rolling doors) belong in the final-state model.

General rules:
- One Revit type per code (`<code> WxH` or `<code> - <desc> WxH`) `[IMPORTED KPwBI-ARS]`; same geometry used by two codes → still two types (codes are what the schedule counts).
- Codes on the keyplan/plan but not in the schedule: built as drawn, own type, LOW `[IMPORTED KPwBI-ARS]`.
- Codes in the schedule never used on a plan: list them; ask before skipping.
- Width/height basis must be consistent (opening vs frame vs leaf). If unclear, ask once and record.
- Ask the user the **detail level** once: "accurate size, approximate look" (KPwBI doors: stock families, no panels/transoms/sidelights, noted) vs "match the schedule figure" (custom families) `[IMPORTED KPwBI-ARS]`.

## A4. Map to what Revit has
`get_available_family_types` with `OST_Doors` / `OST_Windows`; list family, type, Width/Height. Status per code: `exists` / `duplicate` / `load` (user library) / `new family` / `blocked` (workflow A4). On this machine the standard content library was not found `[IMPORTED STR]`: ask for a library path before assuming `load`.

## A5. Create the types
**Default: the two supported core families in A5d (`KPW_Window`, `KPW_Door`), one type per drawing code** (`AW01 1625x1400`, Type Mark `AW01`). Codes they cannot represent are edge cases: improvise and flag them (A5d). The fixed 2-pane pilot (A5b) was the first step towards `KPW_Window`.

### Parametric family from the template `[VERIFIED 2026-11-25, scratch model]` (pilot: §A5b; script `scripts/revit/family_window_fixed_2pane.cs`)
1. Template: `Metric Window.rft` / `Metric Door.rft`. On this machine: `D:\ProgramData\Autodesk\RVT 2026\Family Templates\English\` (also English-Imperial, curtain-wall variants) `[VERIFIED 2026-11-25]`.
2. The window template already has type parameters **Width, Height, Default Sill Height** (+ Rough Width/Height), reference planes **Left, Right, Sill, Head, Center (Left/Right), Center (Front/Back), Exterior, Interior** (±100 mm), labelled dimensions driving them, and an **Opening Cut already locked to Left/Right/Sill/Head**: it flexes, so do **not** add a second opening `[VERIFIED 2026-11-25, template read]`.
3. Add what the shape needs: extra parameters (`Frame Width` 50, `Frame Depth` 100, formula parameters such as `Half Frame = Frame Width / 2`), extra reference planes (inner frame lines, mullions) each driven by a labelled dimension from a template plane.
4. Geometry = extrusions in the wall plane (sketch plane normal Y), then **lock every face that must move to its reference plane** (`FamilyCreate.NewAlignment(view, plane.GetReference(), face.Reference)` in an elevation view, geometry read with `ComputeReferences = true`). Unlocked faces stay put when Width changes: that is what makes a family "static".
5. **Flex test inside the family before saving:** for 3+ sizes from the catalog set Width/Height on the family type, `Regenerate`, read each solid's bounding box and compare with the expected edges (± 0.5 mm). Fail = do not save.
6. SaveAs to the family folder, close, load into the project, create one type per code (`Duplicate` + set Width/Height/Default Sill Height + `WINDOW_TYPE_ID` = code as Type Mark + Type Comments = sheet/provenance), then repeat the size check on placed instances.
- Family documents work from the MCP tool: `NewFamilyDocument` / `OpenDocumentFile` + own `Transaction`, `SaveAs`, `Close(false)`; one build step per call (≲ 4k chars) `[VERIFIED 2026-11-25]`.
- Labelled dimension: put the **template plane first, the new plane second**; labelling moves the free new plane `[VERIFIED 2026-11-25]`. Formula parameters (`Half Frame = Frame Width / 2`) can drive labels.
- Extrusion depth follows a parameter via `AssociateElementParameterToFamilyParameter(EXTRUSION_END_PARAM, Frame Depth)` `[VERIFIED 2026-11-25]`.
- Window template subcategories: Frame/Mullion, Glass, Sill/Head, Trim, Opening, Plan Swing, Elevation Swing `[VERIFIED 2026-11-25]`.

### A5b. Pilot result: fixed 2-pane window `[VERIFIED 2026-11-25, Revit 2026 scratch model "Project1"]`
- `KPW_Window-Fixed-2Pane.rfa` (frame 50×100, centre mullion, 8 mm glass): **16/16 face locks**, flex test **5/5** (AW01 1625×1400 / AW02 2650×1400 / AW17 1800×3150 / AW09 2700×1450, and Frame Width 70) all within 0.5 mm.
- In the project: types AW01, AW02, AW09, AW17 from the catalog; placed in a 150 mm test wall: widths, sills and heads read back exactly, all 4 in `FindInserts`, wall volume dropped by exactly Σ W×H×0.15 (8.4 → 6.0645 m³). Changing a type's Width/Height in the project resized the placed window and its hole; 0 warnings.
- Limits: panes are equal (AW03's 1095/1055 split is not reproduced: note it or add a `Pane Left` parameter); the Opening Cut is the template's, so the hole = Width × Height (frame outside), matching the KPwBI "Ukuran Opening" basis.
- Same family serves AW01, 02, 03, 09, 12, 17, 20, 24 (all fixed 2-pane). Next shapes: fixed 3-pane, projected leaf + lights, single/double steel door (`Metric Door.rft`).

### A5d. Supported core families (user decision 2026-11-25: fewer types, reliable)
Only these two families are "supported". Build them from the scripts, flex-test them, then make **one type per drawing code** in them.

| Family | Script | Covers | Parameters | Status |
|---|---|---|---|---|
| `KPW_Window` | `scripts/revit/family_window_core.cs` | fixed or operable aluminium windows and glass partitions, 1–6 equal pane columns, optional top and bottom light | Width, Height, Default Sill Height, Columns, Has/ Top Light Height, Has/ Bottom Light Height, Frame Width, Frame Depth | `[VERIFIED 2026-11-25]` 40 locks, flex 8/8, placed and checked in a project (AW04/AW18/AW21) |
| `KPW_Door` | `scripts/revit/family_door_core.cs` | single or double swing doors (steel, wood, glass), optional transom, vision panel, bottom louvre | Width, Height, Leaves, Has Transom + Transom Door Height, Has Vision Panel + size/bottom, Has Louvre + height/bottom/margin, Frame Width, Thickness, Frame Depth | `[VERIFIED 2026-11-25]` 47 locks, flex 8/8, sweep 101/120 committed, placed and checked (D46/D47/D52/D55) |

**Rules learnt building them** `[VERIFIED 2026-11-25]` (each one froze Revit or gave a wrong result once):
- **Every combination must stay valid, including hidden parts.** A hidden part's reference planes still solve; cap them with `if()` so no labelled dimension can go ≤ 0 (D55 vision 800 on one leaf pushed the hidden two-leaf panel to −100 → "Parameter VDaL has an invalid value", modal dialog, API frozen).
- **Park hidden parts inside the unit:** hidden geometry still counts in the bounding box (AW21 read 3550 wide instead of 750 until hidden mullions were parked at the frame).
- **Order when changing several values:** switch optional parts off → set sizes → switch parts on. In a family document each `FamilyManager.Set` regenerates at once, so an in-between state (transom taller than the door) fails even if the end state is fine; on project types it is solved at commit.
- **Test by committing, not only by rolling back:** a failure surfaces at commit; a rolled-back flex test passed the D55 case that later failed.
- A `FailuresProcessing` handler (`ProceedWithRollBack`) caught a commit-time failure without a dialog, but not failures raised inside `FamilyManager.Set`.
- **Keep bridge calls short** (one family step or ≤ ~24 regenerations): long sweeps hit the bridge timeout while Revit keeps working, which looks like a hang.
- **Create types in one call, place instances in the next:** windows placed in the same call that created their types stayed uncut (not in `FindInserts`); re-placed in a new call they cut. Confirms the KPwBI lesson.
- Reloading a changed family = delete the Family (its types and instances go too), load, recreate types, place in a later call.

Mapping rules: opening (projected/casement) leaves are not modelled, so record them in the type's `Operation` and Comments. A glass door uses `KPW_Door` with a vision panel almost the size of the leaf. Codes that differ only in swing direction are separate types in the same family, with the hand set at placement. Unequal panes → equal panes + a note (LOW).

**Anything the two families cannot represent = an edge case.** At run time:
1. Do not stop. Choose the closest reasonable build yourself:
   - the core family with the nearest settings;
   - a curtain wall with door panels, for storefronts and curved or corner glazing;
   - a stock family duplicate;
   - a simple one-off family that has the right opening size and cuts the wall.
2. The **opening size, sill and host must still be right** and the wall must be cut; only the look may be approximate.
3. Mark it: type Comments and element Comments `IMPROVISED: <what was done> | <code> | <sheet>` and LOW CONFIDENCE.
4. Log it in the project log (Architecture → "Improvised door/window types") and add one line to `lessons-learned.md` (`#openings-edge`), so it can become supported later (A5c lists the known ones).

### A5c. Edge cases seen in the sample sets (2026-11-25) and how to support them
Drawing facts `[VERIFIED 2026-11-25, samples]`; the support column is `[THEORY]` until piloted like A5b. Sets: KPwBI DIY, DRC Kalimantan (`4.DRC_ARSITEKTUR.pdf` AR-709..728, text), Tower 4 ITS (`001+DED+ARSITEKTUR+COMPILE.pdf` p98–110, scanned), Bandara Hang Nadim (`DED Architecture.pdf`, schedules p720–721, 736, 751–756, 780, 787, 794 for utility buildings, scanned), Hunver (no schedule), RSUD (architecture folder has no schedule).

| Case | Seen in | Support |
|---|---|---|
| Pane / leaf count grows with width | DRC W1/W2/W3 (1, 2, 3 columns, same rows); Tower PL1 4 leaves vs PL2 8 leaves | Integer `Columns` parameter driving an array of mullions/leaves, else one family per count |
| Unequal panes | KPwBI AW03 1095/1055 | `Pane Left` width parameter, other pane takes the rest |
| Optional transom, side light, top/bottom lights, vision panel | KPwBI D53/D54/AW04; DRC SD2 (150×400 vision panel); Bandara DW1/DW2/DW3 | Yes/No visibility + height/width parameters per part, all on reference planes |
| Same geometry, only the swing direction differs, two codes | DRC SD1 (opens in) vs SD1A (opens out) | One family, two types (codes stay), set facing/hand at placement from the code |
| Louvre infill instead of glass | DRC BV (bouven), Bandara G1/G2 (steel grille "windows"), KPwBI D46/D48/D50 louvres, Bandara double door with louvre transom | Infill = glass / louvre / solid parameter; louvre as a panel with blade pattern, not modelled blades |
| Several units ganged in one code | Tower BV2 (3 windows, double 50+50 mullions) | One family with `Units` count, or place N instances: ask |
| Sliding window (panes in two tracks) | Tower J2B | New family type: two leaves offset in depth, overlap parameter |
| Sliding door: surface track, pocket, automatic, grille on a track wider than the opening | Bandara DW3; DRC DW19 (automatic); KPwBI D43/D44/D45 (track 3800–6800), D58 | New family type; track/box may extend past the opening: model it as family geometry, cut = opening only |
| Folding / bifold door | Tower PL1, PL2 | New family type; leaf count as above, closed position drawn |
| Rolling door / shutter with box above | KPwBI D62/D63; Bandara RD1 5000×5000; DRC rolling shutter (AR-711) | Simple family: opening + curtain panel + box above head (box height parameter) |
| Door with a sill (raised) | KPwBI D65 shaft door at 650 | Door family with a `Sill` offset parameter, or a window family: decide once |
| Curved / corner-wrapping glazing with doors in it | DRC DW1 (arms 7976 and 7840, curve R3020, two double doors) | Not a hosted family: curtain wall on a curved/L wall with door panels |
| Large frameless glazing with doors, posts | DRC DW2 (7980), DW19, DW20; KPwBI D57/D58/D60 | Curtain wall (storefront) with door panels; ask before building a family |
| Screens / grilles that are not openings | KPwBI K01, J01, J02 | Parked unless asked |

Reading edge cases `[VERIFIED 2026-11-25, samples]`:
- **Scanned sets** (Tower 4, Bandara): no text layer, slight skew, approval stamps and signatures printed over dimensions; read at ≥ 200 dpi and flag numbers hidden by stamps LOW. Find schedules through the drawing index (Bandara's index numbers = PDF page numbers), then thumbnail contact sheets.
- **Layouts differ:** KPwBI columns per code with FRAME/LEAF rows; DRC row-table (`KUSEN, PINTU, JENDELA, BOUVEN, HARDWARE, KACA, LOUVRE, SEALANT, AKSESORIS`, text-searchable); Tower 4 one code per sheet at 1:20 with a `KODE … Jumlah` box (count blank); Bandara `TYPE / LOCATION / HARDWARE / MATERIAL` rows under 2–3 codes.
- **False friends:** "SAND BLAST STICKER" (frosted film) is not a blast-rated door; "BOUVEN" is a louvre / vent, not a window.
- **No schedule at all** (Hunver basic design): sizes come from plans and elevations (`MEASURED`, LOW); codes may be missing too.
- **Plan vs elevation mismatches occur in every set** (Bandara DW3 plan 3350 vs elevation 3500; G2 section 2900 vs elevation 2800): always add both chains.

### Duplicate a stock family (quick fallback) `[IMPORTED KPwBI-ARS]`
Duplicate stock symbols (`M_Door-Passage-Single-Flush`, `M_Window-Fixed` …) per code, set `DOOR_WIDTH` / `DOOR_HEIGHT` (windows: `WINDOW_WIDTH` / `WINDOW_HEIGHT` `[THEORY]`), name `<code> - <desc> WxH`. Duplicate in one call, set sizes in the next. Right size, wrong look (no panes/transoms): say so.

### Static family from the template (old KPwBI method, fallback only) `[IMPORTED KPwBI-ARS]`
1. `app.NewFamilyDocument(<Metric Window.rft>)` in its **own** Transaction (not the tool's): `EditFamily` fails inside the tool transaction.
2. FamilyManager: Width, Height, Default Sill; frame 50×100; glass on a Glass subcategory; fixed geometry.
3. **Must contain an Opening cut:** `fd.FamilyCreate.NewOpening(hostWall, curveArray)` with a rectangle over the frame extents. Without it the window sits in the wall uncut ("Can't make cut-out").
4. **Wide units (> ~4 m):** first extend the template host wall (LocationCurve to ±6 m, height 4 m) and Regenerate, THEN set Width/Height, else "Can't make cut-out" dialogs drop the cut.
5. SaveAs to the family folder (`JENDELA_<code>.rfa`; KPwBI kept `REVIT\FAMILIES\Jendela\`), Close, delete `.0001.rfa` backups.
6. **Reopen the file and count Opening elements** (must be ≥ 1).
7. Max 2 families per call. Load in a separate call from placing.
- Family folder for this skill: ask at first use; default `<repo>/families/<Doors|Windows>/` (git-ignored).
- Template path: Revit 2026 templates are on **D:** here (`D:\ProgramData\Autodesk\RVT 2026\Family Templates\English\`), not C: (C: only had Steel Connections templates) `[VERIFIED 2026-11-25]`. On another machine search both drives before asking.
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
