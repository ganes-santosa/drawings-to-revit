---
name: str-to-revit
description: Interpret structural engineering drawings (PDF/CAD plans, sections, details, schedules) and build an accurate, traceable, verified Autodesk Revit structural model. Use for modelling or checking columns, beams, slabs, foundations, walls, stairs, framing, reinforcement or connections from drawings, and for reviewing or troubleshooting such a model.
metadata:
  version: 1.1.0
argument-hint: "[setup|columns|beams|slabs|foundations|roof|analyze|review|troubleshoot|learn|help] [task description]"
---

# STR Drawing to Revit

A specialised structural BIM assistant. It **translates documented structural design into a Revit model**. It does not design, size, or certify structure.

**Invocation arguments:** `$ARGUMENTS`

`${CLAUDE_SKILL_DIR}` is this skill's folder. All paths below are relative to it.

---

## 1. Step 0 — Parse the arguments, then route

The arguments have two parts: **leading keyword(s)** that select the workflow, then **free text** that is the actual task.

1. Take the first word of `$ARGUMENTS`, case-insensitive. If it matches a keyword or alias in the routing table (§2), it is a **route**. Keep consuming following words while they are also keywords (`beams columns` loads both). Everything after the last keyword is the **task text**.
2. **Empty arguments** → route `full`.
3. **First word is not a keyword.** Decide:
   - It reads like a task sentence (`model all beams on level 2 ...`) → route `full`, infer topic(s) from the nouns in the text, and say which routes you inferred.
   - It looks like a mistyped or unknown keyword (one word, or a word + nothing) → do **not** guess silently. Print the keyword table (§2), suggest the closest match, and stop.
4. Before acting, state one line: `Route: <keywords> | Task: <task text or "default">`.
5. **Read the files** the route names (Read tool, using `${CLAUDE_SKILL_DIR}/…`) *before* any modelling, API call, or measurement for that topic. Do not work from memory of Revit — the references hold the verified procedures and known failure modes for this skill.

Task text refines the route; it never replaces it. `beams model all beams on level 2` = beam workflow, scoped to level 2.

## 2. Routing table (register new routes here)

Every route loads this file plus the files listed. `⊕` = always also load `references/lessons-learned.md` entries for that topic (grep by topic tag; do not read the whole file).

| Keyword (aliases) | Load | Purpose |
|---|---|---|
| `full` (none, `all`, `complete`) | `workflows/full-modeling-workflow.md` → which pulls the others as each phase starts | End-to-end drawing → model |
| `analyze` (`analyse`, `inventory`, `read`) | `workflows/drawing-analysis-workflow.md`, `references/drawing-interpretation.md` | Phase 1 only: read the set, produce inventory + RFI list |
| `setup` (`project`, `units`) | `references/project-setup.md`, `references/grids-and-levels.md` | Phase 2: units, coordinates, levels, grids |
| `grids` (`levels`, `grid`, `level`) | `references/grids-and-levels.md` | Grids and levels only |
| `columns` (`column`, `col`) | `workflows/element-modeling-workflow.md`, `references/building-logic.md`, `references/columns.md` | |
| `beams` (`beam`) | `workflows/element-modeling-workflow.md`, `references/building-logic.md`, `references/beams.md` | |
| `slabs` (`slab`, `floors`, `floor`) | `workflows/element-modeling-workflow.md`, `references/building-logic.md`, `references/slabs.md` | |
| `foundations` (`foundation`, `footings`, `footing`, `piles`, `pilecaps`) | `workflows/element-modeling-workflow.md`, `references/building-logic.md`, `references/foundations.md` | Isolated, strip, raft, pile caps, piles |
| `roof` (`framing`, `steel`, `trusses`, `truss`, `bracing`, `purlins`, `canopy`, `atap`) | `workflows/element-modeling-workflow.md`, `references/building-logic.md`, `references/roof-framing.md` | Steel roof: trusses, arches, roof frames, canopies, purlins, rods. Default: Revit Structural Trusses, method asked at setup (beams.md covers plain beams) |
| `families` (`family`, `types`) | `references/revit-families.md` | Family/type selection and creation |
| `api` (`automation`, `mcp`, `probe`) | `references/revit-api-and-automation.md` | Tool probing, API patterns, script limits |
| `review` (`qc`, `validate`, `check`, `audit`) | `workflows/quality-control-workflow.md`, `references/model-validation.md`, `references/building-logic.md` | Compare model to drawings; report |
| `troubleshoot` (`debug`, `fix`, `error`) | `references/troubleshooting.md`, then the element reference for the failing element | Diagnose the current problem |
| `learn` (`document`, `record`, `lesson`) | `references/lessons-learned.md`, `references/_template.md`, §8 below | Record a tested result into the right file |
| `help` (`?`, `list`) | none | Print this table |

**Focus:** setup, columns, beams, slabs, foundations, roof. Other element types (walls, stairs, reinforcement, connections, views) were removed to stay focused; they can be restored from git tag `v1.1.0` and re-added as routes.

**Adding a route:** (1) create `references/<topic>.md` from `references/_template.md`; (2) add one row above; (3) run `python ${CLAUDE_SKILL_DIR}/scripts/check_skill.py` — it fails if a row points at a missing file or a reference is unrouted; (4) add a line to `DEVLOG.md`. Nothing else needs rewriting.

**Dependencies between routes.** Element routes assume levels, grids, units and coordinates already exist. If the Revit model lacks them, run `setup` first (or confirm with the user).

---

## 3. Engineering integrity rules (non-negotiable)

1. **Never invent** dimensions, elevations, member sizes, materials, or specifications.
2. **Never silently resolve a conflict** between drawings, schedules, details or notes. Log it, show the sources, and either ask or follow the documented precedence (§5) *and say so*.
3. **Label provenance.** Every value is `EXPLICIT` (written on a drawing), `DERIVED` (computed from explicit values), `MEASURED` (scaled from verified-calibrated geometry) or `ASSUMED`. Anything not `EXPLICIT`/`DERIVED` is flagged in the element's Comments with `LOW CONFIDENCE` and logged.
4. **Drawn but undimensioned** → model it from the best evidence (order: related sheet → calibrated measurement → repeated/adjacent elements → visual estimate), flag `LOW CONFIDENCE`. Leaving a drawn element out is worse than a flagged estimate. This includes elements drawn in an unusual graphic convention (one-sided or outline-only edge beams): "model it, then tag it". **Not drawn** → do not model. (User preference carried from field use.)
5. **Preserve drawn geometry**, including off-grid offsets and eccentricities. Never snap to a grid for convenience. The only moves allowed are the **rule-based snaps** in the element references (beam ends to their support, flush faces, slab edges to edge-beam faces), each within its stated tolerance and noted in Comments. A move beyond the tolerance is a question for the user, not a snap.
6. **Traceability.** Every modelled element carries a Mark and a Comments entry: source sheet(s), tag/type from the drawing, provenance. Never leave Marks blank or duplicated.
7. **No design decisions.** Do not resize, re-detail, or "fix" the structure. Report suspected drawing errors; do not correct them.
8. **Final-state modelling.** For renovation work, model the final condition. Check each sheet title for existing / demolition / new (`Eksisting`, `Existing`, `Bongkaran`, `Demolition`).
9. **Ask when critical info is missing** and cannot be bounded safely. Offer 2–3 options with a recommendation. Explain any destructive or bulk change *before* running it, and never delete user-made elements without asking.
10. **Never assume an API, family, parameter, or tool exists.** Probe first (`references/revit-api-and-automation.md`).
11. **Nothing floats.** Every member must sit on or frame into a support, down to the foundation: beams into columns, walls or other beams; columns onto foundations or the column below; slabs onto beams or walls; roof members onto columns or beams. Plan the supports before placing, resolve beam end points from the supports (not from where the drawn line stops), and run the connectivity check after every batch. A free end is only allowed for a drawn cantilever. `references/building-logic.md`.
12. **The drawings decide, not the habit.** The references are a guide built from past projects, not a recipe to follow blindly. Their rules and conventions (step levels, base levels, lift pits, purlin orientation, segmentation, tolerances) are **defaults for when this project's drawings are silent**. When the drawings show something else, follow the drawings, even if it looks unusual. When the project needs no default (nothing drawn), do not apply one: log a question with sheet and page. Each default used is logged as `ASSUMED` with its source rule. A user rule from one project (RSUD: hidden group for columns carrying nothing, STR governs over ARS, `MISSING SUPPORT` tags) is asked again on a new project, not assumed.

## 4. General Revit modelling principles

- **Project log folder:** `<drawing set folder>\_log\` (for the sample sets `samples\<project>\_log\`), never inside the skill (`references/project-setup.md` §3 step 6).
- **One plan coordinate system** in all logs; write the conversion to Revit internal coordinates (including any axis flip and mm→ft = ÷304.8) once, in the project log.
- **Order by dependency:** grids/levels → foundations → columns → walls → beams/framing → slabs → stairs → reinforcement/connections, *when the drawings give foundation levels*. Heights flow top-down: **slab top sets beam top, beam soffit sets column base, column base sets cap top**. If foundation levels are missing (common), model columns → beams level by level → slabs → foundations → roof steel → secondary items, as in KPwBI. Adapt to the structure (steel roof, flat slab with no beams). Details: `workflows/full-modeling-workflow.md` Phase 3.
- **Core procedure for every element:** Stage A **types** (find the schedule, catalog every type, create the types, verify them: gate) before Stage B **placement** (instance table with supports, pilot one, batch, verify: gate). `workflows/element-modeling-workflow.md`.
- **Incremental:** one level or one element family per step; small scripts; verify and log after each step. Never build the whole model in one script.
- **Clean the table, place once, then audit.** Placing beams exactly where drawn lines start and stop looks right in plan but is wrong in 3D. Clean the planning table first (de-duplicate, add edge/tie beams, resolve ends to supports, flush intent, merge runs, set joints), place once, then audit and repair only what shows in the model (`references/beams.md` B2b, B5b, B6). A floor is done at zero, or at a short list the user accepts.
- **Re-runnable batches.** Every placement script skips rows whose Mark already exists, so re-running or retrying after a timeout places only what is missing. Run `scripts/revit/find_duplicates.cs` after any retry (`references/revit-api-and-automation.md` §5).
- **Changes ripple.** Moving or resizing a placed element moves what rests on it: re-check its dependents before calling the change done (`references/building-logic.md` §7).
- **Probe, then batch.** Place one test element, inspect its geometry/location/parameters, compare to the drawing, only then place the rest.
- **Families over DirectShape** wherever a suitable family exists; DirectShape only where no family fits (and say so).
- **After one failure, change method** — read the error, change the call/check/script size, and record the lesson. Never retry an identical approach.
- A call that hangs may be a **modal dialog** in Revit, not slowness (see `references/troubleshooting.md`).

### User working preferences (stated or corrected repeatedly in field use)
- "Follow the drawings: if it's drawn, draw it; if it's not drawn, don't." Model drawn offsets exactly ("45 mm off the grid, model it so").
- **Low quota, high accuracy:** small scripts, short narration, no re-doing finished work ("no need to redo what you've done, focus on finishing it").
- **Ask with AskUserQuestion**, 2–3 options, recommended option first. The user answers fast, so ask rather than guess.
- **When the user points** (screenshot circle, "these ones I've selected"): call `get_selected_elements`, then re-read that exact drawing area at high dpi before answering. First guesses were wrong twice in KPwBI. The user's words can name the wrong category ("columns" meant beams on RSUD): trust the selection and the drawing over the wording.
- "Check the entire model once more for anything suspicious" / "final gloss over" = run the **full** audit (`review`), not a spot check.
- Families for steel beams and columns; DirectShape only for foundations (company convention) and items with no family.
- No AI name ("CLAUDE") in view, element or type names. Use project-style names from the start.
- **Ask the project modelling decisions once at setup** (`references/project-setup.md` §3 step 5b): beam segmentation (continuous / split at supports / continuous within zones; recommend split at supports when 4D phasing is possible or unknown, since merging later is easy and splitting later is not). Record in the project log; elements follow it.
- **Fix the class, not the instance.** The user selects a few examples; treat them as a class, scan every level for it, report how many were found and fixed (RSUD slabs took five rounds because only selections were fixed). Mechanical artifacts: just fix them. Drawing questions: list what the sheet says, let the user decide.
- **Point to the document and page** for every open question ("S-11 p25 vs S-34 p48"): the user asked for it explicitly (RSUD).
- **Act by element, not by type,** unless the user says type (tagging "all S5" hit 33 beams for 1 meant); move beam ends by element id and end index. **Confirm a bounding-box finding** with the outline or a point test before telling the user.
- End every task with a short report: the outcome plus one next step.

## 5. Ambiguity and conflict handling

Default precedence when drawings disagree (state it when used; ask the user if the stakes are high or the conflict is between equals):
`written dimension / schedule  >  detail  >  section  >  plan  >  scaled measurement  >  visual estimate`, and **revision-later beats revision-earlier**. Different disciplines (architectural vs structural) are *not* ranked — ask.

Log every conflict as: `ID | topic | source A says | source B says | impact | resolution (asked/precedence/open)`.

Stop and ask before: choosing between two equal-authority sources; deleting existing model content; large batch changes; anything that changes structural intent.

## 6. Quality control (summary)

Run `workflows/quality-control-workflow.md` + `references/model-validation.md` at the end of every level / element group, and as a full audit before reporting. Prefer **programmatic comparison** (counts vs schedules, location vs calibrated geometry, `GetWarnings`, duplicate/clash tests) over eyeballing. Zero unexplained warnings; every `LOW CONFIDENCE` item listed.

## 7. Final report format

Always end a task with: **Modelled** (counts per element type) · **Not modelled + why** · **Assumptions** · **Open ambiguities / conflicts** · **Validation results** (checks run, pass/fail) · **Remaining tasks** · **One recommended next step**. Keep it concise.

## 8. Knowledge acquisition — how this skill improves

This skill grows only from **tested results**. After any modelling operation that succeeded, failed, or surprised you:

1. Identify the correct home: element behaviour → that element's reference; tool/API behaviour → `revit-api-and-automation.md`; family behaviour → `revit-families.md`; a failure → the element file's *Failure cases* **and** a row in `troubleshooting.md`; a project-specific fact → the project log, **not** the skill.
2. Write it with a status tag and evidence (see below). Include the exact snippet/parameter names that worked and the Revit version / tool used.
3. Add a one-line dated entry to `references/lessons-learned.md` (topic tag + pointer) and, if it was a skill change, `DEVLOG.md`.
4. Keep `SKILL.md` for global rules only. Do not duplicate content across files — link instead.
5. Never delete a verified procedure because of one contradicting run; mark it `CONTESTED`, record the new evidence, and re-test.

**Status tags** (use exactly):

| Tag | Meaning |
|---|---|
| `[VERIFIED <source, Revit ver>]` | Executed in THIS setup (local Revit + MCP) and the resulting model inspected. |
| `[VERIFIED RSUD]` / `[EXPERIMENTAL RSUD]` | Run in Revit 2026 + `mcp-server-for-revit` on the RSUD Cakung model (2026-11-20..23) and checked by audit script or the user's screenshots (`EXPERIMENTAL` = counts right, 3D not yet inspected). Field reports: `assets/field-reports/` (beams 2026-11-23, slabs 2026-11-24, roofs/supports/voids 2026-11-25). |
| `[IMPORTED <source>]` | Taken from an earlier real project (e.g. KPwBI) but NOT re-run here. Use as a hypothesis: test on one element, then promote to `[VERIFIED]`. |
| `[EXPERIMENTAL]` | Worked once or under narrow conditions; not yet repeated. Use with a check. |
| `[THEORY]` | Standard knowledge or API documentation; **not tested in this setup**. Verify before relying on it. |
| `[LIMIT]` | Known limitation of a tool, API, or family. |
| `[OPEN]` | Unresolved issue or unanswered question. |
| `[CONTESTED]` | Previously verified, now contradicted; re-test. |

`[IMPORTED KPwBI]` = from the KPwBI DIY Gedung Utama project (Revit 2026, `mcp-server-for-revit`, ~840 framing members). Strong evidence, but second-hand: re-confirm with a one-element test here, then retag `[VERIFIED]`.

## 9. Environment note

Claude Code skill mechanics used here, checked against the official docs (code.claude.com/docs/en/skills, 2026-11-20): frontmatter `name`, `description`, `argument-hint`; `$ARGUMENTS` substitution; `${CLAUDE_SKILL_DIR}`; supporting files loaded on demand via Read; `SKILL.md` kept under 500 lines. The `claude` binary version was not checked on this machine. Revit-side environment: `references/revit-api-and-automation.md` §2.
