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
