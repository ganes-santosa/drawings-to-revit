# Lessons learned — dated index

> Append-only. One line per lesson: `#topic [status] summary → pointer`. Detail lives in the pointed-to file. Grep by tag: `grep "#openings" lessons-learned.md`.

## 2026-11-24 — imported from the legacy skill `architectural-drawings-to-revit` (KPwBI DIY, Revit 2026)
- #openings [IMPORTED KPwBI-ARS] Every window family needs an Opening cut; reopen and count → openings-families.md A5
- #openings [IMPORTED KPwBI-ARS] Wide windows (> ~4 m): extend the template host wall before sizing → openings-families.md A5
- #openings [IMPORTED KPwBI-ARS] Never load and place in one call; flip only after Regenerate → openings-placement.md B5
- #openings [OPEN] Doors vanish at commit on 100 mm Generic walls → openings-placement.md B4
- #openings [IMPORTED KPwBI-ARS] Keyplan leaders can end at window glyphs: overlap check, list doubtful tags → openings-placement.md B2b
- #walls [IMPORTED KPwBI-ARS] Walls whole, inserts cut; merge collinear runs → building-logic.md §2, walls.md B2b
- #walls [IMPORTED KPwBI-ARS] Unjoin before deleting joined walls; snap to exact faces (no 1–4 mm overlaps) → walls.md B4–B5
- #floors [IMPORTED KPwBI-ARS] No temporary overlaps; floor edge at the wall face → floors.md B4–B5
- #roofs [IMPORTED KPwBI-ARS] Slopes by coordinates and rise/run; sketch plane = underside → roofs.md B4–B5
- #calibration [IMPORTED KPwBI-ARS] Piecewise per-sheet grid calibration; verify on a known element → drawing-interpretation.md §4
- #drawings [IMPORTED KPwBI-ARS] Identity from hatch/shape is an inference: say so, ask → SKILL.md §3.5
- #api [IMPORTED KPwBI-ARS] ≲ 4k-char typed scripts; verify persistence in a later call; check document.Title → revit-api-and-automation.md §4
- #preferences [IMPORTED KPwBI-ARS] Drawn → model (LOW if undimensioned); native families over DirectShape; no CLAUDE in names; keep deferred things deferred → SKILL.md §3–4

## 2026-11-24 — skill development
- #skill [VERIFIED docs 2026-11-24] `$ARGUMENTS`, `${CLAUDE_SKILL_DIR}`, `argument-hint`, SKILL.md < 500 lines (code.claude.com/docs/en/skills) → SKILL.md §9
- #api [VERIFIED 2026-11-24] `say_hello` timed out while its modal dialog waited: never use it as a connection test → revit-api-and-automation.md §1
- #env [VERIFIED 2026-11-24] Do not probe or test on a model other agents are working on (user rule) → project-setup.md §2
- #tools [VERIFIED 2026-11-24] find_schedules.py: all 26 KPwBI door/window schedule pages ranked first after adding the English title word "schedule" and table header words; sizes/codes inside are outlined → drawing-interpretation.md §3
- #tools [VERIFIED 2026-11-24] `--sheets` reads sheet number + title from the title block (KPwBI); RSUD titles outlined, Hunver no text at all → drawing-interpretation.md §3

## 2026-11-25 — first real catalog task (KPwBI drawings, no Revit)
- #walls [VERIFIED 2026-11-25, samples] Wall-type legend gives code + material name only; thickness comes from standard details (layers) and 1:50 partial plans (dimensions) → walls.md A1, A3
- #walls [VERIFIED 2026-11-25, samples] One legend code can have two thicknesses (B: 130 and 150): split the type; a code with no thickness anywhere (C) is blocked and asked → walls.md A3
- #walls [VERIFIED 2026-11-25, samples] Finish legends are text and differ per building; paint/accessory/plinth codes are not layers → walls.md A3
- #openings [VERIFIED 2026-11-25, samples] Schedule sizes = frame outside = wall opening ("Ukuran Opening"); one code (D51) writes H x W → openings-families.md A3
- #openings [VERIFIED 2026-11-25, samples] Elevation, plan and section chains disagree on 7 window codes and quantities are mostly blank: record both, RFI, count from keyplans → openings-families.md A3
- #openings [VERIFIED 2026-11-25, samples] Keyplan tags are real text: letter + number pairing by position gives per-code counts; schedule qty differed on 9 codes → drawing-interpretation.md §3
- #drawings [VERIFIED 2026-11-25, samples] Some pages are stored rotated (Part3 standard details, /Rotate 270): render the whole page and crop the image, not the PDF clip → drawing-interpretation.md §3

## 2026-11-25 — parametric window family pilot (Revit 2026, scratch model)
- #openings [VERIFIED 2026-11-25] Parametric family from Metric Window.rft: lock frame/mullion/glass faces to reference planes; flex test 5/5, placed and cut exactly → openings-families.md A5, A5b, scripts/revit/family_window_fixed_2pane.cs
- #openings [VERIFIED 2026-11-25] The template's Opening Cut already follows Width/Height: never add a second opening → openings-families.md A5
- #openings [VERIFIED 2026-11-25] NewFamilyInstance at level z gives sill 0: set INSTANCE_SILL_HEIGHT_PARAM after placing → openings-placement.md B4
- #api [VERIFIED 2026-11-25] Family documents can be created, edited, saved and loaded from send_code_to_revit (own Transaction) → revit-api-and-automation.md §4
- #env [VERIFIED 2026-11-25] Revit 2026 family templates are on D:\ProgramData\Autodesk\RVT 2026\Family Templates\English → openings-families.md A5

## 2026-11-25 — door/window edge cases from five sample sets (no Revit)
- #openings [VERIFIED 2026-11-25, samples] Edge cases: pane/leaf count by width, unequal panes, optional transoms/side lights/vision panels, swing-only code pairs, louvre infill, ganged units, sliding/folding/rolling doors, raised-sill door, curved corner glazing, storefronts → openings-families.md A5c
- #drawings [VERIFIED 2026-11-25, samples] Tower 4 and Bandara are scanned (no text, stamps over dimensions); Hunver has no schedule; DRC schedules are text; Bandara index number = PDF page → openings-families.md A5c

## 2026-11-25 — core door/window families (Revit 2026 scratch model)
- #openings [VERIFIED 2026-11-25] KPW_Window (1-6 columns, top/bottom lights): 40/40 locks, flex 8/8 incl. DRC W3; pane widths match the drawings → openings-families.md A5d, scripts/revit/family_window_core.cs
- #openings [VERIFIED 2026-11-25] KPW_Door (1/2 leaves, transom, vision, louvre): 47/47 locks, flex 8/8 → openings-families.md A5d, scripts/revit/family_door_core.cs
- #openings [VERIFIED 2026-11-25] Yes/No formulas drive IS_VISIBLE_PARAM; if() and unit literals ("100 mm") work in formulas; keep hidden parts geometrically valid (positive sizes) for every combination → A5d
- #openings [VERIFIED 2026-11-25] Coincident planes (leaf top = transom bar bottom): lock faces by plane NAME per element, not by position → scripts/revit/family_door_core.cs
- #openings-edge [user rule 2026-11-25] Unsupported door/window codes: improvise (right opening, sill, host, cut), mark IMPROVISED + LOW, log it → openings-families.md A5d
- #openings [VERIFIED 2026-11-25] Hidden parts must stay valid (cap with if()) and parked inside the unit (bbox); set flags off → sizes → flags on; test by committing → openings-families.md A5d
- #openings [VERIFIED 2026-11-25] Types created and instances placed in the same call stayed uncut; separate calls cut → openings-families.md A5d, openings-placement.md B5
- #api [VERIFIED 2026-11-25] Long sweeps over the bridge time out while Revit keeps working (looks like a hang); FailuresProcessing handler catches commit-time failures only → revit-api-and-automation.md §4
