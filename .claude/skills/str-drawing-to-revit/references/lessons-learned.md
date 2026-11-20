# Lessons learned — dated index

> Append-only. One line per tested lesson: `date | topic tag | status | summary | pointer`. Detail lives in the pointed-to file. Grep by tag: `grep "#beams" lessons-learned.md`.

## 2026-11-20 — imported from legacy skill `structural-drawings-to-revit` (KPwBI DIY Gedung Utama, Revit 2026)
- #beams [VERIFIED KPwBI] Y_JUSTIFICATION=1 required (492 beams were (b−200)/2 off) → beams.md §8
- #beams [VERIFIED KPwBI] DisallowJoinAtEnd at non-column ends; merge collinear (602→492) → beams.md §5
- #calibration [VERIFIED KPwBI] piecewise grid calibration; global scale caused 112 mm shift → grids-and-levels.md §5
- #api [VERIFIED KPwBI] ≲4k-char scripts; Chinese error strings; int[]/local-function compile failures → revit-api-and-automation.md §4
- #slabs [VERIFIED KPwBI] overlapping floor rebuild raises modal dialog that looks like a timeout → slabs.md §5
- #drawings [VERIFIED KPwBI] end-on section label misread (30 posts, beams 950 mm high) → drawing-interpretation.md §5
- #foundations [VERIFIED KPwBI] DirectShape convention; group split cap/pile; orphan caps from demolished frame → foundations.md
- #framing [VERIFIED KPwBI] no angle/CNP family → DirectShape extrusions → structural-framing.md §5
- #views [VERIFIED KPwBI] template-injected filters hide slabs → troubleshooting.md
- #preferences Model drawn-but-undimensioned (flag LOW CONFIDENCE); model drawn offsets exactly; families over DirectShape; no AI name in view names; ask with options + recommendation → SKILL.md §3

## 2026-11-20 — skill development
- #skill [VERIFIED container, Claude Code 2.1.329] `$ARGUMENTS`, `$N`, `${CLAUDE_SKILL_DIR}`, frontmatter `argument-hint` exist in the installed binary → SKILL.md §9
- #env [OPEN] No Revit in the cloud container; Revit-side `[THEORY]` items await live tests → assets/examples/live-test-plan.md
