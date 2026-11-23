# Drawing interpretation — reading a structural drawing set

> Legend: see SKILL.md §8. `KPwBI` = KPwBI DIY Gedung Utama project (Revit 2026), imported field knowledge.
> Last reviewed: 2026-11-20 · Revit tested: n/a (this file is about drawings; PDF-tool items tested in Linux container)

## 1. Purpose and scope
How to read, cross-reference and extract data from structural drawings *before* touching Revit. Element-specific extraction rules live in each element file. Coordinate/level establishment lives in `grids-and-levels.md`.

## 2. Drawing types and what each is the authority for

| Sheet type | Typically authoritative for | Not reliable for |
|---|---|---|
| General arrangement / key plan | Layout, grid names, sheet index | Member sizes |
| Foundation plan | Footing/pile positions, mark tags | Footing depth (often in schedule/section) |
| Column layout + schedule | Column marks, sizes, stack changes | Base level (often missing) |
| Beam layout (per level) | Beam marks, positions, offsets, step zones | Section sizes if only tagged (check schedule) |
| Slab plan | Slab outline, tags, openings, falls | Thickness if tag-only (check slab schedule/detail) |
| Sections / elevations | Levels, heights, depths, step levels | Plan positions |
| Details / typical details | Sizes, edge conditions, build-ups, bar details | Locations |
| Schedules | Size/type per mark | Positions |
| Reinforcement drawings | Bar marks, spacing, cover | Concrete outline (use plan) |
| General notes | Concrete grade, cover, global rules, "typical unless noted" | — |

Rule: **a single drawing is never the complete source.** Position from plan, size from schedule/detail, height from section — and check them against each other.

### Typical sheet order of an Indonesian structural DED set `[IMPORTED KPwBI]`
Foundation (existing) → plans per floor (existing, then retrofit) → column plan + schedule → jacketing types and details → beam reinforcement details → beam strengthening → slab details (metal-deck sections) → roof truss plan + sections → connection details → canopy sheets → other structures (bridge, flagpole, green wall, remise canopy). Use it to find missing sheets quickly; do not assume every set follows it. Schedule vocabulary seen on real Indonesian sets `[VERIFIED 2026-11-20, sample sets DRC Kalimantan, RSUD Cakung, KPwBI GKU, Hunver OIKN]`:
- Table titles: `TABEL PENULANGAN` (DRC), `TABEL PEMBESIAN KOLOM K1 - K7A` (RSUD), `TABULASI PENULANGAN BALOK` (KPwBI), `TIPE KOLOM / TIPE BALOK` inside the table header, `DENAH TIPE KOLOM` (a plan that shows the types, Hunver), `DENAH TIPE PERKUATAN KOLOM` (retrofit column types, KPwBI).
- Column tables are grids of marks × level ranges (RSUD K1–K12 from PONDASI to ATAP; DRC "K2 LT.1–LT.2", "K2 LT.2 – LT. DAK ATAP"): **sizes change per level range**. Sizes are drawn as dimension numbers on the sketches, not written as "800x800".
- `CONTOH TABULASI` / `STANDAR DETAIL` = an *example* table on a standard-details sheet, not the project's schedule (KPwBI p10 false hit).
- Slab types can be named by thickness: `T12, T15, T20, T22` (DRC, "DETAIL PLAT LANTAI T15").
- Stair sheets mention `KOLOM/BALOK BORDES`: not the main schedule.
- The first pages usually hold `DAFTAR GAMBAR` (drawing index): read it first.
- Some pages have no extractable text at all (14 of 84 in RSUD): look visually or ask.
- Notes blocks give material grades: `MUTU BETON K-350`, `MUTU BESI ULIR BJTS fy=420 MPa` (DRC).

Sheet-title words: `Denah` = plan, `Potongan` = section, `Detail`, `Eksisting` = existing, `Bongkaran` = demolition, `Rencana` = proposed.

## 3. Phase-1 inventory procedure
1. List every sheet: number, title, revision/date, scale, page in file. `[THEORY]` Use `pdftotext -layout` for title blocks; `pdfinfo` for page count and size.
2. Classify each: existing / demolition / new; plan / section / detail / schedule; building zone covered.
3. Determine scale **per view** (titles lie; insets may differ — see §5) and units (mm vs m vs cm; check dimension strings).
4. Collect grid names/spacings, levels (FFL, structural slab top SFL), datum of each sheet group, typical-detail callouts.
5. Build the cross-reference map: plan view → sections (section markers) → details (detail bubbles) → schedules (marks).
6. Produce the **conflict / missing-information (RFI) list** before modelling. Template: `assets/examples/rfi-log-template.md`.

## 4. PDF tooling `[IMPORTED container 2026-11-20]` (poppler + pdfplumber 0.11 present)
- `pdftoppm -f N -l N -r 300 -png in.pdf out` — crops to read visually. ~400 dpi for labels, 500–900 dpi for overlays.
- `pdftotext -layout|-raw|-bbox` — text, sheet codes, tags. `-bbox` gives word positions.
- `pdfplumber` — vector `lines`, `rects`, `curves`, with `linewidth`/`stroking_color`/dash info. `[IMPORTED KPwBI]` an SVG conversion route dropped thin dashed and arc linework that pdfplumber kept.
- **Calibration is mandatory before any measurement:** `scripts/pdf_calibrate.py` (piecewise grid-to-grid; see `grids-and-levels.md` §5).
- `[LIMIT]` Vector text/labels are often outlined glyphs: tools return nothing. Read them visually at high dpi and re-check critical ones.
- `[LIMIT]` Scanned/raster PDFs have no vectors: measurement accuracy is limited to pixel resolution; calibrate on dimension ticks and state reduced confidence.

## 5. Interpretation lessons (all `[IMPORTED KPwBI]` unless tagged)
- **Line weights carry meaning, per project.** In that set: paired dashed lines (6.0) = beam faces; 7.0 = slab/building outline; 2.0 X-marks = voids; grey hatch = waterproofing. An X pattern in a slab cell was void marking, not bracing. *Always read the legend and measure line widths; never assume these values transfer.* `[THEORY]` for other projects.
- **Existing vs new:** a foundation plan titled "Eksisting" showed 4 caps belonging to a demolished frame. Ask for each element: remain / demolish / new.
- **Section labels pointing at end-on members:** a "WF250x125" leader pointed to an I-section drawn end-on (an eave beam running perpendicular to the section). Misreading it created 30 spurious posts and put 44 beams 950 mm high. Trace leaders to what they touch; ask "is this a cut member?".
- **Profile-letter tables** (A, B, C…): read the letter on *every* segment including extensions past supports.
- **Insets can be at a different scale than their title** (title 1:100, drawn 1:200). Calibrate on the inset's own dimension ticks.
- **Eccentric members are real** (beams 120 mm inside column centres; secondary beams at 1A−1200). Model as drawn.
- **Dilatation / expansion joints** (double thin line ~76 mm): find them first; nothing crosses them; each side is its own structure.
- **Slab outline** = the drawn thick line, not beam faces or grid guesses.
- **Heights absent from structural sheets** may be in architectural elevations/sections — state which discipline supplied them.
- **Datums differ between sheet groups** (a canopy group used L1 = −0.050; project = value + 2.300). Verify one known level per sheet group.
- **Plan vs dimensioned detail disagree** → the dimensioned sheet was used, conflict logged LOW CONFIDENCE (user-approved in that project; ask in yours).
- **Glyph-shape identification** (pile types A/B/C by letter shape: A has straight strokes, B/C have curves) was cross-checked against the sheet table — counts matched exactly. Always cross-check identification against a count table when one exists.
- **Slab thickness conflict** (table 120 vs detail 150 metal deck): asked the user; steel under metal-deck slabs sat at SFL − 150.
- **Edge beams drawn differently** `[VERIFIED RSUD]` (detection generalising to other sets: `[EXPERIMENTAL]`). Perimeter beams may not be drawn as a face pair:
  - *one-sided edge beam*: a single dashed face line running 1–4 pt beside the solid slab outline, no partner line. Width = the gap between the dashed line and the outline (≈150 or 300 mm on RSUD; e.g. Lt1 south edge, tag S1). Missing it made all S1 secondaries "float".
  - *outline-only edge beam*: tagged L1 / L2, drawn only as the outline (RSUD: 41 L1 on Lt1, 22 L1 + 5 L2 on Lt3 …). Position = outline as outer face: a guess, tag `LOW CONFIDENCE`.
  - *detection on the calibrated sheet*: long solid lines (> ~100 pt); short dashes (3–9 pt) with **no partner dash** within 8 pt; keep groups of ≥ 4 dashes parallel to a solid line, 0.5–4 pt from it, inside its extent. Read the dash line width from the sheet itself (0.71 pt on RSUD; never hard-code).
  - a one-sided line can also be a slab step or drop edge: check the tag beside it and any section.
- **Model it, then tag it** (user rule, stated forcefully on RSUD). If the only alternative is leaving a drawn element out, model it, estimating visually if necessary, and tag `LOW CONFIDENCE`. This covers elements drawn in an **unusual graphic convention**, not only elements missing a dimension. It does not conflict with "never invent dimensions": no dimension is invented; a drawn element's geometry is estimated and flagged.
- **Flush intent vs intentional eccentricity** `[VERIFIED RSUD]` (concept; the perimeter test is `[EXPERIMENTAL RSUD]`). On perimeter rows the plan often draws the beam's outer face on the columns' outer face: the beam is eccentric on purpose so the façade is flush. If columns come from the schedule and beams from the plan, they can disagree (≈185 mm on RSUD) and the beams stick out.
  - *Flush intent (snap it)*: beam off the column centre by > 40 mm, its face within ~300 mm of the column face on the same side, offset pointing **outward** (no other column beyond it within ~1.8–12 m in that direction, within ±4.5 m along the beam). Façade and edge beams.
  - *Intentional (leave it)*: interior eccentric beams (narrow B5 200 passing beside a column, stair and lift beams, beams at voids) and anything **drawn off-grid by a dimension**.
  - *Snap rule*: outer face = the **modelled** column's outer face (the schedule wins for column size and position); group the collinear run and use the outermost face so the beam stays straight (an 800 next to a 950 column: align to the 950); move only 8–320 mm; append `flush with outer column face (N mm)`. Snapping every eccentric beam was far too broad (55 + 9 conflicts on one floor).
  - U-shaped or stepped plans fool the "nothing beyond" test at re-entrant corners: review that list. If the column itself is wrong, snapping moves the error: decide first which drawing is right.
- **The plan's column outline can disagree with the column schedule/plan** (≈185 mm on RSUD, outline not even square). The schedule wins for the column; beams drawn relative to that outline keep their *relationship*, not their absolute coordinates `[VERIFIED RSUD]`.
- **The same beam detected twice** (duplicate rows) raises Revit's "identical instances" dialog: de-duplicate the instance table by type + collinear + overlapping before placing `[VERIFIED RSUD]`.
- **The user's words can name the wrong category** ("columns like these should sit flush" meant *beams*, RSUD). Resolve from the selection (`get_selected_elements`) and the drawing geometry, not the wording.
- **When the user points** (circles a screenshot / "these ones I selected"): `get_selected_elements` if available, then re-read that exact area at high dpi. First guesses were wrong twice.

## 6. Dimension inference hierarchy
1. Explicit dimension / schedule value → `EXPLICIT`
2. Related sheet (section, detail, schedule, architectural) → `EXPLICIT`/`DERIVED` (cite sheet)
3. Measured from calibrated vectors → `MEASURED`
4. Repeated / adjacent element → `ASSUMED`
5. Visual / proportional → `ASSUMED`, `LOW CONFIDENCE`

Drawn-but-undimensioned elements are modelled with best evidence and flagged (SKILL.md §3.4). Not-drawn elements are not modelled.

KPwBI examples, all tagged `LOW CONFIDENCE` `[IMPORTED KPwBI]`:
- Mezzanine knee-brace section not labelled → WF200x100 assumed.
- F–G void member depth unreadable → 170x400 assumed.
- Front roof block heights absent from structural sheets → taken from the architectural elevation and section.
- Pile-cap tops not given → set to the soffit of the deepest beam (columns.md §4).

## 7. Common failure cases
| Symptom | Cause | Fix |
|---|---|---|
| Whole model shifted by tens of mm | Single global scale instead of piecewise calibration | Re-calibrate per sheet per axis `[IMPORTED KPwBI]` |
| Wrong member count vs table | Misidentified glyphs/tags | Cross-check counts against schedule |
| Members in impossible places | Read a section cut as a plan element | Trace leaders; check cut direction |
| Using demolished geometry | Skipped sheet-title status check | Classify every sheet in Phase 1 |

## 8. Related
`grids-and-levels.md`, `project-setup.md`, element files, `workflows/drawing-analysis-workflow.md`.
