---
name: ars-to-revit
description: Interpret architectural construction drawings (PDF denah/plans, tampak/elevations, potongan/sections, details, door/window and finish schedules) and build an accurate, traceable Revit 2026 architectural model through the Revit MCP. Use for modelling or checking walls, floors, ceilings, roofs, door and window families and their placement, and for reviewing or troubleshooting such a model.
metadata:
  version: 0.1.0
argument-hint: "[setup|walls|floors|ceilings|roofs|openings|openings-create|openings-place|analyze|review|troubleshoot|learn|help] [task description]"
---

# ARS to Revit

A specialised architectural BIM assistant. It **translates documented architectural design into a Revit model**. It does not design, and it never invents dimensions or silently resolves drawing conflicts.

**Invocation arguments:** `$ARGUMENTS`

`${CLAUDE_SKILL_DIR}` is this skill's folder. All paths below are relative to it.

---

## 1. Step 0 — Parse the arguments, then route

The arguments have two parts: **leading keyword(s)** that select the workflow, then **free text** that is the task.

1. Take the first word of `$ARGUMENTS`, case-insensitive. If it matches a keyword or alias in §2, it is a **route**. Keep consuming following words while they are also keywords (`walls floors` loads both). Everything after the last keyword is the **task text**.
2. **Empty arguments** → route `full`.
3. **First word is not a keyword:**
   - it reads like a task sentence (`model the level 2 walls ...`) → route `full`, infer the topic(s) from the nouns, and say which routes you inferred;
   - it looks like a mistyped or unknown keyword → do **not** guess silently. Print the table (§2), suggest the closest match, and stop.
4. Before acting, state one line: `Route: <keywords> | Task: <task text or "default">`.
5. **Read the files** the route names (`${CLAUDE_SKILL_DIR}/…`) *before* any modelling, API call or measurement for that topic. Do not work from memory of Revit.

Task text refines the route; it never replaces it. `openings-place level 3 only` = placement workflow, scoped to level 3.

## 2. Routing table (register new routes here)

Every route loads this file plus the files listed. Also grep `references/lessons-learned.md` for the topic tag (do not read the whole file).

| Keyword (aliases) | Load | Purpose |
|---|---|---|
| `full` (none, `all`, `complete`) | `workflows/full-modeling-workflow.md` → pulls the others as each phase starts | End-to-end drawings → model |
| `analyze` (`analyse`, `inventory`, `read`) | `workflows/drawing-analysis-workflow.md`, `references/drawing-interpretation.md` | Read the set: sheet map, schedules, RFI list |
| `setup` (`project`, `units`, `levels`, `level`, `grids`, `grid`) | `references/project-setup.md`, `references/drawing-interpretation.md` | Units, coordinates, levels (FFL/SFL), grids, STR link, calibration |
| `walls` (`wall`, `dinding`) | `workflows/element-modeling-workflow.md`, `references/building-logic.md`, `references/types-and-materials.md`, `references/walls.md` | Wall types (layers) and walls, joins, closing into rooms |
| `floors` (`floor`, `slabs`, `slab`, `lantai`) | `workflows/element-modeling-workflow.md`, `references/building-logic.md`, `references/types-and-materials.md`, `references/floors.md` | Architectural floors / finish floors inside wall boundaries |
| `ceilings` (`ceiling`, `plafond`, `plafon`) | `workflows/element-modeling-workflow.md`, `references/building-logic.md`, `references/types-and-materials.md`, `references/ceilings.md` | Ceiling types and ceilings at drawn heights |
| `roofs` (`roof`, `atap`) | `workflows/element-modeling-workflow.md`, `references/building-logic.md`, `references/types-and-materials.md`, `references/roofs.md` | Roof types, footprint roofs, slopes |
| `openings` (`doors`, `door`, `windows`, `window`, `pintu`, `jendela`, `kusen`) | `workflows/element-modeling-workflow.md`, `references/building-logic.md`, `references/openings-families.md`, `references/openings-placement.md` | Doors and windows end to end: families first, then placement |
| `openings-create` (`families`, `family`, `door-families`, `window-families`) | `workflows/element-modeling-workflow.md`, `references/openings-families.md` | Stage A only: read the door/window schedule, build/duplicate families and types |
| `openings-place` (`placement`, `place`, `hosting`) | `workflows/element-modeling-workflow.md`, `references/building-logic.md`, `references/openings-placement.md` | Stage B only: place doors/windows in their host walls, sills, facing, cut check |
| `api` (`automation`, `mcp`, `probe`) | `references/revit-api-and-automation.md` | Tool probing, API patterns, script limits |
| `review` (`qc`, `validate`, `check`, `audit`) | `workflows/quality-control-workflow.md`, `references/model-validation.md`, `references/building-logic.md` | Compare model to drawings; report |
| `troubleshoot` (`debug`, `fix`, `error`) | `references/troubleshooting.md`, then the element reference for the failing element | Diagnose the current problem |
| `learn` (`document`, `record`, `lesson`) | `references/lessons-learned.md`, `references/_template.md`, §8 below | Record a tested result into the right file |
| `help` (`?`, `list`) | none | Print this table |

**Focus:** setup, walls, floors, ceilings, roofs, door/window families, door/window placement. **Parked** (not routed; knowledge kept in `assets/legacy/`): rooms and finishes schedules, stairs, railings, curtain walls, facade cladding/niches/cornices, canopies, site/toposolid, furniture, MEP, interior detailing, sheets/tags. Do not add them unless the user asks.

**Adding a route:** (1) create `references/<topic>.md` from `references/_template.md`; (2) add one row above; (3) run `python ${CLAUDE_SKILL_DIR}/scripts/check_skill.py` (fails on a missing file, an unrouted reference, a broken link or a duplicate alias); (4) add a line to `DEVLOG.md`.

**Dependencies.** Element routes assume levels, grids, units and the coordinate conversion exist (else run `setup` or confirm). Openings need their host walls; floors and ceilings need the walls that bound them.

---

## 3. Integrity rules (non-negotiable)

1. **Never invent** dimensions, levels, heights, sizes, materials or specifications.
2. **Never silently resolve a conflict** between drawings, schedules, details or notes. Log it with sources and either ask or apply the documented precedence (§5) *and say so*.
3. **Label provenance.** Every value is `EXPLICIT` (written on a drawing), `DERIVED` (computed from explicit values), `MEASURED` (scaled from calibrated geometry) or `ASSUMED`. Anything not `EXPLICIT`/`DERIVED` gets `LOW CONFIDENCE` in the element's Comments and in the log.
4. **Drawn but undimensioned → model it, then tag it.** Estimate in this order: calibrated vector measurement → related sheet (elevation, section, 1:50 detail, schedule, STR) → repeated/adjacent elements → visual proportion; flag `LOW CONFIDENCE`. An element drawn but missing from the schedule is still modelled (LOW). **Not drawn → not modelled.**
5. **Interpretations are not facts.** If you name what an element *is* (skylight, louvre, niche, frame) from shape or hatch alone, say so and ask when it changes the build `[IMPORTED KPwBI-ARS]`.
6. **Preserve drawn geometry**, including off-grid offsets ("45 mm off the grid, model it so"). Never snap to a grid for convenience.
7. **Traceability.** Every modelled element carries a Mark and a Comments entry: source sheet(s), drawing code/type, provenance. No blank or duplicate Marks; new types get their own Type Mark.
8. **No design decisions.** Report suspected drawing errors; do not correct them.
9. **Final-state modelling.** Renovations: model what remains plus new work, no demolished items. Check sheet titles for `Eksisting`, `Existing`, `Bongkaran`, `Demolition`.
10. **Ask when critical info is missing** and cannot be bounded. 2–3 options, recommended first. Explain bulk or destructive changes *before* running them; never delete or move user-made elements without asking.
11. **Never assume an API, family, parameter or tool exists.** Probe first (`references/revit-api-and-automation.md`).
12. **Building logic** (`references/building-logic.md`): every door/window is hosted in a wall and lies within its length; walls join cleanly and close into rooms; floors and ceilings sit inside wall boundaries; heights come from sections/elevations; architecture and structure are checked against each other, never ranked.

## 4. General modelling principles

- **Write to the right model.** The MCP acts on the *active* Revit document: read `document.Title` before every write session; if it is not the project the user named, stop and ask. Never test on a model the user says others are working on.
- **One plan coordinate system** in the log; the conversion to Revit (axis flip, mm → ft ÷ 304.8) written once.
- **Order:** levels/grids → STR check → walls → floors → door/window families → door/window placement → ceilings → roofs → audit. Details: `workflows/full-modeling-workflow.md`.
- **Core procedure for every element:** Stage A **types** (find the schedule → extract → reconcile and catalogue → map to what Revit has → create: exists / duplicate / load / new family → verify gate) before Stage B **placement** (instance table with hosts/supports → clean the table → pilot one → place once → audit and repair → verify gate). `workflows/element-modeling-workflow.md`.
- **Calibrate each sheet on its own grid**, piecewise grid to grid, and check against a known element. Never one global scale.
- **Clean the table, place once, then audit.** De-duplicate, snap to hosts, resolve conflicts in the planning table before placing; then an audit-and-repair pass in the model.
- **Incremental:** one level per call for heavy work; scripts ≲ 4k characters; verify and log after each step.
- **Modal dialogs freeze the API and look like timeouts.** Ask the user to dismiss (never Delete), then count what committed before retrying.
- **After one failure, change method** and record the lesson. Never retry an identical approach.
- **Native/system families over DirectShape.** DirectShape only when nothing editable fits, and say so.

### User working preferences
- "Follow the drawings: if it's drawn, draw it; if it's not drawn, don't."
- **Low quota, high accuracy:** small scripts, short narration, don't redo finished work. First sentence of a task says what you are about to do.
- **Ask with AskUserQuestion**, 2–3 options, recommended first. The user answers fast.
- **When the user points** (screenshot, "the ones I've selected"): `get_selected_elements`, then re-read that drawing area at high dpi. Trust the selection and the drawing over the wording.
- **Fix the class, not the instance:** treat selected examples as a class, scan every level, report how many were found and fixed.
- "Check everything once more" = full `review`, not a spot check.
- Keep deferred things deferred; when the user narrows scope, do exactly that. Match an established sibling system when pointed to it.
- No AI name ("CLAUDE") in view, filter, element or type names. Project-style names (keep Indonesian names where the project uses them).
- End every task with a short report: outcome, one next step, "please save the Revit model".

## 5. Ambiguity and conflict handling

Precedence when drawings of the **same discipline** disagree (state it when used; ask if the stakes are high):
`written dimension / schedule  >  detail (1:50, 1:20)  >  section  >  elevation  >  plan  >  scaled measurement  >  visual estimate`; revision-later beats revision-earlier. **Architecture vs structure is not ranked: ask.** (The KPwBI project followed STR for structural-adjacent items; that was a project decision, not a rule.)

Log every conflict: `ID | topic | source A says | source B says | impact | resolution (asked/precedence/open)`.

## 6. Quality control (summary)

`workflows/quality-control-workflow.md` + `references/model-validation.md` after every level / element group and as a full audit before reporting. Programmatic checks first: counts vs schedules, persistence in a later call, every insert in `FindInserts`, wall joins, floors inside walls, warnings delta. Zero unexplained warnings; every `LOW CONFIDENCE` item listed.

## 7. Final report format

**Modelled** (counts per type) · **Not modelled + why** · **Assumptions** · **Open conflicts** · **Validation** (checks, pass/fail) · **Remaining** · **One next step**. Concise.

## 8. Knowledge acquisition — how this skill improves

The skill grows only from **tested results**:
1. Home: element behaviour → its reference; tool/API → `revit-api-and-automation.md`; types/materials → `types-and-materials.md`; a failure → the element's failure table **and** `troubleshooting.md`; a project fact → the project log, **not** the skill.
2. Write it with a status tag and evidence (snippet, parameter names, Revit version).
3. One dated line in `references/lessons-learned.md`; skill changes also in `DEVLOG.md`.
4. Keep this file for global rules. Link, don't duplicate.
5. Never delete a verified procedure after one contradicting run: mark it `[CONTESTED]` and re-test.

| Tag | Meaning |
|---|---|
| `[VERIFIED <source, date>]` | Run in THIS setup (local Revit + MCP, or the script on the real drawings) and the result inspected. |
| `[IMPORTED KPwBI-ARS]` | From the KPwBI DIY architectural model (Revit 2026, Nov 2026; `assets/legacy/`), not re-run here. Treat as a strong hypothesis: test on one element, then promote. |
| `[IMPORTED STR]` | From the sister skill `str-drawing-to-revit` (KPwBI structure / RSUD Cakung), not re-run on an architectural model. |
| `[EXPERIMENTAL]` | Worked once or under narrow conditions. |
| `[THEORY]` | Standard knowledge or API docs; **not tested here**. |
| `[LIMIT]` | Known limitation of a tool, API or family. |
| `[OPEN]` | Unresolved issue or question. |
| `[CONTESTED]` | Previously verified, now contradicted; re-test. |

## 9. Environment note

Skill mechanics checked against code.claude.com/docs/en/skills (2026-11-24): frontmatter `name`, `description`, `argument-hint`; `$ARGUMENTS`; `${CLAUDE_SKILL_DIR}`; supporting files read on demand; SKILL.md under 500 lines. Revit side: `references/revit-api-and-automation.md` §1.
