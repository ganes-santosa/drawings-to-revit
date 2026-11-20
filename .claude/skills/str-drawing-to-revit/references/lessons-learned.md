# Lessons learned — dated index

> Append-only. One line per tested lesson: `date | topic tag | status | summary | pointer`. Detail lives in the pointed-to file. Grep by tag: `grep "#beams" lessons-learned.md`.

## 2026-11-20 — imported from legacy skill `structural-drawings-to-revit` (KPwBI DIY Gedung Utama, Revit 2026)
- #beams [IMPORTED KPwBI] Y_JUSTIFICATION=1 required (492 beams were (b−200)/2 off) → beams.md §8
- #beams [IMPORTED KPwBI] DisallowJoinAtEnd at non-column ends; merge collinear (602→492) → beams.md §5
- #calibration [IMPORTED KPwBI] piecewise grid calibration; global scale caused 112 mm shift → grids-and-levels.md §5
- #api [IMPORTED KPwBI] ≲4k-char scripts; Chinese error strings; int[]/local-function compile failures → revit-api-and-automation.md §4
- #slabs [IMPORTED KPwBI] overlapping floor rebuild raises modal dialog that looks like a timeout → slabs.md §5
- #drawings [IMPORTED KPwBI] end-on section label misread (30 posts, beams 950 mm high) → drawing-interpretation.md §5
- #foundations [IMPORTED KPwBI] DirectShape convention; group split cap/pile; orphan caps from demolished frame → foundations.md
- #framing [IMPORTED KPwBI] no angle/CNP family → DirectShape extrusions → structural-framing.md §5
- #views [IMPORTED KPwBI] template-injected filters hide slabs → troubleshooting.md
- #preferences Model drawn-but-undimensioned (flag LOW CONFIDENCE); model drawn offsets exactly; families over DirectShape; no AI name in view names; ask with options + recommendation → SKILL.md §3

## 2026-11-20 — skill development
- #skill [VERIFIED docs 2026-11-20] `$ARGUMENTS`, `$N`, `${CLAUDE_SKILL_DIR}`, `argument-hint` documented at code.claude.com/docs/en/skills (binary version not checked locally) → SKILL.md §9
- #env [VERIFIED local 2026-11-20] Revit 2026 installed locally; MCP calls fail with `connect to revit client failed` until Revit + add-in are running → revit-api-and-automation.md
- #env [OPEN] Revit-side `[THEORY]`/`[IMPORTED]` items await live tests → assets/examples/live-test-plan.md
- #tags Imported KPwBI knowledge retagged `[IMPORTED KPwBI]` (was `[VERIFIED KPwBI]`); promote only after a local test → SKILL.md §8
- #skill [VERIFIED 2026-11-20] Legacy skill archived verbatim (assets/legacy/) and compared item by item; missing items integrated: user preferences (SKILL.md §4), height chain / build order (full workflow Phase 3), real KPwBI family/type/mark names (beams, revit-families, framing, slabs), views & filters (new views-and-documentation.md), DED sheet order + inference examples (drawing-interpretation), 7 troubleshooting rows → assets/legacy/README.md
