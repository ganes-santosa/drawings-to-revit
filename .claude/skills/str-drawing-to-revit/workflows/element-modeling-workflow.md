# Element modelling workflow — the core procedure (columns, beams, slabs, foundations, roof)

Every element route follows the same three stages, in order. **Do not start placing until Stage A has passed its gate.** The element reference (`references/<element>.md`) supplies the element-specific details for each step; this file is the order and the gates.

```
Stage 0  Scope and prerequisites
Stage A  TYPES      find the schedule → catalog → map to Revit → create → verify (gate)
Stage B  PLACEMENT  find the layout → instance table + supports → clean the table → pilot one → place once → audit and repair → verify (gate)
Stage C  CLOSE-OUT  log, learn, report
```

---

## Stage 0 — Scope and prerequisites
1. **Scope** from the task text: which element, levels, zones, marks. Confirm existing / demolished / new status of the sheets involved.
2. **Prerequisites exist in Revit:** levels, grids, units and the coordinate conversion (else run `setup`). Check the connection with the read-only probe (`revit-api-and-automation.md` §3) or `get_current_view_info`, never `say_hello` (its modal dialog blocks the API, seen 2026-11-24 in the architecture skill `[IMPORTED ARS]`). If Revit is not connected, stop and tell the user.
3. **Read** the element reference and `references/building-logic.md`.
4. **Read the project modelling decisions** from the project log (beam segmentation, slab segmentation, column stacks). If they are missing, ask them now (`project-setup.md` §3 step 5b) before Stage B.

---

## Stage A — Types (make every type accurately before placing anything)

### A1. Find the type tables
- Look for the schedule in the drawing folder yourself first: `python ${CLAUDE_SKILL_DIR}/scripts/find_schedules.py <drawing folder or pdf> --element <columns|beams|slabs|foundations|roof>`. It lists the pages whose text matches schedule keywords (English and Indonesian: SCHEDULE, TABEL, DAFTAR, TYPE, PENULANGAN, KOLOM, BALOK, PELAT, PONDASI, ...), with the matching lines.
- Open the top candidates visually (render the page at 200–400 dpi) and confirm which is the real table. On the sample sets the right page was in the top 1–3 for columns in 3 of 4 sets; beams and slabs were often missed because their tables were outlined text `[VERIFIED 2026-11-20]`. The script is a shortlist, never the answer.
- Read the drawing index (`DAFTAR GAMBAR`, flagged by the script) for sheet titles when the search misses.
- If nothing is found, or several candidates conflict, **ask the user to point to the sheet/page** (AskUserQuestion with the candidates as options).
- If the set has **no schedule** for this element, sizes come from plan tags (`B1 300x600`), sections or typical details. Record that the type source is not a schedule.
- Note the sheet number, revision and page. Use the **latest revision**; if two revisions disagree, log a conflict.

### A2. Read the table and extract every type
For each row, extract what the table gives (element reference §A lists the fields per element):
- drawing mark (K1, B2, S1 …) and any level range it applies to;
- dimensions (b × h, profile name, thickness, diameter, depth …), in mm;
- material / grade (fc' 25 MPa, K-300, BJ 37, …) if given;
- other properties if given (reinforcement summary, finish, notes). Reinforcement is recorded, not modelled, unless the task asks for rebar.

Read labels at 300–400 dpi; outlined text is often not machine-readable (`drawing-interpretation.md` §4). Re-read any digit you are unsure of.

### A3. Reconcile and catalog
1. **Marks on the plans vs marks in the table:** every mark used on a layout plan must exist in the table, and every table row should be used somewhere. List both kinds of mismatch.
2. **Same mark, different size by level** (e.g. K1 = 600×600 at L1, 500×500 at L3): keep one catalog row per mark per level range.
3. **Cross-check** the table against sections and details (a section showing a 700-deep beam tagged B2 = 600 deep is a conflict). Never resolve silently (SKILL.md §5).
4. **Decide the Revit type identity.** Default: **one Revit type per unique geometry + material**, named after its size, listing the marks it serves (KPwBI style: `PELAT BETON 120mm (S1/S2/S3)`). The drawing mark goes on each instance (Comments, and Mark pattern). If the project wants one type per drawing mark instead, ask once and record the choice.
5. Write the **type catalog** (`assets/examples/type-catalog-template.csv`; save in the project log folder). One row per drawing mark per level range, with: category, mark, level range, dimensions, material, source sheet/page, provenance, Revit family, Revit type name, status.

### A4. Map the catalog to what Revit has
1. Inventory the project: `get_available_family_types` with the element's category (`OST_StructuralColumns`, `OST_StructuralFraming`, `OST_Floors`, `OST_StructuralFoundation`, `OST_Truss` for roof trusses), or a collector script. List family, type, key dimension parameters, material. Roof trusses: if no matching truss types exist, ask whether to make them first (recommended) or let the user load their own (`roof-framing.md` A4b).
2. For each catalog row, set the status:
   - `exists`: a type with exactly these dimensions and material already exists → use it;
   - `duplicate`: a suitable family exists but not this size → duplicate a type of it;
   - `load`: the family exists in a library the user can point to (steel profiles usually come with a type catalog) → load only the needed types;
   - `new family`: no suitable family anywhere → build one from a template;
   - `blocked`: cannot be made → ask (DirectShape only as a flagged last resort, or as the project convention, e.g. KPwBI foundations).
3. Never use a "close enough" size silently. A substitution is `LOW CONFIDENCE` and needs the user's OK.

### A5. Create the types
Order of preference: **exists → duplicate → load → new family → DirectShape (ask)**. Element-specific parameter names are in each reference §A.
- **Duplicate** (`revit-families.md` §3): `symbol.Duplicate("<name>")`, then set dimensions **in a separate call**, then set material and Type Mark. One concern per script; try/catch per type; return `name | id | result`.
- **System families (floors):** duplicate a floor type and edit its compound structure (layer thickness, material, structural layer) — `slabs.md` §A.
- **Load from library:** ask the user for the library path (do not assume one exists; on this machine the standard Revit content library was not found). Load only the needed types (`document.LoadFamilySymbol(path, typeName)` for type-catalog families) `[THEORY]`.
- **New family from scratch:** start from the matching template (`Metric Structural Column.rft`, `Metric Structural Framing - Beams and Braces.rft`; found on this machine under `C:\ProgramData\Autodesk\Revit Steel Connections 2026\en-UK\Family Templates\` `[VERIFIED exists]`). Build it with parameters for every dimension (b, h, …) and a structural material parameter, then save it to the **family folder** and load it. Family folder: ask the user at first use, default `<repo>/families/<Category>/`, and record the choice in the project log (`.rfa` files are git-ignored). Creating a family through `send_code_to_revit` is `[OPEN]` (the host keeps a transaction open; KPwBI could not edit family documents). If it fails, ask the user to create the family from the template by hand, with exact parameters.
- **Materials:** find the material by name (`FilteredElementCollector(document).OfClass(typeof(Material))`). If missing, propose a name (e.g. `Beton fc' 25 MPa`) and create it only after the user agrees.
- Naming: follow the project's existing names first (KPwBI examples in `revit-families.md`). No AI name in type names.

### A6. Verify the types — GATE
Read every created/used type back from Revit and compare to the catalog:
- every catalog row has a Revit type id (status not `blocked`);
- dimensions equal the catalog exactly (mm, read back from the type parameters, not from the name);
- material set as catalogued; category correct; type is active/placeable (`symbol.IsActive` or activate);
- every mark that appears on the layout plans resolves to a type.

Report the table (`mark | type | dims ok | material ok | id`). **Do not start Stage B until this passes** or the user accepts the listed exceptions.

---

## Stage B — Placement (place every instance accurately)

### B1. Find the layout drawings
Layout plans per level for this element, plus sections/details that give heights. Calibrate each plan sheet before measuring (`grids-and-levels.md` §5). Classify sheet status (existing / demolished / new).

### B2. Build the instance table
One row per instance: mark → catalog type, plan position (grid intersection + dimensioned offsets, or calibrated measurement), level, base/top or top elevation, orientation/rotation, **supports** (what each end or base sits on, `building-logic.md` §3), source sheet, provenance (`EXPLICIT / DERIVED / MEASURED / ASSUMED`). Element-specific columns: each reference §B.

### B2b. Clean the table (columns, beams and slabs: required)
Columns: de-duplicate, size from the schedule, stacks continuous, stack alignment, base support, top (`columns.md` B3b).

Slabs: generate outlines from real face lines, clean loop artifacts, snap edges to edge-beam faces, clean again, pre-build audit (`slabs.md` B2b). Build beams first.

Beams: before placing anything, clean the instance table in fixed order: de-duplicate → add missing edge/tie beams → resolve ends to supports → flush intent → merge runs then apply the segmentation mode → set joints → check the table (`beams.md` B2b). Place columns first so the table uses the columns as modelled.

### B3. Cross-check before placing
- **Defaults vs drawings (SKILL.md §3.12):** for every reference rule or convention used to fill the table, check that this project's drawings do not say otherwise. List the defaults applied (rule, where it came from, which rows) in the project log as `ASSUMED`; anything the drawings contradict follows the drawings.
- Counts per mark vs the schedule / plan totals.
- Every instance's type is in the verified catalog (Stage A).
- Every support cell filled, or the member is a drawn cantilever (Comments `CANTILEVER`).
- Heights follow the height chain: slab top → beam top → column top/base → cap top.
Unresolved items → log and ask before placing them.

### B4. Pilot one instance
Place **one** typical instance. Read back: location (mm), level, offsets, type, orientation, bounding box / solid position vs location line. Compare with the drawing. Fix the method until it is exactly right; a new method gets documented (Stage C).

### B5. Batch
- One level or one group per call; scripts ≲ 4k characters.
- **Supports first:** foundations/columns → primary beams → secondary beams → slabs; roof columns → rafters/trusses → purlins.
- Every instance gets its Mark and Comments (sheet, drawing mark, provenance, `LOW CONFIDENCE`, `CANTILEVER`).
- try/catch per instance; return `id | mark | result`.
- **Re-runnable:** skip rows whose Mark already exists (`revit-api-and-automation.md` §5). After a timeout or modal dialog, count what committed, then re-run the same batch; run `scripts/revit/find_duplicates.cs`.
- **Log after every block:** element ids, Marks, counts, tags and group sizes in the project log. After a crash or power cut, compare the reopened file with the log element by element, re-apply only the missing blocks, and compare with the last audit's counts `[VERIFIED RSUD]`.

### B5b. Audit and repair (columns, beams and slabs: required)
Columns: `find_duplicates.cs`, `audit_columns.cs`, `check_connectivity.cs` (`columns.md` B5b).

Slabs: the 12-check slab audit on every level after every change; classify beams sticking out before fixing; re-compute dak on the levels below (`slabs.md` B5b, B6).

Beams: after each floor is placed, audit it and repair only what the audit lists (`beams.md` B5b). If the table was cleaned well (B2b), this pass should find little.

Any repair that moves, resizes or re-heights an element: re-check what rests on it (`building-logic.md` §7) before closing the floor.

### B6. Verify the placement — GATE
1. Connectivity: `scripts/revit/check_connectivity.cs` → 0 unexplained floating ends / unsupported columns.
2. The element reference §B verification list (positions, elevations, orientation, counts).
3. `document.GetWarnings()` grouped by description; duplicates and marks blank/duplicated (`scripts/revit/find_duplicates.cs`).
Fix model errors, re-run the failed checks. Drawing discrepancies are reported, not "fixed".

---

## Stage C — Close-out
1. **Log** to the project log: type catalog (final), counts modelled vs expected, assumptions, conflicts, not-modelled + why.
2. **Learn:** anything that failed, surprised, or worked for the first time → update the element reference with a status tag and evidence, `lessons-learned.md`, and `troubleshooting.md` for new failures (SKILL.md §8).
3. **Report** per SKILL.md §7, short: modelled, not modelled, assumptions, open questions, checks run, one next step.
