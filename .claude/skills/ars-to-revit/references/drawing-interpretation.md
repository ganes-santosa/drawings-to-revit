# Drawing interpretation — reading architectural sets, finding sheets, calibrating, measuring

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-24 · Real sets looked at: KPwBI DIY (Part1–4), RSUD Cakung ARSITEKTUR, Hunver OIKN 390B.

## 1. Scope
How to read an architectural DED set: which sheet answers which question, how to find sheets and schedules, how to calibrate and measure. Element-specific reading rules live in each element file §A1/§B1.

## 2. Sheet types and what each is for `[IMPORTED KPwBI-ARS]`
| Sheet (Indonesian) | Use it for |
|---|---|
| Denah (plan, 1:100–1:400) | wall lines (pairs of parallel vector lines; centre and thickness from the pair), openings, grids, level marks, door/window tags |
| Tipe dinding (wall-type plan) | which wall type sits where (KPwBI A-42xx) |
| Finishing lantai / dinding / plafond plans | floor finish, wall finish and ceiling type + height per room (KPwBI A-40xx, A-41xx, A-43xx) `[VERIFIED 2026-11-24 titles found by script]`; KPwBI wall-finish legends (W1… codes) are real text and pair with their codes by position `[VERIFIED 2026-11-25, samples]` |
| Tampak (elevation) | window/door x positions (overlay check), sill/head heights, bands, top levels, finish legend codes |
| Potongan (section) | floor-to-floor, roof pitch per direction (can differ by direction: 34.9° vs 29.4° on one KPwBI building), eave/fascia heights, ceiling heights |
| Parsial / detail 1:50, 1:20 | exact depths, steps, wall build-ups, frame sections (read at 300 dpi) |
| Keyplan pintu / jendela | where each door/window code sits (KPwBI A-80xx, 1:400 with leaders; some leaders end ambiguously: check against the elevation) |
| Schedule pintu / jendela | code, W × H, sill, frame, leaf/panel, hardware, glazing (KPwBI A-81xx) |
| Bongkaran / Eksisting | renovation: what stays and what goes. Read before modelling a renovation element |
| Gambar 3D / render | design intent (recessed vs projecting, which faces are stone vs paint); used to correct misreadings |
| STR sheets / STR link | alignment reference for columns and anything structural-adjacent |

## 3. Finding sheets and schedules
- **Script:** `python ${CLAUDE_SKILL_DIR}/scripts/find_schedules.py <pdf|folder> --sheets` prints one line per page: sheet type, sheet number and title read from the title block. `--element openings|walls|finishes|ceilings|floors|roofs` ranks schedule/legend candidates.
- Results on real sets `[VERIFIED 2026-11-24]`:
  - **KPwBI Part4:** all 26 door/window schedule pages (A-8101..8126, p3–28) ranked above everything else; keyplans p1–2 excluded. Titles are mixed language: `SCHEDULE PINTU 01`, `SCHEDULE JENDELA 08`. Table headers are text (`LOCATION FRAME LEAF / PANEL HARDWARE REMARKS FIGURE TYPE`) but **sizes and codes inside the tables are outlined**: read them visually.
  - **KPwBI Part1–4 `--sheets`:** titles read correctly from the title block (`TIPE DINDING, BANGUNAN UTAMA - DENAH LANTAI 1`, `Denah Bongkaran Plafon Lt. Dasar`). One title is misspelt on the drawing (`Bongkraran`); the demolition pattern now catches it. Wall types p11–17, finishes p55–60 and ceiling plans p18–20 of Part2 found by `--element`.
  - **RSUD Cakung ARSITEKTUR** (79 single-page PDFs): titles are outlined; only dimension numbers and some sheet numbers (`AR.1301`) are text; 39 pages have no text at all. Use the file names (`AR 3100.pdf`) and look visually.
  - **Hunver OIKN 390B** architectural album (34 p): no text on any page. Visual only.
- The script is a shortlist, never the answer. Open the top pages (render 200–300 dpi) and confirm. If nothing is found, read the drawing index (`DAFTAR GAMBAR`) visually or **ask the user to point to the sheet**.
- **Rotated pages** (KPwBI Part3 standard details carry `/Rotate 270`): a PyMuPDF `clip` rectangle taken from the displayed page lands in the wrong place. Render the whole page once and crop the image `[VERIFIED 2026-11-25, samples]`.
- Text *inside* drawings is often split into glyphs: `pdftotext -bbox` (or PyMuPDF `get_text("words")`) and pair a code word ("AW", "D", "P") with the nearest number to locate tags `[IMPORTED KPwBI-ARS]`. On the KPwBI keyplans each tag is a letter line with a number line just below it (bboxes overlap by ~1.5 pt): pairing letter → number with |dx| < 4 pt and −3 < dy < 5 pt, deduplicated by position, gave per-code counts for 11 of 12 keyplan sheets `[VERIFIED 2026-11-25, samples]`.
- Build a page map per PDF once and keep it in the project log.

## 4. Calibration and measuring
- **Never one global scale.** Read the vector grid lines and map **piecewise grid to grid, per sheet, per axis**; verify on every grid line before measuring. A 0.04 % scale error plus a 1 pt origin error shifted a roof by 112 mm `[IMPORTED KPwBI-ARS]`. `scripts/pdf_calibrate.py` does this (needs `pdfplumber`, **not installed on this machine** `[VERIFIED 2026-11-24]`; script copied from the STR skill, not yet run here `[IMPORTED STR]`).
- **Check the calibration on a known element** (a column or a dimensioned wall). Bubble-derived calibration was off x +11 / y −118 mm on one KPwBI building, found by checking columns `[IMPORTED KPwBI-ARS]`.
- Cross-check scale with section level lines (e.g. 5500 floor to floor) and printed dimensions.
- Sheets of the same set can be shifted against each other: calibrate every sheet on its own grid `[IMPORTED STR]`.
- Raster measuring: mm/px = 25.4 / dpi × scale (1:50 at 300 dpi = 4.23 mm/px; 1:100 at 250 dpi = 10.16; 1:400 at 600 dpi = 16.9) `[IMPORTED KPwBI-ARS]`.
- Some keyplan pages use nested transforms where vector coordinates were unreliable: render crops with mm rulers drawn on them and read positions visually `[IMPORTED KPwBI-ARS]`.
- Vector fill paths (not raster tracing) give exact zone outlines; merge tiled fills by cancelling shared edges `[IMPORTED KPwBI-ARS]`.

## 5. Interpretation rules
- **Identity from shape or hatch alone is an interpretation**: say so, ask when it changes the build. A long hipped rectangle with blue hatch was modelled as a skylight; it was not `[IMPORTED KPwBI-ARS]`.
- **Study an element's nature before modelling:** plan + elevation + section + 1:50 detail + render. A facade read as projecting surrounds was really recessed niches `[IMPORTED KPwBI-ARS]`.
- **Apply user corrections exactly** and record them (a band height corrected by the user to +5.90..+7.22) `[IMPORTED KPwBI-ARS]`.
- **Elevation overlay check** for opening positions: render the elevation at known dpi, derive px ↔ mm from two grid lines, draw ticks at the placed positions, compare `[IMPORTED KPwBI-ARS]`.
- Codes in the drawing but not in the schedule are still modelled, flagged LOW `[IMPORTED KPwBI-ARS]`.
- When the user points at something: re-read that exact area at high dpi before answering `[IMPORTED STR]`.

## Failure cases
See `troubleshooting.md` (rows tagged drawings).

## Related
`project-setup.md` (levels, grids), element files §A1/§B1, `workflows/drawing-analysis-workflow.md`.
